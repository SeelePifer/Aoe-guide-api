#!/usr/bin/env python3
"""
Test script para demostrar la funcionalidad de la API con pasos detallados
"""

import requests
import json

# URL base de la API
BASE_URL = "http://localhost:8000"

def test_build_guide():
    """Test para obtener guía detallada de un tipo de build"""
    
    print("=== Test de Guía Detallada de Builds ===\n")
    
    # Test 1: Obtener guía para Feudal Rush
    print("1. Obteniendo guía para 'feudal_rush':")
    try:
        response = requests.get(f"{BASE_URL}/builds/feudal_rush/guide")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Build Type: {data['build_type']}")
            print(f"   ✓ Main Build: {data['main_build']['name']}")
            print(f"   ✓ Difficulty: {data['main_build']['difficulty']}")
            print(f"   ✓ Total Steps: {len(data['main_build']['steps'])}")
            print(f"   ✓ Alternative Builds: {len(data['alternative_builds'])}")
            print(f"   ✓ Total Available: {data['total_available']}")
            
            # Mostrar los primeros 3 pasos
            print("\n   Primeros 3 pasos del build principal:")
            for i, step in enumerate(data['main_build']['steps'][:3]):
                print(f"      {i+1}. {step['action']} ({step['age']} - {step['time']})")
                print(f"         {step['details']}")
                if step['resources_needed']:
                    print(f"         Recursos: {step['resources_needed']}")
                print()
        else:
            print(f"   ✗ Error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Obtener builds filtrados por tipo
    print("2. Obteniendo builds filtrados por 'feudal_rush':")
    try:
        response = requests.get(f"{BASE_URL}/builds/feudal_rush")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Total builds: {data['total']}")
            print(f"   ✓ Build type: {data['build_type']}")
            
            # Mostrar información de los primeros 3 builds
            print("\n   Primeros 3 builds:")
            for i, build in enumerate(data['builds'][:3]):
                print(f"      {i+1}. {build['name']} ({build['difficulty']})")
                print(f"         Steps: {len(build['steps']) if build['steps'] else 0}")
                print()
        else:
            print(f"   ✗ Error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Obtener todos los tipos de builds disponibles
    print("3. Tipos de builds disponibles:")
    try:
        response = requests.get(f"{BASE_URL}/builds/types")
        if response.status_code == 200:
            types = response.json()
            print(f"   ✓ Tipos disponibles: {', '.join(types)}")
        else:
            print(f"   ✗ Error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")

def test_specific_build_steps():
    """Test para mostrar pasos específicos de un build"""
    
    print("\n=== Test de Pasos Específicos ===\n")
    
    # Test con Fast Castle
    print("4. Guía detallada para 'fast_castle':")
    try:
        response = requests.get(f"{BASE_URL}/builds/fast_castle/guide")
        if response.status_code == 200:
            data = response.json()
            main_build = data['main_build']
            print(f"   Build: {main_build['name']}")
            print(f"   Dificultad: {main_build['difficulty']}")
            print(f"   Total de pasos: {len(main_build['steps'])}")
            
            print("\n   Pasos detallados:")
            for step in main_build['steps']:
                print(f"      Paso {step['step_number']}: {step['action']}")
                print(f"         Edad: {step['age']} | Tiempo: {step['time']}")
                print(f"         Detalles: {step['details']}")
                if step['resources_needed']:
                    print(f"         Recursos necesarios: {step['resources_needed']}")
                print()
        else:
            print(f"   ✗ Error: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error de conexión: {e}")

if __name__ == "__main__":
    print("Iniciando tests de la API de AoE Build Guide...")
    print("Asegúrate de que la API esté ejecutándose en http://localhost:8000")
    print("\n")
    
    test_build_guide()
    test_specific_build_steps()
    
    print("\n=== Tests Completados ===")
    print("La API ahora incluye:")
    print("✓ Pasos detallados paso a paso para cada build")
    print("✓ Información de recursos necesarios")
    print("✓ Tiempos específicos para cada acción")
    print("✓ Guías detalladas por tipo de build")
    print("✓ Endpoint específico para guías: /builds/{build_type}/guide")
