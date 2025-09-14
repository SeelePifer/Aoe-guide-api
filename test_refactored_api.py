#!/usr/bin/env python3
"""
Test script completo para la API refactorizada con arquitectura en capas
"""

import requests
import json
import time
import sys
from typing import Dict, Any


class APITester:
    """Clase para probar la API refactorizada"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "passed": 0,
            "failed": 0,
            "total": 0
        }
    
    def test_endpoint(self, name: str, method: str, endpoint: str, expected_status: int = 200) -> bool:
        """Test individual de un endpoint"""
        self.results["total"] += 1
        
        try:
            url = f"{self.base_url}{endpoint}"
            print(f"🧪 Testing {name}...")
            print(f"   {method.upper()} {endpoint}")
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, timeout=10)
            else:
                print(f"   ❌ Método no soportado: {method}")
                self.results["failed"] += 1
                return False
            
            if response.status_code == expected_status:
                print(f"   ✅ Status: {response.status_code}")
                self.results["passed"] += 1
                return True
            else:
                print(f"   ❌ Status: {response.status_code} (esperado: {expected_status})")
                self.results["failed"] += 1
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Error de conexión - ¿Está la API ejecutándose?")
            self.results["failed"] += 1
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results["failed"] += 1
            return False
    
    def test_endpoint_with_data(self, name: str, method: str, endpoint: str, expected_data: Dict[str, Any]) -> bool:
        """Test de endpoint con validación de datos"""
        self.results["total"] += 1
        
        try:
            url = f"{self.base_url}{endpoint}"
            print(f"🧪 Testing {name}...")
            print(f"   {method.upper()} {endpoint}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validar estructura de datos
                valid = True
                for key, expected_type in expected_data.items():
                    if key not in data:
                        print(f"   ❌ Campo faltante: {key}")
                        valid = False
                    elif not isinstance(data[key], expected_type):
                        print(f"   ❌ Tipo incorrecto para {key}: {type(data[key])} (esperado: {expected_type})")
                        valid = False
                
                if valid:
                    print(f"   ✅ Status: {response.status_code} - Datos válidos")
                    self.results["passed"] += 1
                    return True
                else:
                    print(f"   ❌ Datos inválidos")
                    self.results["failed"] += 1
                    return False
            else:
                print(f"   ❌ Status: {response.status_code}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results["failed"] += 1
            return False
    
    def test_build_guide_endpoint(self) -> bool:
        """Test específico para el endpoint de guías de build"""
        self.results["total"] += 1
        
        try:
            url = f"{self.base_url}/builds/feudal_rush/guide"
            print(f"🧪 Testing Build Guide Endpoint...")
            print(f"   GET /builds/feudal_rush/guide")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Validar estructura de la guía
                required_fields = ["build_type", "main_build", "alternative_builds", "total_available"]
                valid = all(field in data for field in required_fields)
                
                if valid and "steps" in data["main_build"]:
                    steps = data["main_build"]["steps"]
                    if len(steps) > 0:
                        print(f"   ✅ Status: {response.status_code}")
                        print(f"   ✅ Build Type: {data['build_type']}")
                        print(f"   ✅ Main Build: {data['main_build']['name']}")
                        print(f"   ✅ Total Steps: {len(steps)}")
                        print(f"   ✅ Alternative Builds: {len(data['alternative_builds'])}")
                        
                        # Mostrar primer paso como ejemplo
                        if steps:
                            first_step = steps[0]
                            print(f"   ✅ Primer paso: {first_step['action']} ({first_step['age']})")
                        
                        self.results["passed"] += 1
                        return True
                    else:
                        print(f"   ❌ No hay pasos en la guía")
                        self.results["failed"] += 1
                        return False
                else:
                    print(f"   ❌ Estructura de datos inválida")
                    self.results["failed"] += 1
                    return False
            else:
                print(f"   ❌ Status: {response.status_code}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.results["failed"] += 1
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests"""
        print("🚀 Iniciando tests de la API refactorizada...")
        print("=" * 60)
        
        # Test 1: Endpoint raíz
        self.test_endpoint("Root Endpoint", "GET", "/")
        
        # Test 2: Obtener todos los builds
        self.test_endpoint_with_data(
            "All Builds", 
            "GET", 
            "/builds", 
            {"builds": list, "total": int, "build_type": str}
        )
        
        # Test 3: Tipos de builds
        self.test_endpoint_with_data(
            "Build Types", 
            "GET", 
            "/builds/types", 
            {}
        )
        
        # Test 4: Dificultades
        self.test_endpoint_with_data(
            "Difficulties", 
            "GET", 
            "/builds/difficulties", 
            {}
        )
        
        # Test 5: Builds por tipo
        self.test_endpoint_with_data(
            "Builds by Type", 
            "GET", 
            "/builds/feudal_rush", 
            {"builds": list, "total": int, "build_type": str}
        )
        
        # Test 6: Búsqueda de builds
        self.test_endpoint_with_data(
            "Search Builds", 
            "GET", 
            "/builds/search?q=scout", 
            {"builds": list, "total": int, "build_type": str}
        )
        
        # Test 7: Guía de build (test específico)
        self.test_build_guide_endpoint()
        
        # Test 8: Builds por dificultad
        self.test_endpoint_with_data(
            "Builds by Difficulty", 
            "GET", 
            "/builds/difficulty/beginner", 
            {"builds": list, "total": int, "build_type": str}
        )
        
        print("\n" + "=" * 60)
        self.print_results()
    
    def print_results(self):
        """Imprime los resultados de los tests"""
        print("📊 RESULTADOS DE LOS TESTS")
        print("=" * 60)
        print(f"✅ Tests pasados: {self.results['passed']}")
        print(f"❌ Tests fallidos: {self.results['failed']}")
        print(f"📈 Total tests: {self.results['total']}")
        
        success_rate = (self.results['passed'] / self.results['total']) * 100 if self.results['total'] > 0 else 0
        print(f"🎯 Tasa de éxito: {success_rate:.1f}%")
        
        if self.results['failed'] == 0:
            print("\n🎉 ¡Todos los tests pasaron! La API refactorizada funciona correctamente.")
        else:
            print(f"\n⚠️  {self.results['failed']} test(s) fallaron. Revisa la configuración de la API.")


def check_api_availability(base_url: str = "http://localhost:8000") -> bool:
    """Verifica si la API está disponible"""
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Función principal"""
    print("🔧 AoE Build Guide API - Test Suite")
    print("=" * 60)
    
    # Verificar disponibilidad de la API
    if not check_api_availability():
        print("❌ La API no está disponible en http://localhost:8000")
        print("\n📋 Para ejecutar la API refactorizada:")
        print("   python main_refactored.py")
        print("\n📋 Para ejecutar la API original:")
        print("   python main.py")
        print("\n⏳ Esperando 5 segundos antes de continuar...")
        time.sleep(5)
    
    # Crear tester y ejecutar tests
    tester = APITester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
