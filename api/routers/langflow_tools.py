from fastapi import APIRouter

from pydantic import BaseModel


class IrrigationRequest(BaseModel):
    plot_id: str

router = APIRouter(
    prefix="/api/langflow",
    tags=["Langflow"],
)

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "AgriTwin Backend",
    }

@router.post("/irrigation")
async def irrigation(request: IrrigationRequest):

    # TEMPORAL:
    # luego aquí conectaremos tu motor IA real.

    return {
        "source": "ai_inference_engine",
        "recommendation_id": "REC-DEMO-001",
        "plot_id": request.plot_id,
        "irrigate": True,
        "water_mm": 14.8,
        "confidence": 0.86,
        "status": "integration_test",
    }