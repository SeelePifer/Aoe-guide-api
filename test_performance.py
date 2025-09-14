#!/usr/bin/env python3
"""
Script de testing de rendimiento para la API optimizada
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
import json


class PerformanceTester:
    """Tester de rendimiento para la API optimizada"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
    
    async def test_endpoint(self, session: aiohttp.ClientSession, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Testea un endpoint específico"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with session.get(url, params=params) as response:
                end_time = time.time()
                
                response_data = await response.json()
                
                return {
                    "endpoint": endpoint,
                    "status_code": response.status,
                    "response_time": (end_time - start_time) * 1000,  # ms
                    "data_size": len(json.dumps(response_data)),
                    "success": response.status == 200,
                    "cache_header": response.headers.get("X-Cache-Status", "unknown"),
                    "process_time": response.headers.get("X-Process-Time", "unknown")
                }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status_code": 0,
                "response_time": (time.time() - start_time) * 1000,
                "data_size": 0,
                "success": False,
                "error": str(e)
            }
    
    async def run_single_tests(self) -> Dict[str, Any]:
        """Ejecuta tests individuales de endpoints"""
        print("🧪 Ejecutando tests individuales...")
        
        async with aiohttp.ClientSession() as session:
            tests = [
                ("/", {}),
                ("/health", {}),
                ("/builds/types", {}),
                ("/builds/difficulties", {}),
                ("/cache/stats", {}),
                ("/builds", {"page": 1, "size": 10}),
                ("/builds/feudal_rush", {"page": 1, "size": 5}),
                ("/builds/difficulty/beginner", {"page": 1, "size": 5}),
                ("/builds/search", {"q": "rush", "page": 1, "size": 5}),
                ("/builds/filter", {"build_type": "feudal_rush", "page": 1, "size": 5})
            ]
            
            results = []
            for endpoint, params in tests:
                result = await self.test_endpoint(session, endpoint, params)
                results.append(result)
                
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {endpoint} - {result['response_time']:.2f}ms")
            
            return {"single_tests": results}
    
    async def run_load_tests(self, concurrent_requests: int = 10, requests_per_endpoint: int = 5) -> Dict[str, Any]:
        """Ejecuta tests de carga"""
        print(f"🚀 Ejecutando tests de carga ({concurrent_requests} concurrent, {requests_per_endpoint} por endpoint)...")
        
        endpoints = [
            ("/builds", {"page": 1, "size": 10}),
            ("/builds/feudal_rush", {"page": 1, "size": 5}),
            ("/builds/search", {"q": "rush", "page": 1, "size": 5})
        ]
        
        all_results = []
        
        async with aiohttp.ClientSession() as session:
            for endpoint, params in endpoints:
                print(f"   Testing {endpoint}...")
                
                # Crear tareas concurrentes
                tasks = []
                for _ in range(requests_per_endpoint):
                    task = self.test_endpoint(session, endpoint, params)
                    tasks.append(task)
                
                # Ejecutar en lotes concurrentes
                batch_size = concurrent_requests
                batch_results = []
                
                for i in range(0, len(tasks), batch_size):
                    batch = tasks[i:i + batch_size]
                    batch_result = await asyncio.gather(*batch)
                    batch_results.extend(batch_result)
                
                all_results.extend(batch_results)
        
        return {"load_tests": all_results}
    
    async def run_cache_tests(self) -> Dict[str, Any]:
        """Ejecuta tests de cache"""
        print("💾 Ejecutando tests de cache...")
        
        async with aiohttp.ClientSession() as session:
            # Primera llamada (cache miss)
            result1 = await self.test_endpoint(session, "/builds", {"page": 1, "size": 10})
            
            # Segunda llamada (cache hit)
            result2 = await self.test_endpoint(session, "/builds", {"page": 1, "size": 10})
            
            # Tercera llamada (cache hit)
            result3 = await self.test_endpoint(session, "/builds", {"page": 1, "size": 10})
            
            cache_improvement = ((result1["response_time"] - result2["response_time"]) / result1["response_time"]) * 100
            
            print(f"   Cache Miss: {result1['response_time']:.2f}ms")
            print(f"   Cache Hit 1: {result2['response_time']:.2f}ms")
            print(f"   Cache Hit 2: {result3['response_time']:.2f}ms")
            print(f"   Mejora de cache: {cache_improvement:.1f}%")
            
            return {
                "cache_tests": [result1, result2, result3],
                "cache_improvement": cache_improvement
            }
    
    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza los resultados de los tests"""
        analysis = {}
        
        # Análisis de tests individuales
        if "single_tests" in results:
            single_tests = results["single_tests"]
            successful_tests = [t for t in single_tests if t["success"]]
            
            analysis["single_tests"] = {
                "total_tests": len(single_tests),
                "successful_tests": len(successful_tests),
                "success_rate": (len(successful_tests) / len(single_tests)) * 100,
                "avg_response_time": statistics.mean([t["response_time"] for t in successful_tests]),
                "max_response_time": max([t["response_time"] for t in successful_tests]),
                "min_response_time": min([t["response_time"] for t in successful_tests])
            }
        
        # Análisis de tests de carga
        if "load_tests" in results:
            load_tests = results["load_tests"]
            successful_load_tests = [t for t in load_tests if t["success"]]
            
            analysis["load_tests"] = {
                "total_requests": len(load_tests),
                "successful_requests": len(successful_load_tests),
                "success_rate": (len(successful_load_tests) / len(load_tests)) * 100,
                "avg_response_time": statistics.mean([t["response_time"] for t in successful_load_tests]),
                "max_response_time": max([t["response_time"] for t in successful_load_tests]),
                "min_response_time": min([t["response_time"] for t in successful_load_tests]),
                "throughput": len(successful_load_tests) / (max([t["response_time"] for t in successful_load_tests]) / 1000)
            }
        
        return analysis
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Ejecuta todos los tests de rendimiento"""
        print("🚀 Iniciando tests de rendimiento de la API optimizada...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Ejecutar tests
        single_results = await self.run_single_tests()
        load_results = await self.run_load_tests()
        cache_results = await self.run_cache_tests()
        
        # Combinar resultados
        all_results = {**single_results, **load_results, **cache_results}
        
        # Analizar resultados
        analysis = self.analyze_results(all_results)
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE RENDIMIENTO")
        print("=" * 60)
        
        # Mostrar análisis
        if "single_tests" in analysis:
            st = analysis["single_tests"]
            print(f"✅ Tests Individuales: {st['successful_tests']}/{st['total_tests']} ({st['success_rate']:.1f}%)")
            print(f"   Tiempo promedio: {st['avg_response_time']:.2f}ms")
            print(f"   Tiempo máximo: {st['max_response_time']:.2f}ms")
        
        if "load_tests" in analysis:
            lt = analysis["load_tests"]
            print(f"🚀 Tests de Carga: {lt['successful_requests']}/{lt['total_requests']} ({lt['success_rate']:.1f}%)")
            print(f"   Tiempo promedio: {lt['avg_response_time']:.2f}ms")
            print(f"   Throughput: {lt['throughput']:.2f} req/s")
        
        if "cache_improvement" in cache_results:
            print(f"💾 Mejora de Cache: {cache_results['cache_improvement']:.1f}%")
        
        print(f"⏱️  Tiempo total de tests: {total_time:.2f}s")
        
        return {
            "results": all_results,
            "analysis": analysis,
            "total_time": total_time
        }


async def main():
    """Función principal"""
    print("AoE Build Guide API - Performance Testing")
    print("=" * 60)
    
    tester = PerformanceTester()
    
    try:
        results = await tester.run_all_tests()
        
        # Guardar resultados en archivo
        with open("performance_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Resultados guardados en performance_results.json")
        
    except Exception as e:
        print(f"❌ Error durante los tests: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
