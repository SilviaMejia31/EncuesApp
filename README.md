# Sistema básico de encuestas

En el siguiete proyecto se implementa un sistema web de encuestas lo cual permite lo siguiente:
- Seleccionar país, empresa y sede
- Responder una encuesta
- Almacenar respuestas en una base de datos
- Exportar resultados

El programa esta diseñado para ser simple y claro del sistema de flujo y tecnico.

# Sistema básico de encuestas

Sistema web de encuestas con el flujo:
1) Selección: País → Empresa → Sede  
2) Mostrar encuesta  
3) Guardar respuestas en base de datos  
4) Exportar resultados 

## Estructura del proyecto
- `backend/` API REST (Python + FastAPI)
- `frontend/` Interfaz web (HTML + JS)
- `diagrams/` Diagramas (ER y arquitectura)
- `docs/` Decisiones y notas

## Requisitos
- Python 3.10+ recomendado

## Ejecutar localmente

### Backend
1. Abrir terminal y clonar el repo:
   ```bash
   git clone <URL_DEL_REPO>
   cd EncuesApp/backend

## crear entorno virtual e instalar dependencias
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt

## Crear la base de datos (SQLite) y cargar datos iniciales:

sqlite3 database.db < db/schema.sql
sqlite3 database.db < db/seed.sql

Backend disponible en:

http://localhost:8000

Docs Swagger: http://localhost:8000/docs

Frontend

Abrir frontend/index.html en el navegador (doble click).
Si el backend corre en localhost, ya debería consumir la API.
Si cambias el backend a AWS, edita frontend/app.js y ajusta API_BASE.

Endpoints principales

GET /countries
GET /companies?country_id=1
GET /branches?company_id=1
GET /questions
POST /responses
GET /export (CSV)
