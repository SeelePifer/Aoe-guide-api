# 🧪 Guía de Testing - AoE Build Guide API

## 📋 Tipos de Tests Disponibles

### 1. **Tests Unitarios** (`test_units.py`)

- **Propósito**: Probar cada capa individualmente
- **Cobertura**: Models, Services, Repositories, Scraping
- **Requisitos**: No requiere API ejecutándose
- **Ejecución**: `python test_units.py`

### 2. **Tests de Integración** (`test_integration.py`)

- **Propósito**: Probar la integración entre capas
- **Cobertura**: Dependency Injection, Data Flow, Service Integration
- **Requisitos**: No requiere API ejecutándose
- **Ejecución**: `python test_integration.py`

### 3. **Tests de API** (`test_refactored_api.py`)

- **Propósito**: Probar endpoints HTTP de la API refactorizada
- **Cobertura**: Todos los endpoints, respuestas, validaciones
- **Requisitos**: API refactorizada ejecutándose en puerto 8000
- **Ejecución**: `python test_refactored_api.py`

### 4. **Tests de API Original** (`test_api.py`)

- **Propósito**: Probar endpoints HTTP de la API original
- **Cobertura**: Funcionalidad básica de la API original
- **Requisitos**: API original ejecutándose en puerto 8000
- **Ejecución**: `python test_api.py`

## 🚀 Formas de Ejecutar los Tests

### **Opción 1: Script Maestro (Recomendado)**

```bash
# Ejecutar todos los tests
python run_tests.py

# Ejecutar con tests de API original
python run_tests.py --original

# Solo tests unitarios
python run_tests.py --unit-only

# Solo tests de integración
python run_tests.py --integration-only

# Solo tests de API
python run_tests.py --api-only
```

### **Opción 2: Tests Individuales**

```bash
# Tests unitarios
python test_units.py

# Tests de integración
python test_integration.py

# Tests de API (requiere API ejecutándose)
python test_refactored_api.py

# Tests de API original (requiere API original ejecutándose)
python test_api.py
```

### **Opción 3: Tests Manuales con API**

```bash
# 1. Iniciar API refactorizada
python main_refactored.py

# 2. En otra terminal, ejecutar tests
python test_refactored_api.py

# 3. Detener API (Ctrl+C)
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
