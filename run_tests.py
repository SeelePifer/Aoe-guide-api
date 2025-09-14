#!/usr/bin/env python3
"""
Script maestro para ejecutar todos los tests de la API refactorizada
"""

import subprocess
import sys
import time
import os
from pathlib import Path


class TestRunner:
    """Ejecutor de tests para la API refactorizada"""
    
    def __init__(self):
        self.test_results = {}
        self.api_process = None
    
    def run_command(self, command: str, description: str) -> bool:
        """Ejecuta un comando y retorna si fue exitoso"""
        print(f"\n{'='*60}")
        print(f"🚀 {description}")
        print(f"{'='*60}")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                print("✅ Comando ejecutado exitosamente")
                print(result.stdout)
                return True
            else:
                print("❌ Comando falló")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Comando excedió el tiempo límite")
            return False
        except Exception as e:
            print(f"❌ Error ejecutando comando: {e}")
            return False
    
    def start_api(self, use_refactored: bool = True) -> bool:
        """Inicia la API en segundo plano"""
        api_file = "main_refactored.py" if use_refactored else "main.py"
        
        if not os.path.exists(api_file):
            print(f"❌ Archivo {api_file} no encontrado")
            return False
        
        print(f"\n🚀 Iniciando API ({api_file})...")
        
        try:
            # Iniciar API en segundo plano
            self.api_process = subprocess.Popen(
                [sys.executable, api_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Esperar un poco para que la API se inicie
            print("⏳ Esperando que la API se inicie...")
            time.sleep(5)
            
            # Verificar si la API está funcionando
            import requests
            try:
                response = requests.get("http://localhost:8000/", timeout=5)
                if response.status_code == 200:
                    print("✅ API iniciada correctamente")
                    return True
                else:
                    print(f"❌ API no responde correctamente: {response.status_code}")
                    return False
            except:
                print("❌ No se puede conectar a la API")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando API: {e}")
            return False
    
    def stop_api(self):
        """Detiene la API"""
        if self.api_process:
            print("\n🛑 Deteniendo API...")
            self.api_process.terminate()
            self.api_process.wait()
            print("✅ API detenida")
    
    def run_unit_tests(self) -> bool:
        """Ejecuta tests unitarios"""
        return self.run_command(
            f"{sys.executable} test_units.py",
            "EJECUTANDO TESTS UNITARIOS"
        )
    
    def run_integration_tests(self) -> bool:
        """Ejecuta tests de integración"""
        return self.run_command(
            f"{sys.executable} test_integration.py",
            "EJECUTANDO TESTS DE INTEGRACIÓN"
        )
    
    def run_api_tests(self) -> bool:
        """Ejecuta tests de la API"""
        return self.run_command(
            f"{sys.executable} test_refactored_api.py",
            "EJECUTANDO TESTS DE LA API"
        )
    
    def run_original_api_tests(self) -> bool:
        """Ejecuta tests con la API original"""
        return self.run_command(
            f"{sys.executable} test_api.py",
            "EJECUTANDO TESTS DE LA API ORIGINAL"
        )
    
    def run_all_tests(self, test_original: bool = False):
        """Ejecuta todos los tests"""
        print("🔧 AoE Build Guide API - Test Suite Completa")
        print("=" * 70)
        
        # 1. Tests unitarios (no requieren API)
        print("\n📋 FASE 1: TESTS UNITARIOS")
        self.test_results["unit_tests"] = self.run_unit_tests()
        
        # 2. Tests de integración (no requieren API)
        print("\n📋 FASE 2: TESTS DE INTEGRACIÓN")
        self.test_results["integration_tests"] = self.run_integration_tests()
        
        # 3. Iniciar API refactorizada
        print("\n📋 FASE 3: TESTS DE API REFACTORIZADA")
        if self.start_api(use_refactored=True):
            self.test_results["refactored_api_tests"] = self.run_api_tests()
            self.stop_api()
        else:
            print("❌ No se pudo iniciar la API refactorizada")
            self.test_results["refactored_api_tests"] = False
        
        # 4. Tests con API original (opcional)
        if test_original:
            print("\n📋 FASE 4: TESTS DE API ORIGINAL")
            if self.start_api(use_refactored=False):
                self.test_results["original_api_tests"] = self.run_original_api_tests()
                self.stop_api()
            else:
                print("❌ No se pudo iniciar la API original")
                self.test_results["original_api_tests"] = False
        
        # 5. Mostrar resultados finales
        self.print_final_results()
    
    def print_final_results(self):
        """Imprime los resultados finales"""
        print("\n" + "=" * 70)
        print("📊 RESULTADOS FINALES DE TODOS LOS TESTS")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"✅ Tests pasados: {passed_tests}/{total_tests}")
        print(f"❌ Tests fallidos: {total_tests - passed_tests}/{total_tests}")
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        print(f"🎯 Tasa de éxito general: {success_rate:.1f}%")
        
        print("\n📋 Detalle por fase:")
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        if success_rate == 100:
            print("\n🎉 ¡Todos los tests pasaron! La refactorización fue exitosa.")
        elif success_rate >= 75:
            print("\n⚠️  La mayoría de tests pasaron. Revisa los fallos.")
        else:
            print("\n❌ Muchos tests fallaron. Revisa la implementación.")


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ejecutar tests de la API refactorizada")
    parser.add_argument("--original", action="store_true", help="Incluir tests de la API original")
    parser.add_argument("--unit-only", action="store_true", help="Solo ejecutar tests unitarios")
    parser.add_argument("--integration-only", action="store_true", help="Solo ejecutar tests de integración")
    parser.add_argument("--api-only", action="store_true", help="Solo ejecutar tests de API")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.unit_only:
        runner.run_unit_tests()
    elif args.integration_only:
        runner.run_integration_tests()
    elif args.api_only:
        if runner.start_api(use_refactored=True):
            runner.run_api_tests()
            runner.stop_api()
    else:
        runner.run_all_tests(test_original=args.original)


if __name__ == "__main__":
    main()
