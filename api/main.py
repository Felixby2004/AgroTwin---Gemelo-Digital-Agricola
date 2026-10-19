from fastapi import FastAPI

from api.routers import (
    health_router,
    parcels_router,
    evidence_router,
    farmer_knowledge_router,
    reasoning_router,
    parcel_reasoning_router,
    decision_traces_router,
    parcel_state_router,
    sensors_router,
    satellite_router,
    copernicus_router,
    data_governance_router,
    auth_router,
    memberships_router,
    reports_router,
    ml_predictions,
)

from api.routers.users import (
    router as users_router,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

app = FastAPI(
    title=(
        "Participatory Agricultural "
        "Digital Twin API"
    ),

    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agrotwin-gemelo-digital-agricola.onrender.com",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(
    health_router
)

app.include_router(
    parcels_router
)

app.include_router(
    evidence_router
)

app.include_router(
    farmer_knowledge_router
)

app.include_router(
    reasoning_router
)

app.include_router(
    parcel_reasoning_router
)

app.include_router(
    decision_traces_router
)

app.include_router(
    parcel_state_router
)

app.include_router(
    sensors_router
)

app.include_router(
    satellite_router
)

app.include_router(
    copernicus_router
)

app.include_router(
    data_governance_router
)

app.include_router(
    auth_router
)

app.include_router(
    users_router
)

app.include_router(
    memberships_router
)

app.include_router(
    reports_router
)

app.include_router(
    ml_predictions.router
)

from api.routers.langflow_tools import router as langflow_router

app.include_router(langflow_router)

@app.get("/")
def root():

    return {
        "service": (
            "Participatory Agricultural "
            "Digital Twin"
        ),

        "version": "0.1.0",
    }

# =========================================================
# LANGFLOW CHATBOT
# =========================================================
from api.routers.chatbot import router as chatbot_router

app.include_router(chatbot_router)
