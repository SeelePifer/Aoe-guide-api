"""
Modelos de dominio para builds de Age of Empires
"""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class BuildType(str, Enum):
    """Tipos de builds disponibles"""
    FEUDAL_RUSH = "feudal_rush"
    FAST_CASTLE = "fast_castle"
    DARK_AGE_RUSH = "dark_age_rush"
    WATER_MAPS = "water_maps"


class BuildDifficulty(str, Enum):
    """Niveles de dificultad de los builds"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class BuildStep(BaseModel):
    """Paso individual de un build"""
    step_number: int
    age: str
    time: Optional[str] = None
    action: str
    details: str
    resources_needed: Optional[dict] = None


class Build(BaseModel):
    """Modelo principal de un build"""
    name: str
    difficulty: BuildDifficulty
    description: str
    build_type: BuildType
    feudal_age_time: Optional[int] = None
    castle_age_time: Optional[int] = None
    imperial_age_time: Optional[int] = None
    steps: Optional[List[BuildStep]] = None


class BuildResponse(BaseModel):
    """Respuesta de la API para builds"""
    builds: List[Build]
    total: int
    build_type: str


class BuildGuide(BaseModel):
    """Guía detallada de un tipo de build"""
    build_type: str
    main_build: dict
    alternative_builds: List[dict]
    total_available: int
