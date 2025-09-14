"""
Configuración de la base de datos y caché
"""

from typing import List
from app.models.build_models import Build
from app.services.scraping_service import ScrapingService
from app.repositories.build_repository import BuildRepository


class DatabaseConfig:
    """Configuración y gestión de la base de datos"""
    
    def __init__(self):
        self.scraping_service = ScrapingService()
        self.builds_cache: List[Build] = []
        self.repository: BuildRepository = None
    
    async def initialize(self) -> BuildRepository:
        """Inicializa la base de datos y retorna el repositorio"""
        # Cargar builds desde el scraping
        self.builds_cache = self.scraping_service.scrape_builds()
        
        # Crear repositorio
        self.repository = BuildRepository(self.builds_cache)
        
        return self.repository
    
    async def refresh_data(self) -> None:
        """Refresca los datos desde la fuente"""
        self.builds_cache = self.scraping_service.scrape_builds()
        if self.repository:
            self.repository.update_cache(self.builds_cache)
    
    def get_cache_size(self) -> int:
        """Retorna el tamaño de la caché"""
        return len(self.builds_cache)
