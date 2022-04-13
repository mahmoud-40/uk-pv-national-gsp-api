""" Main FastAPI app """
import logging
import os
from datetime import timedelta

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from nowcasting_datamodel.models import Forecast, ManyForecasts
from sqlalchemy.orm.session import Session

from database import (
    get_forecasts_for_a_specific_gsp_from_database,
    get_forecasts_from_database,
    get_latest_national_forecast_from_database,
    get_session,
)
from gsp import get_gsp_boundaries_from_eso_wgs84
from gsp import router as gsp_router

logger = logging.getLogger(__name__)

version = "0.1.20"
description = """
The Nowcasting API is still under development. It only returns zeros for now.
"""
app = FastAPI(
    title="Nowcasting API",
    version=version,
    description=description,
    contact={
        "name": "Open Climate Fix",
        "url": "https://openclimatefix.org",
        "email": "info@openclimatefix.org",
    },
    license_info={
        "name": "MIT License",
        "url": "https://github.com/openclimatefix/nowcasting_api/blob/main/LICENSE",
    },
)

origins = os.getenv("ORIGINS", "https://app.nowcasting.io").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

thirty_minutes = timedelta(minutes=30)


# Dependency
v0_route = "/v0/forecasts/GB/pv"


app.include_router(gsp_router, prefix=f"{v0_route}")


@app.get("/")
async def get_api_information():
    """Get information about the API itself"""

    logger.info("Route / has be called")

    return {
        "title": "Nowcasting API",
        "version": version,
        "description": description,
        "documentation": "https://api.nowcasting.io/docs",
    }


@app.get(v0_route + "/gsp", response_model=ManyForecasts)
async def get_all_available_forecasts(session: Session = Depends(get_session)) -> ManyForecasts:
    """Get the latest information for all available forecasts"""

    logger.info("Get forecasts for all gsps")

    return get_forecasts_from_database(session=session)


@app.get(v0_route + "/national", response_model=Forecast)
async def get_nationally_aggregated_forecasts(session: Session = Depends(get_session)) -> Forecast:
    """Get an aggregated forecast at the national level"""

    logger.debug("Get national forecasts")
    return get_latest_national_forecast_from_database(session=session)


@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon() -> FileResponse:
    """Get favicon"""
    return FileResponse("src/favicon.ico")
