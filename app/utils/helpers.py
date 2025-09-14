"""
Utilidades y helpers comunes
"""

from typing import List, Dict, Any
from app.models.build_models import Build, BuildStep


def format_build_response(builds: List[Build], build_type: str) -> Dict[str, Any]:
    """Formatea la respuesta de builds para la API"""
    return {
        "builds": [build.dict() for build in builds],
        "total": len(builds),
        "build_type": build_type
    }


def format_build_guide_response(guide_data: Dict[str, Any]) -> Dict[str, Any]:
    """Formatea la respuesta de guía de build para la API"""
    return {
        "build_type": guide_data["build_type"],
        "main_build": guide_data["main_build"],
        "alternative_builds": guide_data["alternative_builds"],
        "total_available": guide_data["total_available"]
    }


def validate_build_data(build_data: Dict[str, Any]) -> bool:
    """Valida que los datos del build sean correctos"""
    required_fields = ["name", "difficulty", "description", "build_type"]
    return all(field in build_data for field in required_fields)


def sanitize_search_query(query: str) -> str:
    """Sanitiza la consulta de búsqueda"""
    return query.strip().lower()


def group_builds_by_difficulty(builds: List[Build]) -> Dict[str, List[Build]]:
    """Agrupa builds por dificultad"""
    groups = {}
    for build in builds:
        difficulty = build.difficulty.value
        if difficulty not in groups:
            groups[difficulty] = []
        groups[difficulty].append(build)
    return groups


def group_builds_by_type(builds: List[Build]) -> Dict[str, List[Build]]:
    """Agrupa builds por tipo"""
    groups = {}
    for build in builds:
        build_type = build.build_type.value
        if build_type not in groups:
            groups[build_type] = []
        groups[build_type].append(build)
    return groups
