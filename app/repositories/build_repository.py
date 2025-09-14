"""
Repositorio optimizado para acceso a datos de builds con cache y paginación
"""

import time
from typing import List, Tuple, Optional
from abc import ABC, abstractmethod
from app.models.build_models import Build, BuildType, BuildDifficulty
from app.models.pagination_models import PaginationParams, FilterParams
from app.config.cache import build_cache
import logging

logger = logging.getLogger(__name__)


class BuildRepositoryInterface(ABC):
    """Interfaz para el repositorio de builds"""
    
    @abstractmethod
    async def get_all_builds(self, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        pass
    
    @abstractmethod
    async def get_builds_by_type(self, build_type: BuildType, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        pass
    
    @abstractmethod
    async def get_builds_by_difficulty(self, difficulty: str, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        pass
    
    @abstractmethod
    async def search_builds(self, query: str, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        pass
    
    @abstractmethod
    async def get_filtered_builds(self, filters: FilterParams, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        pass


class OptimizedBuildRepository(BuildRepositoryInterface):
    """Repositorio optimizado con cache y paginación"""
    
    def __init__(self, builds_cache: List[Build]):
        self.builds_cache = builds_cache
        self.cache = build_cache
        self._build_indexes()
    
    def _build_indexes(self):
        """Construye índices para búsquedas más rápidas"""
        self._type_index = {}
        self._difficulty_index = {}
        self._name_index = {}
        
        for i, build in enumerate(self.builds_cache):
            # Índice por tipo
            if build.build_type not in self._type_index:
                self._type_index[build.build_type] = []
            self._type_index[build.build_type].append(i)
            
            # Índice por dificultad
            if build.difficulty not in self._difficulty_index:
                self._difficulty_index[build.difficulty] = []
            self._difficulty_index[build.difficulty].append(i)
            
            # Índice por nombre (para búsquedas)
            self._name_index[build.name.lower()] = i
    
    async def get_all_builds(self, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Obtener todos los builds disponibles con paginación"""
        start_time = time.time()
        
        # Intentar obtener del cache
        cached_builds = self.cache.get_cached_builds()
        if cached_builds:
            logger.debug("Cache HIT: get_all_builds")
            builds = cached_builds
        else:
            logger.debug("Cache MISS: get_all_builds")
            builds = self.builds_cache
            # Cachear para futuras consultas
            self.cache.cache_builds(builds)
        
        total = len(builds)
        
        # Aplicar paginación
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_all_builds completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_builds_by_type(self, build_type: BuildType, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Obtener builds filtrados por tipo con paginación"""
        start_time = time.time()
        
        # Intentar obtener del cache
        cached_builds = self.cache.get_cached_builds_by_type(build_type.value)
        if cached_builds:
            logger.debug(f"Cache HIT: get_builds_by_type({build_type.value})")
            builds = cached_builds
        else:
            logger.debug(f"Cache MISS: get_builds_by_type({build_type.value})")
            # Usar índice para búsqueda más rápida
            if build_type in self._type_index:
                build_indices = self._type_index[build_type]
                builds = [self.builds_cache[i] for i in build_indices]
            else:
                builds = []
            
            # Cachear resultado
            self.cache.cache_builds_by_type(build_type.value, builds)
        
        total = len(builds)
        
        # Aplicar paginación
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_builds_by_type({build_type.value}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_builds_by_difficulty(self, difficulty: str, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Obtener builds filtrados por dificultad con paginación"""
        start_time = time.time()
        
        # Intentar obtener del cache
        cached_builds = self.cache.get_cached_builds_by_difficulty(difficulty)
        if cached_builds:
            logger.debug(f"Cache HIT: get_builds_by_difficulty({difficulty})")
            builds = cached_builds
        else:
            logger.debug(f"Cache MISS: get_builds_by_difficulty({difficulty})")
            # Usar índice para búsqueda más rápida
            difficulty_enum = BuildDifficulty(difficulty)
            if difficulty_enum in self._difficulty_index:
                build_indices = self._difficulty_index[difficulty_enum]
                builds = [self.builds_cache[i] for i in build_indices]
            else:
                builds = []
            
            # Cachear resultado
            self.cache.cache_builds_by_difficulty(difficulty, builds)
        
        total = len(builds)
        
        # Aplicar paginación
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_builds_by_difficulty({difficulty}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def search_builds(self, query: str, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Buscar builds por nombre o descripción con paginación"""
        start_time = time.time()
        
        # Intentar obtener del cache
        cached_builds = self.cache.get_cached_search_results(query)
        if cached_builds:
            logger.debug(f"Cache HIT: search_builds({query})")
            builds = cached_builds
        else:
            logger.debug(f"Cache MISS: search_builds({query})")
            query_lower = query.lower()
            builds = []
            
            # Búsqueda optimizada usando índices cuando sea posible
            for build in self.builds_cache:
                if (query_lower in build.name.lower() or 
                    query_lower in build.description.lower()):
                    builds.append(build)
            
            # Cachear resultado (TTL más corto para búsquedas)
            self.cache.cache_search_results(query, builds, ttl=1800)
        
        total = len(builds)
        
        # Aplicar paginación
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"search_builds({query}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_filtered_builds(self, filters: FilterParams, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Obtener builds con filtros múltiples y paginación"""
        start_time = time.time()
        
        # Aplicar filtros secuencialmente para optimizar
        builds = self.builds_cache.copy()
        
        # Filtro por tipo
        if filters.build_type:
            build_type = BuildType(filters.build_type)
            builds = [b for b in builds if b.build_type == build_type]
        
        # Filtro por dificultad
        if filters.difficulty:
            difficulty = BuildDifficulty(filters.difficulty)
            builds = [b for b in builds if b.difficulty == difficulty]
        
        # Filtro por búsqueda
        if filters.search:
            query_lower = filters.search.lower()
            builds = [b for b in builds if 
                     query_lower in b.name.lower() or 
                     query_lower in b.description.lower()]
        
        # Ordenamiento
        if filters.sort_by:
            reverse = filters.sort_order == "desc"
            if filters.sort_by == "name":
                builds.sort(key=lambda x: x.name, reverse=reverse)
            elif filters.sort_by == "difficulty":
                builds.sort(key=lambda x: x.difficulty.value, reverse=reverse)
            elif filters.sort_by == "build_type":
                builds.sort(key=lambda x: x.build_type.value, reverse=reverse)
            elif filters.sort_by == "feudal_age_time":
                builds.sort(key=lambda x: x.feudal_age_time or 0, reverse=reverse)
            elif filters.sort_by == "castle_age_time":
                builds.sort(key=lambda x: x.castle_age_time or 0, reverse=reverse)
        
        total = len(builds)
        
        # Aplicar paginación
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_filtered_builds completed in {query_time:.2f}ms")
        
        return builds, total
    
    def update_cache(self, builds: List[Build]) -> None:
        """Actualizar la caché de builds y limpiar cache"""
        self.builds_cache = builds
        self._build_indexes()
        
        # Limpiar cache existente
        self.cache.invalidate_builds_cache()
        
        # Cachear nueva lista
        self.cache.cache_builds(builds)
        
        logger.info(f"Cache updated with {len(builds)} builds")


# Alias para compatibilidad hacia atrás
BuildRepository = OptimizedBuildRepository
