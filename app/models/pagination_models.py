"""
Models for pagination and performance filters
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Any, Dict
from math import ceil


class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number (starting from 1)")
    size: int = Field(default=10, ge=1, le=100, description="Page size (maximum 100)")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be greater than 0')
        return v
    
    @validator('size')
    def validate_size(cls, v):
        if v < 1:
            raise ValueError('Size must be greater than 0')
        if v > 100:
            raise ValueError('Size cannot exceed 100')
        return v
    
    @property
    def offset(self) -> int:
        """Calcula el offset para la consulta"""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """Respuesta paginada"""
    data: List[Any]
    pagination: Dict[str, Any]
    
    @classmethod
    def create(
        cls,
        data: List[Any],
        total: int,
        page: int,
        size: int,
        build_type: str = "all"
    ) -> 'PaginatedResponse':
        """Crea una respuesta paginada"""
        total_pages = ceil(total / size) if total > 0 else 1
        
        pagination_info = {
            "page": page,
            "size": size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None
        }
        
        return cls(
            data=data,
            pagination=pagination_info
        )


class FilterParams(BaseModel):
    """Parámetros de filtrado para optimizar consultas"""
    build_type: Optional[str] = Field(default=None, description="Filtrar por tipo de build")
    difficulty: Optional[str] = Field(default=None, description="Filtrar por dificultad")
    search: Optional[str] = Field(default=None, description="Búsqueda de texto")
    sort_by: Optional[str] = Field(default="name", description="Campo para ordenar")
    sort_order: Optional[str] = Field(default="asc", description="Orden: asc o desc")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be "asc" or "desc"')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ['name', 'difficulty', 'build_type', 'feudal_age_time', 'castle_age_time']
        if v not in allowed_fields:
            raise ValueError(f'Sort by must be one of: {", ".join(allowed_fields)}')
        return v


class PerformanceMetrics(BaseModel):
    """Métricas de rendimiento"""
    response_time_ms: float
    cache_hit: bool
    total_items: int
    items_returned: int
    query_time_ms: float
    cache_time_ms: float = 0.0


class OptimizedBuildResponse(BaseModel):
    """Respuesta optimizada de builds con métricas"""
    builds: List[Any]
    pagination: Dict[str, Any]
    performance: PerformanceMetrics
    build_type: str
