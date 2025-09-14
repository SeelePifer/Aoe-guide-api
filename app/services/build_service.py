"""
Optimized business logic service for builds
"""

import time
from typing import List, Optional, Tuple
from app.models.build_models import Build, BuildType, BuildStep, BuildGuide
from app.models.pagination_models import PaginationParams, FilterParams, PaginatedResponse, PerformanceMetrics
from app.repositories.build_repository import BuildRepository
import logging

logger = logging.getLogger(__name__)


class OptimizedBuildService:
    """Optimized service for build management"""
    
    def __init__(self, build_repository: BuildRepository):
        self.build_repository = build_repository
    
    async def get_all_builds(self, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Get all available builds with pagination"""
        start_time = time.time()
        
        builds, total = await self.build_repository.get_all_builds(pagination)
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_all_builds completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_builds_by_type(self, build_type: BuildType, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Get builds filtered by type with pagination"""
        start_time = time.time()
        
        builds, total = await self.build_repository.get_builds_by_type(build_type, pagination)
        
        # Ensure all builds have detailed steps
        for build in builds:
            if not build.steps:
                build.steps = self._get_build_steps(build.name, build.build_type)
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_builds_by_type({build_type.value}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_builds_by_difficulty(self, difficulty: str, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Get builds filtered by difficulty with pagination"""
        start_time = time.time()
        
        builds, total = await self.build_repository.get_builds_by_difficulty(difficulty, pagination)
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_builds_by_difficulty({difficulty}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def search_builds(self, query: str, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Buscar builds por nombre o descripción con paginación"""
        start_time = time.time()
        
        builds, total = await self.build_repository.search_builds(query, pagination)
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"search_builds({query}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_filtered_builds(self, filters: FilterParams, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Obtener builds con filtros múltiples y paginación"""
        start_time = time.time()
        
        builds, total = await self.build_repository.get_filtered_builds(filters, pagination)
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_filtered_builds completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_build_guide(self, build_type: BuildType) -> BuildGuide:
        """Obtener guía detallada paso a paso para un tipo de build específico"""
        builds, _ = await self.get_builds_by_type(build_type)
        
        if not builds:
            raise ValueError(f"No se encontraron builds para el tipo: {build_type.value}")
        
        # Obtener el primer build como ejemplo principal
        main_build = builds[0]
        if not main_build.steps:
            main_build.steps = self._get_build_steps(main_build.name, main_build.build_type)
        
        # Crear guía detallada
        guide = BuildGuide(
            build_type=build_type.value,
            main_build={
                "name": main_build.name,
                "difficulty": main_build.difficulty.value,
                "description": main_build.description,
                "steps": [step.dict() for step in main_build.steps]
            },
            alternative_builds=[
                {
                    "name": build.name,
                    "difficulty": build.difficulty.value,
                    "description": build.description,
                    "steps": [step.dict() for step in (build.steps or self._get_build_steps(build.name, build.build_type))]
                }
                for build in builds[1:6]  # Mostrar hasta 5 builds alternativos
            ],
            total_available=len(builds)
        )
        
        return guide
    
    def _get_build_steps(self, build_name: str, build_type: BuildType) -> List[BuildStep]:
        """Obtiene los pasos detallados para un build específico"""
        
        # Base de datos de builds con pasos detallados
        build_guides = {
            "Scout Rush": {
                BuildType.FEUDAL_RUSH: [
                    BuildStep(
                        step_number=1,
                        age="Dark Age",
                        time="0:00-2:00",
                        action="Construir 6 Villagers",
                        details="Crear 6 villagers en el Town Center. 4 en sheep, 2 en wood.",
                        resources_needed={"food": 300, "wood": 0}
                    ),
                    BuildStep(
                        step_number=2,
                        age="Dark Age",
                        time="2:00-4:00",
                        action="Construir House y Lumber Camp",
                        details="Construir 1 house y 1 lumber camp. 2 villagers en wood, 4 en sheep.",
                        resources_needed={"food": 0, "wood": 100}
                    ),
                    BuildStep(
                        step_number=3,
                        age="Dark Age",
                        time="4:00-6:00",
                        action="Construir 2 Houses más",
                        details="Construir 2 houses adicionales. Mantener 2 en wood, 4 en sheep.",
                        resources_needed={"food": 0, "wood": 100}
                    ),
                    BuildStep(
                        step_number=4,
                        age="Dark Age",
                        time="6:00-8:00",
                        action="Construir Barracks",
                        details="Construir barracks cerca del enemigo. 1 villager en stone, resto en food/wood.",
                        resources_needed={"food": 0, "wood": 175, "stone": 100}
                    ),
                    BuildStep(
                        step_number=5,
                        age="Dark Age",
                        time="8:00-10:00",
                        action="Research Loom",
                        details="Investigar Loom en el Town Center antes de avanzar a Feudal Age.",
                        resources_needed={"food": 50, "gold": 0}
                    ),
                    BuildStep(
                        step_number=6,
                        age="Feudal Age",
                        time="10:00-12:00",
                        action="Construir Stable",
                        details="Construir stable inmediatamente al llegar a Feudal Age.",
                        resources_needed={"food": 0, "wood": 100}
                    ),
                    BuildStep(
                        step_number=7,
                        age="Feudal Age",
                        time="12:00-15:00",
                        action="Producir Scouts",
                        details="Producir 3-4 scouts y atacar al enemigo. Continuar producción.",
                        resources_needed={"food": 80, "gold": 0}
                    ),
                    BuildStep(
                        step_number=8,
                        age="Feudal Age",
                        time="15:00+",
                        action="Presión constante",
                        details="Mantener presión con scouts, construir más stables si es necesario.",
                        resources_needed={"food": 80, "gold": 0}
                    )
                ]
            },
            "Archer Rush": {
                BuildType.FEUDAL_RUSH: [
                    BuildStep(
                        step_number=1,
                        age="Dark Age",
                        time="0:00-2:00",
                        action="Construir 6 Villagers",
                        details="Crear 6 villagers. 4 en sheep, 2 en wood.",
                        resources_needed={"food": 300, "wood": 0}
                    ),
                    BuildStep(
                        step_number=2,
                        age="Dark Age",
                        time="2:00-4:00",
                        action="Construir Lumber Camp",
                        details="Construir lumber camp. 2 villagers en wood, 4 en sheep.",
                        resources_needed={"food": 0, "wood": 100}
                    ),
                    BuildStep(
                        step_number=3,
                        age="Dark Age",
                        time="4:00-6:00",
                        action="Construir Houses",
                        details="Construir 2 houses. Mantener 2 en wood, 4 en sheep.",
                        resources_needed={"food": 0, "wood": 100}
                    ),
                    BuildStep(
                        step_number=4,
                        age="Dark Age",
                        time="6:00-8:00",
                        action="Construir Barracks",
                        details="Construir barracks. 1 villager en stone, resto en food/wood.",
                        resources_needed={"food": 0, "wood": 175, "stone": 100}
                    ),
                    BuildStep(
                        step_number=5,
                        age="Dark Age",
                        time="8:00-10:00",
                        action="Research Loom",
                        details="Investigar Loom antes de avanzar a Feudal Age.",
                        resources_needed={"food": 50, "gold": 0}
                    ),
                    BuildStep(
                        step_number=6,
                        age="Feudal Age",
                        time="10:00-12:00",
                        action="Construir Archery Range",
                        details="Construir archery range inmediatamente al llegar a Feudal Age.",
                        resources_needed={"food": 0, "wood": 175}
                    ),
                    BuildStep(
                        step_number=7,
                        age="Feudal Age",
                        time="12:00-15:00",
                        action="Producir Archers",
                        details="Producir 4-6 archers. Construir blacksmith para upgrades.",
                        resources_needed={"food": 25, "wood": 50, "gold": 0}
                    ),
                    BuildStep(
                        step_number=8,
                        age="Feudal Age",
                        time="15:00+",
                        action="Atacar con Archers",
                        details="Atacar al enemigo con archers. Construir más ranges si es necesario.",
                        resources_needed={"food": 25, "wood": 50, "gold": 0}
                    )
                ]
            }
        }
        
        # Buscar el build específico
        if build_name in build_guides and build_type in build_guides[build_name]:
            return build_guides[build_name][build_type]
        
        # Si no se encuentra el build específico, devolver pasos genéricos por tipo
        return self._get_generic_steps(build_type)
    
    def _get_generic_steps(self, build_type: BuildType) -> List[BuildStep]:
        """Obtiene pasos genéricos para un tipo de build"""
        generic_steps = {
            BuildType.FEUDAL_RUSH: [
                BuildStep(
                    step_number=1,
                    age="Dark Age",
                    time="0:00-2:00",
                    action="Construir 6 Villagers",
                    details="Crear 6 villagers. 4 en sheep, 2 en wood.",
                    resources_needed={"food": 300, "wood": 0}
                ),
                BuildStep(
                    step_number=2,
                    age="Dark Age",
                    time="2:00-4:00",
                    action="Construir Lumber Camp",
                    details="Construir lumber camp. 2 villagers en wood, 4 en sheep.",
                    resources_needed={"food": 0, "wood": 100}
                ),
                BuildStep(
                    step_number=3,
                    age="Dark Age",
                    time="4:00-6:00",
                    action="Construir Houses",
                    details="Construir 2 houses. Mantener 2 en wood, 4 en sheep.",
                    resources_needed={"food": 0, "wood": 100}
                ),
                BuildStep(
                    step_number=4,
                    age="Dark Age",
                    time="6:00-8:00",
                    action="Construir Barracks",
                    details="Construir barracks cerca del enemigo.",
                    resources_needed={"food": 0, "wood": 175, "stone": 100}
                ),
                BuildStep(
                    step_number=5,
                    age="Dark Age",
                    time="8:00-10:00",
                    action="Research Loom",
                    details="Investigar Loom antes de avanzar a Feudal Age.",
                    resources_needed={"food": 50, "gold": 0}
                ),
                BuildStep(
                    step_number=6,
                    age="Feudal Age",
                    time="10:00+",
                    action="Estrategia Feudal",
                    details="Implementar la estrategia específica del build en Feudal Age.",
                    resources_needed={"food": 0, "wood": 0, "gold": 0}
                )
            ],
            BuildType.FAST_CASTLE: [
                BuildStep(
                    step_number=1,
                    age="Dark Age",
                    time="0:00-2:00",
                    action="Construir 6 Villagers",
                    details="Crear 6 villagers. 4 en sheep, 2 en wood.",
                    resources_needed={"food": 300, "wood": 0}
                ),
                BuildStep(
                    step_number=2,
                    age="Dark Age",
                    time="2:00-4:00",
                    action="Construir Lumber Camp",
                    details="Construir lumber camp. 2 villagers en wood, 4 en sheep.",
                    resources_needed={"food": 0, "wood": 100}
                ),
                BuildStep(
                    step_number=3,
                    age="Dark Age",
                    time="4:00-6:00",
                    action="Construir Houses",
                    details="Construir 2 houses. Mantener 2 en wood, 4 en sheep.",
                    resources_needed={"food": 0, "wood": 100}
                ),
                BuildStep(
                    step_number=4,
                    age="Dark Age",
                    time="6:00-8:00",
                    action="Construir Mining Camp",
                    details="Construir mining camp en gold. 2 villagers en gold, 2 en wood, 2 en sheep.",
                    resources_needed={"food": 0, "wood": 100, "stone": 0}
                ),
                BuildStep(
                    step_number=5,
                    age="Dark Age",
                    time="8:00-10:00",
                    action="Research Loom",
                    details="Investigar Loom antes de avanzar a Feudal Age.",
                    resources_needed={"food": 50, "gold": 0}
                ),
                BuildStep(
                    step_number=6,
                    age="Feudal Age",
                    time="10:00-12:00",
                    action="Construir Market y Blacksmith",
                    details="Construir market y blacksmith. 3 villagers en gold, 2 en wood, 3 en sheep.",
                    resources_needed={"food": 0, "wood": 275, "gold": 0}
                ),
                BuildStep(
                    step_number=7,
                    age="Feudal Age",
                    time="12:00-15:00",
                    action="Avanzar a Castle Age",
                    details="Avanzar a Castle Age lo más rápido posible. 4 villagers en gold, 2 en wood, 2 en sheep.",
                    resources_needed={"food": 800, "gold": 200}
                ),
                BuildStep(
                    step_number=8,
                    age="Castle Age",
                    time="15:00+",
                    action="Estrategia Castle",
                    details="Implementar la estrategia específica del build en Castle Age.",
                    resources_needed={"food": 0, "wood": 0, "gold": 0}
                )
            ]
        }
        
        return generic_steps.get(build_type, [])


# Alias para compatibilidad hacia atrás
BuildService = OptimizedBuildService
