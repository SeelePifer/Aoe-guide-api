"""
Configuración de dependencias e inyección de dependencias
"""

from app.services.build_service import BuildService
from app.repositories.build_repository import BuildRepository
from app.controllers.build_controller import BuildController
from app.controllers.app_controller import AppController
from app.config.database import DatabaseConfig


class DependencyContainer:
    """Contenedor de dependencias para inyección"""
    
    def __init__(self):
        self._build_repository: BuildRepository = None
        self._build_service: BuildService = None
        self._build_controller: BuildController = None
        self._app_controller: AppController = None
        self._database_config: DatabaseConfig = None
    
    async def initialize(self):
        """Inicializa todas las dependencias"""
        # Inicializar configuración de base de datos
        self._database_config = DatabaseConfig()
        self._build_repository = await self._database_config.initialize()
        
        # Inicializar servicios
        self._build_service = BuildService(self._build_repository)
        
        # Inicializar controladores
        self._build_controller = BuildController(self._build_service)
        self._app_controller = AppController(self._build_service)
    
    @property
    def build_repository(self) -> BuildRepository:
        """Retorna el repositorio de builds"""
        return self._build_repository
    
    @property
    def build_service(self) -> BuildService:
        """Retorna el servicio de builds"""
        return self._build_service
    
    @property
    def build_controller(self) -> BuildController:
        """Retorna el controlador de builds"""
        return self._build_controller
    
    @property
    def app_controller(self) -> AppController:
        """Retorna el controlador principal"""
        return self._app_controller
    
    @property
    def database_config(self) -> DatabaseConfig:
        """Retorna la configuración de base de datos"""
        return self._database_config


# Instancia global del contenedor de dependencias
dependency_container = DependencyContainer()
