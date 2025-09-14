"""
Controlador para endpoints de builds
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.build_models import Build, BuildType, BuildDifficulty, BuildResponse, BuildGuide
from app.services.build_service import BuildService


class BuildController:
    """Controlador para manejar las peticiones de builds"""
    
    def __init__(self, build_service: BuildService):
        self.build_service = build_service
        self.router = APIRouter(prefix="/builds", tags=["builds"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas del controlador"""
        
        @self.router.get("/", response_model=BuildResponse)
        async def get_all_builds():
            """Obtener todos los builds disponibles"""
            builds = await self.build_service.get_all_builds()
            return BuildResponse(
                builds=builds,
                total=len(builds),
                build_type="all"
            )
        
        @self.router.get("/types", response_model=List[str])
        async def get_build_types():
            """Obtener todos los tipos de builds disponibles"""
            return [build_type.value for build_type in BuildType]
        
        @self.router.get("/difficulties", response_model=List[str])
        async def get_difficulties():
            """Obtener todas las dificultades disponibles"""
            return [difficulty.value for difficulty in BuildDifficulty]
        
        @self.router.get("/search", response_model=BuildResponse)
        async def search_builds(q: str):
            """Buscar builds por nombre o descripción"""
            builds = await self.build_service.search_builds(q)
            return BuildResponse(
                builds=builds,
                total=len(builds),
                build_type="search"
            )
        
        @self.router.get("/{build_type}", response_model=BuildResponse)
        async def get_builds_by_type(build_type: BuildType):
            """Obtener builds filtrados por tipo con pasos detallados"""
            builds = await self.build_service.get_builds_by_type(build_type)
            return BuildResponse(
                builds=builds,
                total=len(builds),
                build_type=build_type.value
            )
        
        @self.router.get("/{build_type}/guide", response_model=BuildGuide)
        async def get_build_guide(build_type: BuildType):
            """Obtener guía detallada paso a paso para un tipo de build específico"""
            try:
                return await self.build_service.get_build_guide(build_type)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.router.get("/difficulty/{difficulty}", response_model=BuildResponse)
        async def get_builds_by_difficulty(difficulty: BuildDifficulty):
            """Obtener builds filtrados por dificultad"""
            builds = await self.build_service.get_builds_by_difficulty(difficulty.value)
            return BuildResponse(
                builds=builds,
                total=len(builds),
                build_type="all"
            )
