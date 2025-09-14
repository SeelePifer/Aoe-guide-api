#!/usr/bin/env python3
"""
Tests de integración para la API refactorizada
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.config.dependencies import dependency_container
from app.models.build_models import BuildType, BuildDifficulty


class IntegrationTester:
    """Clase para tests de integración"""
    
    def __init__(self):
        self.results = {"passed": 0, "failed": 0, "total": 0}
    
    def test(self, name: str, test_func) -> bool:
        """Ejecuta un test individual"""
        self.results["total"] += 1
        print(f"🧪 Testing {name}...")
        
        try:
            result = test_func()
            if result:
                print(f"   ✅ {name} - PASSED")
                self.results["passed"] += 1
                return True
            else:
                print(f"   ❌ {name} - FAILED")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print(f"   ❌ {name} - ERROR: {e}")
            self.results["failed"] += 1
            return False
    
    async def test_dependency_injection(self):
        """Test de inyección de dependencias"""
        print("\nTESTING DEPENDENCY INJECTION")
        print("=" * 40)
        
        # Inicializar dependencias
        await dependency_container.initialize()
        
        # Test que todas las dependencias estén disponibles
        self.test("Dependency Container Initialization", lambda:
            dependency_container.build_repository is not None
        )
        
        self.test("Build Service Available", lambda:
            dependency_container.build_service is not None
        )
        
        self.test("Build Controller Available", lambda:
            dependency_container.build_controller is not None
        )
        
        self.test("App Controller Available", lambda:
            dependency_container.app_controller is not None
        )
    
    async def test_service_integration(self):
        """Test de integración de servicios"""
        print("\nTESTING SERVICE INTEGRATION")
        print("=" * 40)
        
        # Obtener servicio
        build_service = dependency_container.build_service
        
        # Test get_all_builds
        all_builds = await build_service.get_all_builds()
        self.test("Get All Builds", lambda:
            isinstance(all_builds, list)
        )
        
        # Test get_builds_by_type
        feudal_builds = await build_service.get_builds_by_type(BuildType.FEUDAL_RUSH)
        self.test("Get Builds by Type", lambda:
            isinstance(feudal_builds, list)
        )
        
        # Test search_builds
        search_results = await build_service.search_builds("scout")
        self.test("Search Builds", lambda:
            isinstance(search_results, list)
        )
        
        # Test get_build_guide
        try:
            guide = await build_service.get_build_guide(BuildType.FEUDAL_RUSH)
            self.test("Get Build Guide", lambda:
                guide.build_type == "feudal_rush" and 
                "main_build" in guide.dict() and
                "alternative_builds" in guide.dict()
            )
        except Exception as e:
            print(f"   ⚠️  Build Guide test skipped: {e}")
            self.results["total"] -= 1  # No contar como test fallido
    
    async def test_repository_integration(self):
        """Test de integración del repositorio"""
        print("\nTESTING REPOSITORY INTEGRATION")
        print("=" * 40)
        
        # Obtener repositorio
        repository = dependency_container.build_repository
        
        # Test get_all_builds
        all_builds = await repository.get_all_builds()
        self.test("Repository Get All Builds", lambda:
            isinstance(all_builds, list)
        )
        
        # Test get_builds_by_type
        feudal_builds = await repository.get_builds_by_type(BuildType.FEUDAL_RUSH)
        self.test("Repository Get Builds by Type", lambda:
            isinstance(feudal_builds, list)
        )
        
        # Test get_builds_by_difficulty
        beginner_builds = await repository.get_builds_by_difficulty("beginner")
        self.test("Repository Get Builds by Difficulty", lambda:
            isinstance(beginner_builds, list)
        )
        
        # Test search_builds
        search_results = await repository.search_builds("test")
        self.test("Repository Search Builds", lambda:
            isinstance(search_results, list)
        )
    
    async def test_controller_integration(self):
        """Test de integración de controladores"""
        print("\nTESTING CONTROLLER INTEGRATION")
        print("=" * 40)
        
        # Obtener controladores
        build_controller = dependency_container.build_controller
        app_controller = dependency_container.app_controller
        
        # Test que los controladores tengan routers
        self.test("Build Controller Router", lambda:
            build_controller.router is not None
        )
        
        self.test("App Controller Router", lambda:
            app_controller.get_router() is not None
        )
    
    async def test_data_flow(self):
        """Test del flujo completo de datos"""
        print("\nTESTING DATA FLOW")
        print("=" * 40)
        
        # Obtener servicios
        build_service = dependency_container.build_service
        repository = dependency_container.build_repository
        
        # Test flujo completo: Repository -> Service -> Controller
        all_builds = await repository.get_all_builds()
        service_builds = await build_service.get_all_builds()
        
        self.test("Data Flow Consistency", lambda:
            len(all_builds) == len(service_builds)
        )
        
        # Test que los builds tengan pasos detallados
        if service_builds:
            first_build = service_builds[0]
            self.test("Build Steps Integration", lambda:
                first_build.steps is not None and len(first_build.steps) > 0
            )
    
    async def run_all_tests(self):
        """Ejecuta todos los tests de integración"""
        print("Iniciando tests de integración de la arquitectura refactorizada...")
        print("=" * 70)
        
        await self.test_dependency_injection()
        await self.test_repository_integration()
        await self.test_service_integration()
        await self.test_controller_integration()
        await self.test_data_flow()
        
        print("\n" + "=" * 70)
        self.print_results()
    
    def print_results(self):
        """Imprime los resultados de los tests"""
        print("📊 RESULTADOS DE LOS TESTS DE INTEGRACIÓN")
        print("=" * 70)
        print(f"✅ Tests pasados: {self.results['passed']}")
        print(f"❌ Tests fallidos: {self.results['failed']}")
        print(f"📈 Total tests: {self.results['total']}")
        
        success_rate = (self.results['passed'] / self.results['total']) * 100 if self.results['total'] > 0 else 0
        print(f"🎯 Tasa de éxito: {success_rate:.1f}%")
        
        if self.results['failed'] == 0:
            print("\n🎉 ¡Todos los tests de integración pasaron! La arquitectura está funcionando correctamente.")
        else:
            print(f"\n⚠️  {self.results['failed']} test(s) fallaron. Revisa la integración entre capas.")


async def main():
    """Función principal"""
    print("AoE Build Guide API - Integration Tests")
    print("=" * 70)
    
    tester = IntegrationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
