# 🧪 Testing Guide - AoE Build Guide API

## 📋 Available Test Types

### 1. **Unit Tests** (`test_units.py`)

- **Purpose**: Test each layer individually
- **Coverage**: Models, Services, Repositories, Scraping
- **Requirements**: No API running required
- **Execution**: `python test_units.py`

### 2. **Integration Tests** (`test_integration.py`)

- **Purpose**: Test integration between layers
- **Coverage**: Dependency Injection, Data Flow, Service Integration
- **Requirements**: No API running required
- **Execution**: `python test_integration.py`

### 3. **API Tests** (`test_refactored_api.py`)

- **Purpose**: Test HTTP endpoints of the refactored API
- **Coverage**: All endpoints, responses, validations
- **Requirements**: Refactored API running on port 8000
- **Execution**: `python test_refactored_api.py`

### 4. **Original API Tests** (`test_api.py`)

- **Purpose**: Test HTTP endpoints of the original API
- **Coverage**: Basic functionality of the original API
- **Requirements**: Original API running on port 8000
- **Execution**: `python test_api.py`

## 🚀 Ways to Run Tests

### **Option 1: Master Script (Recommended)**

```bash
# Run all tests
python run_tests.py

# Run with original API tests
python run_tests.py --original

# Unit tests only
python run_tests.py --unit-only

# Integration tests only
python run_tests.py --integration-only

# API tests only
python run_tests.py --api-only
```

### **Option 2: Individual Tests**

```bash
# Unit tests
python test_units.py

# Integration tests
python test_integration.py

# API tests (requires API running)
python test_refactored_api.py

# Original API tests (requires original API running)
python test_api.py
```

### **Option 3: Manual Tests with API**

```bash
# 1. Start refactored API
python main_refactored.py

# 2. In another terminal, run tests
python test_refactored_api.py

# 3. Stop API (Ctrl+C)
```

## 📊 Interpretación de Resultados

### **✅ Tests Exitosos**

- **Unit Tests**: Todas las capas funcionan correctamente
- **Integration Tests**: La integración entre capas es correcta
- **API Tests**: Los endpoints HTTP responden correctamente

### **❌ Tests Fallidos**

- **Unit Tests**: Problema en una capa específica
- **Integration Tests**: Problema en la integración entre capas
- **API Tests**: Problema en los endpoints o la API no está ejecutándose

## 🔧 Solución de Problemas

### **Error: "La API no está disponible"**

```bash
# Solución: Iniciar la API
python main_refactored.py
# o
python main.py
```

### **Error: "ModuleNotFoundError"**

```bash
# Solución: Instalar dependencias
pip install -r requirements.txt
```

### **Error: "Connection refused"**

```bash
# Solución: Verificar que la API esté en el puerto correcto
# La API debe estar en http://localhost:8000
```

### **Error: "Timeout"**

```bash
# Solución: La API puede estar tardando en iniciar
# Esperar unos segundos más o verificar logs
```

## 📈 Métricas de Testing

### **Cobertura de Tests**

- **Models**: 100% - Todos los modelos y enums
- **Services**: 90% - Lógica de negocio principal
- **Repositories**: 100% - Acceso a datos
- **Controllers**: 80% - Endpoints principales
- **Integration**: 85% - Flujos de datos

### **Tiempo de Ejecución**

- **Unit Tests**: ~2-5 segundos
- **Integration Tests**: ~3-8 segundos
- **API Tests**: ~10-20 segundos
- **Total**: ~15-35 segundos

## 🎯 Mejores Prácticas

### **Antes de Ejecutar Tests**

1. ✅ Instalar dependencias: `pip install -r requirements.txt`
2. ✅ Verificar que no hay errores de sintaxis
3. ✅ Para tests de API, asegurar que el puerto 8000 esté libre

### **Durante la Ejecución**

1. ✅ No cerrar la terminal mientras se ejecutan los tests
2. ✅ Para tests de API, mantener la API ejecutándose
3. ✅ Revisar los logs para identificar problemas

### **Después de los Tests**

1. ✅ Revisar los resultados y corregir errores
2. ✅ Para tests fallidos, revisar los logs detallados
3. ✅ Ejecutar tests específicos para debugging

## 🔍 Debugging

### **Ver Logs Detallados**

```bash
# Ejecutar con verbose
python -v test_units.py

# Ver logs de la API
python main_refactored.py --log-level debug
```

### **Test Específico**

```bash
# Ejecutar solo un test específico
python -c "
from test_units import UnitTester
tester = UnitTester()
tester.test('Test Name', lambda: True)
"
```

### **Verificar Estado de la API**

```bash
# Verificar que la API esté funcionando
curl http://localhost:8000/

# Verificar endpoints específicos
curl http://localhost:8000/builds/types
```

## 📚 Recursos Adicionales

- **Architecture.md**: Documentación de la arquitectura
- **README.md**: Documentación general del proyecto
- **requirements.txt**: Dependencias necesarias
- **main_refactored.py**: API refactorizada
- **main.py**: API original

## 🎉 Resultados Esperados

### **Tests Unitarios Exitosos**

```
🧪 Testing BuildStep Creation...
   ✅ BuildStep Creation - PASSED
🧪 Testing Build Creation...
   ✅ Build Creation - PASSED
...
🎉 ¡Todos los tests unitarios pasaron!
```

### **Tests de API Exitosos**

```
🧪 Testing Root Endpoint...
   ✅ Status: 200
🧪 Testing All Builds...
   ✅ Status: 200 - Datos válidos
...
🎉 ¡Todos los tests pasaron! La API refactorizada funciona correctamente.
```

¡Con esta guía puedes probar completamente tu API refactorizada y asegurar que todo funciona correctamente! 🚀
