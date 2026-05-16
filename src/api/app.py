from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(
    title="Wind Generation API",

    description=(
        "API for processed wind "
        "generation datasets"
    ),

    version="1.0.0"
)

app.include_router(router)