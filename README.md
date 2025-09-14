# AoE Build Guide API

A REST API built with FastAPI that consumes Age of Empires build information from [AoE Companion](https://aoecompanion.com/build-guides).

## Features

- 🎯 **Build type filtering**: Feudal Rush, Fast Castle, Dark Age Rush, Water Maps
- 📊 **Difficulty filtering**: Beginner, Intermediate, Advanced
- 🔍 **Text search**: Search builds by name or description
- ⚡ **Smart caching**: Builds are loaded once at startup
- 🚀 **RESTful API**: Well-documented endpoints

## Installation

1. Clone the repository:

```bash
git clone https://github.com/SeelePifer/Aoe-guide-api.git
cd Aoe-guide-api
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main_optimized.py
```

The API will be available at `http://localhost:8000`

## Documentation

Once the application is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Available Endpoints

### Get all builds

```
GET /builds
```

### Filter by build type

```
GET /builds/{build_type}
```

Available types:

- `feudal_rush`
- `fast_castle`
- `dark_age_rush`
- `water_maps`

### Filter by difficulty

```
GET /builds/difficulty/{difficulty}
```

Available difficulties:

- `beginner`
- `intermediate`
- `advanced`

### Search builds

```
GET /builds/search?q={query}
```

### Get build types

```
GET /builds/types
```

### Get difficulties

```
GET /builds/difficulties
```

### Refresh cache

```
POST /builds/refresh
```

## Usage Examples

### Get all Feudal Rush builds

```bash
curl http://localhost:8000/builds/feudal_rush
```

### Search for archer builds

```bash
curl "http://localhost:8000/builds/search?q=archer"
```

### Get builds for beginners

```bash
curl http://localhost:8000/builds/difficulty/beginner
```

## Response Structure

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

## Technologies Used

- **FastAPI**: Modern and fast web framework
- **BeautifulSoup4**: Web scraping
- **Requests**: HTTP client
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

## Notes

- The API performs web scraping from AoE Companion on startup
- Data is cached in memory for better performance
- Use the `/builds/refresh` endpoint to update data
- The API includes CORS enabled for frontend usage
