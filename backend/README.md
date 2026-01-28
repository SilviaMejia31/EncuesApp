# Backend - EncuesApp

Este backend está desarrollado en Python utilizando FastAPI.
Provee una API REST para gestionar encuestas y almacenar respuestas.

## Endpoints

- GET `/countries`  
  Devuelve el listado de países.

- GET `/companies?country_id=1`  
  Devuelve empresas filtradas por país.

- GET `/branches?company_id=1`  
  Devuelve sedes filtradas por empresa.

- GET `/questions`  
  Devuelve hasta 5 preguntas.

- POST `/responses`  
  Guarda una encuesta respondida.

Ejemplo de body:
```json
{
  "branch_id": 1,
  "answers": [
    { "question_id": 1, "value": "5" },
    { "question_id": 2, "value": "Sí" },
    { "question_id": 3, "value": "Rápido" }
  ]
}


