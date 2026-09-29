from datetime import datetime

from pydantic import BaseModel, Field


class IrrigationEvent(BaseModel):
    timestamp: datetime

    amount_mm: float = Field(
        ...,
        ge=0,
    )

    duration_hours: float | None = Field(
        default=None,
        ge=0,
    )

    efficiency: float = Field(
        default=1.0,
        gt=0,
        le=1,
    )

    source: str = "manual"

    notes: str | None = None

    @property
    def effective_irrigation_mm(self) -> float:
        return self.amount_mm * self.efficiency