"""
API optimizada con mejoras de rendimiento
"""

import asyncio
import logging
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.config.settings import settings
from app.models.build_models import BuildType, BuildDifficulty
from app.models.pagination_models import PaginationParams, FilterParams, PaginatedResponse
from app.services.build_service import OptimizedBuildService
from app.repositories.build_repository import OptimizedBuildRepository
from app.services.scraping_service import OptimizedScrapingService
from app.middleware.performance import PerformanceMiddleware, CacheHeadersMiddleware, RequestLoggingMiddleware
from app.config.cache import cache_manager

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_optimized_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI optimizada"""
    
    # Crear aplicación FastAPI
    app = FastAPI(
        title=f"{settings.app_name} - Optimized",
        description=f"{settings.app_description} - Versión optimizada con mejoras de rendimiento",
        version="2.0.0"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # Agregar middleware de rendimiento
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(CacheHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    
    # Agregar compresión
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    return app


# Crear aplicación
app = create_optimized_app()

# Variables globales para los servicios
build_service = None
build_repository = None


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    global build_service, build_repository
    
    logger.info("🚀 Inicializando servicios optimizados...")
    
    # Inicializar scraping service asíncrono
    scraping_service = OptimizedScrapingService()
    builds_cache = await scraping_service.scrape_builds()
    
    # Inicializar repositorio optimizado
    build_repository = OptimizedBuildRepository(builds_cache)
    
    # Inicializar servicio optimizado
    build_service = OptimizedBuildService(build_repository)
    
    # Limpiar cache expirado
    cache_manager.clear_expired()
    
    logger.info(f"✅ Servicios optimizados inicializados. {len(builds_cache)} builds cargados.")


# Dependency para obtener el servicio
def get_build_service() -> OptimizedBuildService:
    if build_service is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    return build_service


# Dependency para paginación
def get_pagination_params(
    page: int = Query(1, ge=1, description="Número de página"),
    size: int = Query(10, ge=1, le=100, description="Tamaño de página")
) -> PaginationParams:
    return PaginationParams(page=page, size=size)


# Dependency para filtros
def get_filter_params(
    build_type: str = Query(None, description="Filtrar por tipo de build"),
    difficulty: str = Query(None, description="Filtrar por dificultad"),
    search: str = Query(None, description="Búsqueda de texto"),
    sort_by: str = Query("name", description="Campo para ordenar"),
    sort_order: str = Query("asc", description="Orden: asc o desc")
) -> FilterParams:
    return FilterParams(
        build_type=build_type,
        difficulty=difficulty,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )


# Endpoints optimizados
@app.get("/")
async def root():
    """Endpoint raíz con información de la API optimizada"""
    cache_stats = cache_manager.get_stats()
    
    return {
        "message": "AoE Build Guide API - Optimized",
        "version": "2.0.0",
        "features": [
            "Cache persistente",
            "Paginación",
            "Compresión gzip",
            "Scraping asíncrono",
            "Índices optimizados",
            "Métricas de rendimiento"
        ],
        "cache_stats": cache_stats,
        "endpoints": {
            "all_builds": "/builds",
            "builds_by_type": "/builds/{build_type}",
            "build_guide": "/builds/{build_type}/guide",
            "builds_by_difficulty": "/builds/difficulty/{difficulty}",
            "search_builds": "/builds/search",
            "filtered_builds": "/builds/filter",
            "build_types": "/builds/types",
            "difficulties": "/builds/difficulties",
            "cache_stats": "/cache/stats",
            "refresh_cache": "/builds/refresh"
        }
    }


@app.get("/builds", response_model=PaginatedResponse)
async def get_all_builds(
    pagination: PaginationParams = Depends(get_pagination_params),
    service: OptimizedBuildService = Depends(get_build_service)
):
    """Obtener todos los builds disponibles con paginación"""
    builds, total = await service.get_all_builds(pagination)
    
    return PaginatedResponse.create(
        data=[build.dict() for build in builds],
        total=total,
        page=pagination.page,
        size=pagination.size,
        build_type="all"
    )


@app.get("/builds/filter", response_model=PaginatedResponse)
async def get_filtered_builds(
    filters: FilterParams = Depends(get_filter_params),
    pagination: PaginationParams = Depends(get_pagination_params),
    service: OptimizedBuildService = Depends(get_build_service)
):
    """Obtener builds con filtros múltiples y paginación"""
    builds, total = await service.get_filtered_builds(filters, pagination)
    
    return PaginatedResponse.create(
        data=[build.dict() for build in builds],
        total=total,
        page=pagination.page,
        size=pagination.size,
        build_type=filters.build_type or "all"
    )


@app.get("/builds/types", response_model=list)
async def get_build_types():
    """Obtener todos los tipos de builds disponibles"""
    return [build_type.value for build_type in BuildType]


@app.get("/builds/difficulties", response_model=list)
async def get_difficulties():
    """Obtener todas las dificultades disponibles"""
    return [difficulty.value for difficulty in BuildDifficulty]


@app.get("/builds/search", response_model=PaginatedResponse)
async def search_builds(
    q: str = Query(..., description="Término de búsqueda"),
    pagination: PaginationParams = Depends(get_pagination_params),
    service: OptimizedBuildService = Depends(get_build_service)
):
    """Buscar builds por nombre o descripción con paginación"""
    builds, total = await service.search_builds(q, pagination)
    
    return PaginatedResponse.create(
        data=[build.dict() for build in builds],
        total=total,
        page=pagination.page,
        size=pagination.size,
        build_type="search"
    )


@app.get("/builds/{build_type}", response_model=PaginatedResponse)
async def get_builds_by_type(
    build_type: BuildType,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: OptimizedBuildService = Depends(get_build_service)
):
    """Obtener builds filtrados por tipo con paginación"""
    builds, total = await service.get_builds_by_type(build_type, pagination)
    
    return PaginatedResponse.create(
        data=[build.dict() for build in builds],
        total=total,
        page=pagination.page,
        size=pagination.size,
        build_type=build_type.value
    )


@app.get("/builds/{build_type}/guide", response_model=dict)
async def get_build_guide(
    build_type: BuildType,
    service: OptimizedBuildService = Depends(get_build_service)
):
    """Obtener guía detallada paso a paso para un tipo de build específico"""
    try:
        guide = await service.get_build_guide(build_type)
        return guide.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/builds/difficulty/{difficulty}", response_model=PaginatedResponse)
async def get_builds_by_difficulty(
    difficulty: BuildDifficulty,
    pagination: PaginationParams = Depends(get_pagination_params),
    service: OptimizedBuildService = Depends(get_build_service)
):
    """Obtener builds filtrados por dificultad con paginación"""
    builds, total = await service.get_builds_by_difficulty(difficulty.value, pagination)
    
    return PaginatedResponse.create(
        data=[build.dict() for build in builds],
        total=total,
        page=pagination.page,
        size=pagination.size,
        build_type="all"
    )


@app.get("/cache/stats")
async def get_cache_stats():
    """Obtener estadísticas del cache"""
    stats = cache_manager.get_stats()
    return {
        "cache_stats": stats,
        "message": "Estadísticas del cache obtenidas correctamente"
    }


@app.post("/builds/refresh")
async def refresh_builds():
    """Refrescar la caché de builds desde la fuente"""
    if build_repository is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    
    logger.info("🔄 Refrescando cache de builds...")
    
    # Refrescar datos con scraping asíncrono
    scraping_service = OptimizedScrapingService()
    new_builds = await scraping_service.scrape_builds()
    build_repository.update_cache(new_builds)
    
    # Limpiar cache expirado
    expired_count = cache_manager.clear_expired()
    
    return {
        "message": "Builds actualizados correctamente",
        "total": len(new_builds),
        "expired_cleared": expired_count,
        "cache_stats": cache_manager.get_stats()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "services": {
            "build_service": build_service is not None,
            "build_repository": build_repository is not None,
            "cache": cache_manager is not None
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_optimized:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
