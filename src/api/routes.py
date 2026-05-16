from fastapi import APIRouter
from fastapi import HTTPException
from typing import Optional

from src.api.services import (
    get_projects,
    get_generation_data,
    get_restrictions_summary
)

router = APIRouter()


@router.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


@router.get("/projects")
def projects():

    return get_projects()


@router.get("/generation/{project_id}")
def generation(
    project_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frequency: str = "daily"
):

    if frequency not in [
        "daily",
        "monthly"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "frequency must be "
                "'daily' or 'monthly'"
            )
        )

    result = get_generation_data(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency
    )

    if result is None:

        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

    return result


@router.get("/restrictions/summary")
def restrictions_summary(
    project_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):

    return get_restrictions_summary(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date
    )