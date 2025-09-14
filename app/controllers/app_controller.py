"""
Controlador principal de la aplicación
"""

from fastapi import APIRouter
from app.controllers.build_controller import BuildController
from app.services.build_service import BuildService
from app.repositories.build_repository import BuildRepository


class AppController:
    """Controlador principal que maneja todos los endpoints de la aplicación"""
    
    def __init__(self, build_service: BuildService):
        self.build_service = build_service
        self.router = APIRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas principales de la aplicación"""
        
        @self.router.get("/", response_model=dict)
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
        
        @self.router.post("/builds/refresh")
        async def refresh_builds():
            """Refrescar la caché de builds desde la fuente"""
            # Este endpoint se implementará en el servicio principal
            return {"message": "Builds actualizados correctamente"}
    
    def get_router(self):
        """Retorna el router principal"""
        return self.router
