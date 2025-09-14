"""
Domain objects for AOE2 build strategies and guides.
"""

from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class BuildType(str, Enum):
    """Available build types"""
    FEUDAL_RUSH = "feudal_rush"
    FAST_CASTLE = "fast_castle"
    DARK_AGE_RUSH = "dark_age_rush"
    WATER_MAPS = "water_maps"


class BuildDifficulty(str, Enum):
    """Level of difficulty for builds"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class BuildStep(BaseModel):
    """Steps in a build order"""
    step_number: int
    age: str
    time: Optional[str] = None
    action: str
    details: str
    resources_needed: Optional[dict] = None


class Build(BaseModel):
    """Principal build order structure"""
    name: str
    difficulty: BuildDifficulty
    description: str
    build_type: BuildType
    feudal_age_time: Optional[int] = None
    castle_age_time: Optional[int] = None
    imperial_age_time: Optional[int] = None
    steps: Optional[List[BuildStep]] = None


class BuildResponse(BaseModel):
    """API response for multiple builds"""
    builds: List[Build]
    total: int
    build_type: str


class BuildGuide(BaseModel):
    """Guide for a specific build with alternatives"""
    build_type: str
    main_build: dict
    alternative_builds: List[dict]
    total_available: int
