import unicodedata
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import (
    BaseModel,
    Field,
)
from sqlalchemy.orm import Session

from api.auth_dependencies import (
    get_current_user,
)
from api.dependencies import (
    get_db,
)
from api.services.langflow_client import (
    LangflowClientError,
    run_langflow,
)

from database.models.identity import (
    UserModel,
)
from database.repositories.parcel_membership_repository import (
    ParcelMembershipRepository,
)
from database.repositories.parcel_repository import (
    ParcelRepository,
)

from twin.identity import (
    SystemRole,
)


router = APIRouter(
    prefix="/api",
    tags=["chatbot"],
)


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000,
    )

    session_id: str | None = None

    # Puede venir automáticamente desde
    # /parcels/{parcel_id}.
    parcel_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str

    parcel_id: str | None = None
    parcel_name: str | None = None

    orchestrator: str = "langflow"


def _normalize(
    value: str,
) -> str:

    value = unicodedata.normalize(
        "NFKD",
        value,
    )

    value = "".join(
        character
        for character in value
        if not unicodedata.combining(
            character
        )
    )

    return " ".join(
        value
        .casefold()
        .split()
    )


def _visible_parcels(
    *,
    db: Session,
    current_user: UserModel,
):

    parcels = (
        ParcelRepository(
            db
        )
        .list_all()
    )

    if (
        current_user.system_role
        == SystemRole.ADMIN.value
    ):
        return parcels

    memberships = (
        ParcelMembershipRepository(
            db
        )
        .list_by_user(
            current_user.id
        )
    )

    visible_ids = {
        membership.parcel_id
        for membership
        in memberships
    }

    return [
        parcel
        for parcel in parcels
        if parcel.id in visible_ids
    ]


def _has_parcel_intent(
    message: str,
) -> bool:

    normalized = _normalize(
        message
    )

    terms = (
        "parcela",
        "regar",
        "riego",
        "humedad",
        "estado",
        "recomendacion",
        "riesgo",
        "cultivo",
        "suelo",
        "datos",
        "por que",
    )

    return any(
        term in normalized
        for term in terms
    )


def _resolve_parcel(
    *,
    message: str,
    parcel_id: str | None,
    parcels,
):

    # =========================================
    # 1. ID suministrado por el frontend
    # =========================================

    if parcel_id:

        for parcel in parcels:

            if (
                str(parcel.id)
                == str(parcel_id)
            ):
                return parcel

        raise HTTPException(
            status_code=404,
            detail=(
                "La parcela indicada no existe "
                "o no está disponible para este usuario."
            ),
        )

    # =========================================
    # 2. Buscar nombre dentro del mensaje
    # =========================================

    normalized_message = (
        _normalize(
            message
        )
    )

    matches = []

    for parcel in parcels:

        parcel_name = _normalize(
            parcel.name
        )

        if (
            parcel_name
            and parcel_name
            in normalized_message
        ):
            matches.append(
                parcel
            )

    if matches:

        # Si algún nombre fuera parte de otro,
        # preferimos el nombre más específico.
        matches.sort(
            key=lambda item:
                len(item.name),
            reverse=True,
        )

        return matches[0]

    # =========================================
    # 3. Si solo existe una parcela visible,
    #    "mi parcela" puede resolverse sola.
    # =========================================

    if (
        len(parcels) == 1
        and
        _has_parcel_intent(
            message
        )
    ):
        return parcels[0]

    return None


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    payload: ChatRequest,

    current_user: UserModel = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):

    message = payload.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail=(
                "El mensaje no puede estar vacío."
            ),
        )

    session_id = (
        payload.session_id
        or f"agritwin-{uuid4()}"
    )

    parcels = _visible_parcels(
        db=db,
        current_user=current_user,
    )

    selected_parcel = (
        _resolve_parcel(
            message=message,
            parcel_id=payload.parcel_id,
            parcels=parcels,
        )
    )

    # =========================================
    # CONTEXTO PARA LANGFLOW
    # =========================================

    if selected_parcel:

        message_for_agent = f"""
CONTEXTO INTERNO DE AGRITWIN:

La parcela activa del usuario es:

Nombre: {selected_parcel.name}
parcel_id: {selected_parcel.id}

REGLAS OBLIGATORIAS:

- Usa parcel_id={selected_parcel.id} cuando una herramienta
  de AgriTwin solicite el identificador de la parcela.

- Para hablar con el agricultor utiliza el nombre:
  "{selected_parcel.name}".

- No muestres el parcel_id, UUID ni otros identificadores
  internos salvo que el usuario lo solicite expresamente.

- Si el usuario dice "mi parcela", "esta parcela",
  "regarla", "ella", "¿por qué?" u otra referencia
  contextual, se refiere a esta parcela.

- No busques la parcela utilizando su nombre en una
  herramienta que requiera parcel_id.

- No inventes datos.

MENSAJE DEL USUARIO:

{message}
""".strip()

    elif (
        len(parcels) > 1
        and
        _has_parcel_intent(
            message
        )
    ):

        available_names = "\n".join(
            f"- {parcel.name}"
            for parcel in parcels
        )

        message_for_agent = f"""
CONTEXTO INTERNO DE AGRITWIN:

No se ha podido determinar con seguridad qué parcela
quiere consultar el usuario.

Parcelas disponibles para este usuario:

{available_names}

No llames herramientas que requieran parcel_id hasta
que el usuario indique cuál de estas parcelas quiere
consultar.

Pregunta al usuario de forma breve qué parcela desea
consultar.

No muestres IDs internos.

MENSAJE DEL USUARIO:

{message}
""".strip()

    else:

        message_for_agent = message

    try:

        answer = await run_langflow(
            message=message_for_agent,
            session_id=session_id,
        )

    except LangflowClientError as exc:

        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return ChatResponse(
        session_id=session_id,
        answer=answer,

        parcel_id=(
            str(selected_parcel.id)
            if selected_parcel
            else None
        ),

        parcel_name=(
            selected_parcel.name
            if selected_parcel
            else None
        ),
    )
