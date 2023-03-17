from fastapi import APIRouter, FastAPI
from loguru import logger

from app.config import settings, setup_app_logging
from app import api

# setup logging as early as possible
setup_app_logging(config=settings)

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


@app.get("/")
def index():
    return {"message": "Pedestrian Detection Service"}

app.include_router(api.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    # Use this for debugging purposes only
    logger.warning("Running in development mode. Do not run like this in production.")
    import uvicorn

    uvicorn.run(app, host="localhost", port=8001, log_level="debug")