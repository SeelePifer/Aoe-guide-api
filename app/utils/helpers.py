"""
Helper functions for build management and API response formatting.
"""

from typing import List, Dict, Any
from app.models.build_models import Build, BuildStep


def format_build_response(builds: List[Build], build_type: str) -> Dict[str, Any]:
    """Formatting the build response for the API"""
    return {
        "builds": [build.dict() for build in builds],
        "total": len(builds),
        "build_type": build_type
    }


def format_build_guide_response(guide_data: Dict[str, Any]) -> Dict[str, Any]:
    """Formatting the build guide response for the API"""
    return {
        "build_type": guide_data["build_type"],
        "main_build": guide_data["main_build"],
        "alternative_builds": guide_data["alternative_builds"],
        "total_available": guide_data["total_available"]
    }


def validate_build_data(build_data: Dict[str, Any]) -> bool:
    """Validate the structure of build data"""
    required_fields = ["name", "difficulty", "description", "build_type"]
    return all(field in build_data for field in required_fields)


def sanitize_search_query(query: str) -> str:
    """Sanitize the search query to prevent injection attacks"""
    return query.strip().lower()


def group_builds_by_difficulty(builds: List[Build]) -> Dict[str, List[Build]]:
    """Group builds by difficulty"""
    groups = {}
    for build in builds:
        difficulty = build.difficulty.value
        if difficulty not in groups:
            groups[difficulty] = []
        groups[difficulty].append(build)
    return groups


def group_builds_by_type(builds: List[Build]) -> Dict[str, List[Build]]:
    """Group builds by type"""
    groups = {}
    for build in builds:
        build_type = build.build_type.value
        if build_type not in groups:
            groups[build_type] = []
        groups[build_type].append(build)
    return groups
