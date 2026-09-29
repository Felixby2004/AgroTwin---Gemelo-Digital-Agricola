from api.routers.health import (
    router as health_router,
)

from api.routers.parcels import (
    router as parcels_router,
)

from api.routers.evidence import (
    router as evidence_router,
)

from api.routers.farmer_knowledge import (
    router as farmer_knowledge_router,
)

from api.routers.reasoning import (
    router as reasoning_router,
)

from api.routers.parcel_reasoning import (
    router as parcel_reasoning_router,
)

from api.routers.decision_traces import (
    router as decision_traces_router,
)

from api.routers.farmer_response import (
    router as farmer_response_router,
)

from api.routers.parcel_state import (
    router as parcel_state_router,
)

from api.routers.sensors import (
    router as sensors_router,
)

from api.routers.satellite import (
    router as satellite_router,
)

from api.routers.copernicus import (
    router as copernicus_router,
)

from api.routers.data_governance import (
    router as data_governance_router,
)

from api.routers.auth import (
    router as auth_router,
)

from api.routers.memberships import (
    router as memberships_router,
)

from api.routers.reports import (
    router as reports_router,
)

__all__ = [
    "health_router",
    "parcels_router",
    "evidence_router",
    "farmer_knowledge_router",
    "reasoning_router",
    "parcel_reasoning_router",
    "decision_traces_router",
    "farmer_response_router",
    "parcel_state_router",
    "sensors_router",
    "satellite_router",
    "copernicus_router",
    "data_governance_router",
    "auth_router",
    "memberships_router",
    "reports_router",
]