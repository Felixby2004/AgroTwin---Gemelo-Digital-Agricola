from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get("")
def health():

    return {
        "status": "ok",
        "service": "agricultural-digital-twin-api",
    }