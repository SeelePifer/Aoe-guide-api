"""
API refactorizada con arquitectura en capas - Versión funcional
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.models.build_models import BuildType, BuildDifficulty
from app.services.build_service import BuildService
from app.repositories.build_repository import BuildRepository
from app.services.scraping_service import ScrapingService


def create_app() -> FastAPI:
    """Crea y configura la aplicación FastAPI"""
    
    # Crear aplicación FastAPI
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    return app


# Crear aplicación
app = create_app()

# Variables globales para los servicios
build_service = None
build_repository = None


@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    global build_service, build_repository
    
    print("Inicializando servicios...")
    
    # Inicializar scraping service
    scraping_service = ScrapingService()
    builds_cache = scraping_service.scrape_builds()
    
    # Inicializar repositorio
    build_repository = BuildRepository(builds_cache)
    
    # Inicializar servicio
    build_service = BuildService(build_repository)
    
    print(f"Servicios inicializados. {len(builds_cache)} builds cargados.")


# Endpoints de la API
@app.get("/")
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "AoE Build Guide API",
        "version": "1.0.0",
        "endpoints": {
            "all_builds": "/builds",
            "builds_by_type": "/builds/{build_type}",
            "build_guide": "/builds/{build_type}/guide",
            "builds_by_difficulty": "/builds/difficulty/{difficulty}",
            "search_builds": "/builds/search?q={query}",
            "build_types": "/builds/types",
            "difficulties": "/builds/difficulties"
        }
    }


@app.get("/builds", response_model=dict)
async def get_all_builds():
    """Obtener todos los builds disponibles"""
    if build_service is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    
    builds = await build_service.get_all_builds()
    return {
        "builds": [build.dict() for build in builds],
        "total": len(builds),
        "build_type": "all"
    }


@app.get("/builds/types", response_model=list)
async def get_build_types():
    """Obtener todos los tipos de builds disponibles"""
    return [build_type.value for build_type in BuildType]


@app.get("/builds/difficulties", response_model=list)
async def get_difficulties():
    """Obtener todas las dificultades disponibles"""
    return [difficulty.value for difficulty in BuildDifficulty]


@app.get("/builds/search", response_model=dict)
async def search_builds(q: str):
    """Buscar builds por nombre o descripción"""
    if build_service is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    
    builds = await build_service.search_builds(q)
    return {
        "builds": [build.dict() for build in builds],
        "total": len(builds),
        "build_type": "search"
    }


@app.get("/builds/{build_type}", response_model=dict)
async def get_builds_by_type(build_type: BuildType):
    """Obtener builds filtrados por tipo con pasos detallados"""
    if build_service is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    
    builds = await build_service.get_builds_by_type(build_type)
    return {
        "builds": [build.dict() for build in builds],
        "total": len(builds),
        "build_type": build_type.value
    }


@app.get("/builds/{build_type}/guide", response_model=dict)
async def get_build_guide(build_type: BuildType):
    """Obtener guía detallada paso a paso para un tipo de build específico"""
    if build_service is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    
    try:
        guide = await build_service.get_build_guide(build_type)
        return guide.dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/builds/difficulty/{difficulty}", response_model=dict)
async def get_builds_by_difficulty(difficulty: BuildDifficulty):
    """Obtener builds filtrados por dificultad"""
    if build_service is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    
    builds = await build_service.get_builds_by_difficulty(difficulty.value)
    return {
        "builds": [build.dict() for build in builds],
        "total": len(builds),
        "build_type": "all"
    }


@app.post("/builds/refresh")
async def refresh_builds():
    """Refrescar la caché de builds desde la fuente"""
    if build_repository is None:
        raise HTTPException(status_code=503, detail="Servicio no inicializado")
    
    # Refrescar datos
    scraping_service = ScrapingService()
    new_builds = scraping_service.scrape_builds()
    build_repository.update_cache(new_builds)
    
    return {
        "message": "Builds actualizados correctamente", 
        "total": len(new_builds)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_refactored:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
