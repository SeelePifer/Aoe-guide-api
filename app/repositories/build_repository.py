"""
Optimized repository for build data access with cache and pagination
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
    """Interface for build repository"""
    
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
    """Optimized repository with cache and pagination"""
    
    def __init__(self, builds_cache: List[Build]):
        self.builds_cache = builds_cache
        self.cache = build_cache
        self._build_indexes()
    
    def _build_indexes(self):
        """Build indexes for faster searches"""
        self._type_index = {}
        self._difficulty_index = {}
        self._name_index = {}
        
        for i, build in enumerate(self.builds_cache):
            # Index by type
            if build.build_type not in self._type_index:
                self._type_index[build.build_type] = []
            self._type_index[build.build_type].append(i)
            
            # Index by difficulty
            if build.difficulty not in self._difficulty_index:
                self._difficulty_index[build.difficulty] = []
            self._difficulty_index[build.difficulty].append(i)
            
            # Index by name (for searches)
            self._name_index[build.name.lower()] = i
    
    async def get_all_builds(self, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Get all available builds with pagination"""
        start_time = time.time()
        
        # Try to get from cache
        cached_builds = self.cache.get_cached_builds()
        if cached_builds:
            logger.debug("Cache HIT: get_all_builds")
            builds = cached_builds
        else:
            logger.debug("Cache MISS: get_all_builds")
            builds = self.builds_cache
            # Cache for future queries
            self.cache.cache_builds(builds)
        
        total = len(builds)
        
        # Apply pagination
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_all_builds completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_builds_by_type(self, build_type: BuildType, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Get builds filtered by type with pagination"""
        start_time = time.time()
        
        # Try to get from cache
        cached_builds = self.cache.get_cached_builds_by_type(build_type.value)
        if cached_builds:
            logger.debug(f"Cache HIT: get_builds_by_type({build_type.value})")
            builds = cached_builds
        else:
            logger.debug(f"Cache MISS: get_builds_by_type({build_type.value})")
            # Use index for faster search
            if build_type in self._type_index:
                build_indices = self._type_index[build_type]
                builds = [self.builds_cache[i] for i in build_indices]
            else:
                builds = []
            
            # Cache result
            self.cache.cache_builds_by_type(build_type.value, builds)
        
        total = len(builds)
        
        # Apply pagination
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_builds_by_type({build_type.value}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_builds_by_difficulty(self, difficulty: str, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Get builds filtered by difficulty with pagination"""
        start_time = time.time()
        
        # Try to get from cache
        cached_builds = self.cache.get_cached_builds_by_difficulty(difficulty)
        if cached_builds:
            logger.debug(f"Cache HIT: get_builds_by_difficulty({difficulty})")
            builds = cached_builds
        else:
            logger.debug(f"Cache MISS: get_builds_by_difficulty({difficulty})")
            # Use index for faster search
            difficulty_enum = BuildDifficulty(difficulty)
            if difficulty_enum in self._difficulty_index:
                build_indices = self._difficulty_index[difficulty_enum]
                builds = [self.builds_cache[i] for i in build_indices]
            else:
                builds = []
            
            # Cache result
            self.cache.cache_builds_by_difficulty(difficulty, builds)
        
        total = len(builds)
        
        # Apply pagination
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_builds_by_difficulty({difficulty}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def search_builds(self, query: str, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Search builds by name or description with pagination"""
        start_time = time.time()
        
        # Try to get from cache
        cached_builds = self.cache.get_cached_search_results(query)
        if cached_builds:
            logger.debug(f"Cache HIT: search_builds({query})")
            builds = cached_builds
        else:
            logger.debug(f"Cache MISS: search_builds({query})")
            query_lower = query.lower()
            builds = []
            
            # Optimized search using indexes when possible
            for build in self.builds_cache:
                if (query_lower in build.name.lower() or 
                    query_lower in build.description.lower()):
                    builds.append(build)
            
            # Cache result (shorter TTL for searches)
            self.cache.cache_search_results(query, builds, ttl=1800)
        
        total = len(builds)
        
        # Apply pagination
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"search_builds({query}) completed in {query_time:.2f}ms")
        
        return builds, total
    
    async def get_filtered_builds(self, filters: FilterParams, pagination: Optional[PaginationParams] = None) -> Tuple[List[Build], int]:
        """Get builds with multiple filters and pagination"""
        start_time = time.time()
        
        # Apply filters sequentially to optimize
        builds = self.builds_cache.copy()
        
        # Filter by type
        if filters.build_type:
            build_type = BuildType(filters.build_type)
            builds = [b for b in builds if b.build_type == build_type]
        
        # Filter by difficulty
        if filters.difficulty:
            difficulty = BuildDifficulty(filters.difficulty)
            builds = [b for b in builds if b.difficulty == difficulty]
        
        # Filter by search
        if filters.search:
            query_lower = filters.search.lower()
            builds = [b for b in builds if 
                     query_lower in b.name.lower() or 
                     query_lower in b.description.lower()]
        
        # Sorting
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
        
        # Apply pagination
        if pagination:
            start = pagination.offset
            end = start + pagination.size
            builds = builds[start:end]
        
        query_time = (time.time() - start_time) * 1000
        logger.debug(f"get_filtered_builds completed in {query_time:.2f}ms")
        
        return builds, total
    
    def update_cache(self, builds: List[Build]) -> None:
        """Update builds cache and clear cache"""
        self.builds_cache = builds
        self._build_indexes()
        
        # Clear existing cache
        self.cache.invalidate_builds_cache()
        
        # Cache new list
        self.cache.cache_builds(builds)
        
        logger.info(f"Cache updated with {len(builds)} builds")


# Alias for backward compatibility
BuildRepository = OptimizedBuildRepository
