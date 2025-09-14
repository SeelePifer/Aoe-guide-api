# AoE Build Guide API

Una API REST construida con FastAPI que consume información de builds de Age of Empires desde [AoE Companion](https://aoecompanion.com/build-guides).

## Características

- 🎯 **Filtrado por tipo de build**: Feudal Rush, Fast Castle, Dark Age Rush, Water Maps
- 📊 **Filtrado por dificultad**: Beginner, Intermediate, Advanced
- 🔍 **Búsqueda de texto**: Busca builds por nombre o descripción
- ⚡ **Cache inteligente**: Los builds se cargan una vez al inicio
- 🚀 **API RESTful**: Endpoints bien documentados

## Instalación

1. Clona el repositorio:

```bash
git clone <tu-repositorio>
cd Aoe-guide-api
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:

```bash
python main.py
```

La API estará disponible en `http://localhost:8000`

## Documentación

Una vez que la aplicación esté ejecutándose, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints Disponibles

### Obtener todos los builds

```
GET /builds
```

### Filtrar por tipo de build

```
GET /builds/{build_type}
```

Tipos disponibles:

- `feudal_rush`
- `fast_castle`
- `dark_age_rush`
- `water_maps`

### Filtrar por dificultad

```
GET /builds/difficulty/{difficulty}
```

Dificultades disponibles:

- `beginner`
- `intermediate`
- `advanced`

### Buscar builds

```
GET /builds/search?q={query}
```

### Obtener tipos de builds

```
GET /builds/types
```

### Obtener dificultades

```
GET /builds/difficulties
```

### Refrescar cache

```
POST /builds/refresh
```

## Ejemplos de Uso

### Obtener todos los builds de Feudal Rush

```bash
curl http://localhost:8000/builds/feudal_rush
```

### Buscar builds de arqueros

```bash
curl "http://localhost:8000/builds/search?q=archer"
```

### Obtener builds para principiantes

```bash
curl http://localhost:8000/builds/difficulty/beginner
```

## Estructura de Respuesta

```json
{
  "builds": [
    {
      "name": "Scout Rush",
      "difficulty": "intermediate",
      "description": "Start harrassing your opponent with highly mobile Cavalry Scouts...",
      "build_type": "feudal_rush",
      "feudal_age_time": 21,
      "castle_age_time": null,
      "imperial_age_time": null
    }
  ],
  "total": 1,
  "build_type": "feudal_rush"
}
```

## Tecnologías Utilizadas

- **FastAPI**: Framework web moderno y rápido
- **BeautifulSoup4**: Web scraping
- **Requests**: Cliente HTTP
- **Pydantic**: Validación de datos
- **Uvicorn**: Servidor ASGI

## Notas

- La API hace web scraping de AoE Companion al iniciar
- Los datos se cachean en memoria para mejor rendimiento
- Usa el endpoint `/builds/refresh` para actualizar los datos
- La API incluye CORS habilitado para uso en frontends

