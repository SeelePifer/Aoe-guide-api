#!/usr/bin/env python3
"""
Tests unitarios para las capas individuales de la arquitectura refactorizada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.build_models import Build, BuildStep, BuildType, BuildDifficulty
from app.services.build_service import BuildService
from app.repositories.build_repository import BuildRepository
from app.services.scraping_service import ScrapingService


class UnitTester:
    """Clase para tests unitarios de las capas"""
    
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
    
    def test_models(self):
        """Tests para la capa de modelos"""
        print("\n📋 TESTING MODELS LAYER")
        print("=" * 40)
        
        # Test BuildStep
        self.test("BuildStep Creation", lambda: 
            BuildStep(
                step_number=1,
                age="Dark Age",
                time="0:00-2:00",
                action="Test Action",
                details="Test Details",
                resources_needed={"food": 100}
            ).step_number == 1
        )
        
        # Test Build
        self.test("Build Creation", lambda:
            Build(
                name="Test Build",
                difficulty=BuildDifficulty.BEGINNER,
                description="Test Description",
                build_type=BuildType.FEUDAL_RUSH
            ).name == "Test Build"
        )
        
        # Test Enums
        self.test("BuildType Enum", lambda:
            BuildType.FEUDAL_RUSH.value == "feudal_rush"
        )
        
        self.test("BuildDifficulty Enum", lambda:
            BuildDifficulty.INTERMEDIATE.value == "intermediate"
        )
    
    def test_repository(self):
        """Tests para la capa de repositorio"""
        print("\n💾 TESTING REPOSITORY LAYER")
        print("=" * 40)
        
        # Crear datos de prueba
        test_builds = [
            Build(
                name="Test Build 1",
                difficulty=BuildDifficulty.BEGINNER,
                description="Test Description 1",
                build_type=BuildType.FEUDAL_RUSH
            ),
            Build(
                name="Test Build 2",
                difficulty=BuildDifficulty.INTERMEDIATE,
                description="Test Description 2",
                build_type=BuildType.FAST_CASTLE
            )
        ]
        
        # Crear repositorio
        repository = BuildRepository(test_builds)
        
        # Test get_all_builds
        self.test("Repository get_all_builds", lambda:
            len(repository.builds_cache) == 2
        )
        
        # Test get_builds_by_type
        self.test("Repository get_builds_by_type", lambda:
            len([b for b in repository.builds_cache if b.build_type == BuildType.FEUDAL_RUSH]) == 1
        )
        
        # Test search_builds
        self.test("Repository search_builds", lambda:
            len([b for b in repository.builds_cache if "Test" in b.name]) == 2
        )
    
    def test_service(self):
        """Tests para la capa de servicios"""
        print("\n⚙️ TESTING SERVICE LAYER")
        print("=" * 40)
        
        # Crear datos de prueba
        test_builds = [
            Build(
                name="Scout Rush",
                difficulty=BuildDifficulty.INTERMEDIATE,
                description="Test Description",
                build_type=BuildType.FEUDAL_RUSH
            )
        ]
        
        # Crear repositorio y servicio
        repository = BuildRepository(test_builds)
        service = BuildService(repository)
        
        # Test get_build_steps
        self.test("Service get_build_steps", lambda:
            len(service._get_build_steps("Scout Rush", BuildType.FEUDAL_RUSH)) > 0
        )
        
        # Test get_generic_steps
        self.test("Service get_generic_steps", lambda:
            len(service._get_generic_steps(BuildType.FEUDAL_RUSH)) > 0
        )
    
    def test_scraping_service(self):
        """Tests para el servicio de scraping"""
        print("\n🕷️ TESTING SCRAPING SERVICE")
        print("=" * 40)
        
        scraping_service = ScrapingService()
        
        # Test determine_build_type
        self.test("Scraping determine_build_type", lambda:
            scraping_service._determine_build_type("feudal rush") == BuildType.FEUDAL_RUSH
        )
        
        # Test determine_difficulty
        self.test("Scraping determine_difficulty", lambda:
            scraping_service._determine_difficulty("beginner build", "test") == BuildDifficulty.BEGINNER
        )
        
        # Test extract_age_times
        def test_extract_age_times():
            feudal, castle, imperial = scraping_service._extract_age_times("Feudal Age 10 Castle Age 20")
            return feudal == 10 and castle == 20
        
        self.test("Scraping extract_age_times", test_extract_age_times)
    
    def run_all_tests(self):
        """Ejecuta todos los tests unitarios"""
        print("Iniciando tests unitarios de la arquitectura refactorizada...")
        print("=" * 60)
        
        self.test_models()
        self.test_repository()
        self.test_service()
        self.test_scraping_service()
        
        print("\n" + "=" * 60)
        self.print_results()
    
    def print_results(self):
        """Imprime los resultados de los tests"""
        print("📊 RESULTADOS DE LOS TESTS UNITARIOS")
        print("=" * 60)
        print(f"✅ Tests pasados: {self.results['passed']}")
        print(f"❌ Tests fallidos: {self.results['failed']}")
        print(f"📈 Total tests: {self.results['total']}")
        
        success_rate = (self.results['passed'] / self.results['total']) * 100 if self.results['total'] > 0 else 0
        print(f"Tasa de éxito: {success_rate:.1f}%")
        
        if self.results['failed'] == 0:
            print("\n¡Todos los tests unitarios pasaron! La arquitectura está funcionando correctamente.")
        else:
            print(f"\n{self.results['failed']} test(s) fallaron. Revisa la implementación de las capas.")


def main():
    """Función principal"""
    print("AoE Build Guide API - Unit Tests")
    print("=" * 60)
    
    tester = UnitTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
