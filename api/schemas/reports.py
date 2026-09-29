from datetime import datetime
from typing import Any

from api.schemas.common import (
    APIModel,
)


class ReportPreview(
    APIModel
):

    parcel_id: str

    generated_at: datetime

    parcel: dict[
        str,
        Any,
    ]

    summary: dict[
        str,
        Any,
    ]

    latest_decision: (
        dict[
            str,
            Any,
        ]
        | None
    )

    evidence: list[
        dict[
            str,
            Any,
        ]
    ]

    sensors: list[
        dict[
            str,
            Any,
        ]
    ]

    farmer_knowledge: list[
        dict[
            str,
            Any,
        ]
    ]

    decision_traces: list[
        dict[
            str,
            Any,
        ]
    ]

    ml_complementary: dict[
        str,
        Any,
    ]

    governance: dict[
        str,
        Any,
    ]