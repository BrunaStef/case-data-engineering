from pydantic import BaseModel
from typing import Optional


class ProjectResponse(BaseModel):

    projeto: str

    nom_estado: Optional[str]

    nom_subsistema: Optional[str]


class GenerationResponse(BaseModel):

    projeto: str

    period: str

    total_generation: float


class RestrictionSummaryResponse(BaseModel):

    cod_razaorestricao: Optional[str]

    total_hours: int

    total_mwh_restricted: float