"""
ConTroller for handling build-related requests
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.models.build_models import Build, BuildType, BuildDifficulty, BuildResponse, BuildGuide
from app.services.build_service import BuildService


class BuildController:
    """Controller to handle build-related requests"""
    
    def __init__(self, build_service: BuildService):
        self.build_service = build_service
        self.router = APIRouter(prefix="/builds", tags=["builds"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure routes for the controller"""
        
        @self.router.get("/", response_model=BuildResponse)
        async def get_all_builds():
            """Obtain all available builds"""
            builds = await self.build_service.get_all_builds()
            return BuildResponse(
                builds=builds,
                total=len(builds),
                build_type="all"
            )
        
        @self.router.get("/types", response_model=List[str])
        async def get_build_types():
            """Obtain all available build types"""
            return [build_type.value for build_type in BuildType]
        
        @self.router.get("/difficulties", response_model=List[str])
        async def get_difficulties():
            """Obtain all available difficulties"""
            return [difficulty.value for difficulty in BuildDifficulty]
        
        @self.router.get("/search", response_model=BuildResponse)
        async def search_builds(q: str):
            """Search builds by name or description"""
            builds = await self.build_service.search_builds(q)
            return BuildResponse(
                builds=builds,
                total=len(builds),
                build_type="search"
            )
        
        @self.router.get("/{build_type}", response_model=BuildResponse)
        async def get_builds_by_type(build_type: BuildType):
            """Obtain builds filtered by type with detailed steps"""
            builds = await self.build_service.get_builds_by_type(build_type)
            return BuildResponse(
                builds=builds,
                total=len(builds),
                build_type=build_type.value
            )
        
        @self.router.get("/{build_type}/guide", response_model=BuildGuide)
        async def get_build_guide(build_type: BuildType):
            """Obtain the build guide for a specific build type"""
            try:
                return await self.build_service.get_build_guide(build_type)
            except ValueError as e:
                raise HTTPException(status_code=404, detail=str(e))
        
        @self.router.get("/difficulty/{difficulty}", response_model=BuildResponse)
        async def get_builds_by_difficulty(difficulty: BuildDifficulty):
            """Obtain builds filtered by difficulty"""
            builds = await self.build_service.get_builds_by_difficulty(difficulty.value)
            return BuildResponse(
                builds=builds,
                total=len(builds),
                build_type="all"
            )
