from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .database import get_connection
import csv
import io
from fastapi.responses import StreamingResponse
import os
from datetime import datetime, timezone
from mangum import Mangum
from .dynamo import catalog_table, responses_table



app = FastAPI(title="Survey API")

# -----------------------
# Models
# -----------------------
class AnswerIn(BaseModel):
    question_id: int
    value: str

class ResponseIn(BaseModel):
    branch_id: int
    answers: List[AnswerIn]

# -----------------------
# Helpers
# -----------------------
def fetch_all(query: str, params: tuple = ()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def execute(query: str, params: tuple = ()):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    last_id = cur.lastrowid
    conn.close()
    return last_id

# -----------------------
# Routes
# -----------------------
@app.get("/")
def root():
    return {"message": "Survey API is running"}

@app.get("/countries")
def get_countries():
    return fetch_all("SELECT id, name FROM countries ORDER BY name")

@app.get("/companies")
def get_companies(country_id: int):
    return fetch_all(
        "SELECT id, name, country_id FROM companies WHERE country_id = ? ORDER BY name",
        (country_id,),
    )

@app.get("/branches")
def get_branches(company_id: int):
    return fetch_all(
        "SELECT id, name, company_id FROM branches WHERE company_id = ? ORDER BY name",
        (company_id,),
    )

@app.get("/questions")
def get_questions():
    # max 5 preguntas
    return fetch_all("SELECT id, text FROM questions ORDER BY id LIMIT 5")

@app.post("/responses")
def create_response(payload: ResponseIn):
    # Validar branch
    branch = fetch_one("SELECT id FROM branches WHERE id = ?", (payload.branch_id,))
    if not branch:
        raise HTTPException(status_code=400, detail="branch_id inválido (no existe).")

    # Validar cantidad de respuestas (máx 5)
    if len(payload.answers) == 0:
        raise HTTPException(status_code=400, detail="Debe enviar al menos una respuesta.")
    if len(payload.answers) > 5:
        raise HTTPException(status_code=400, detail="Máximo 5 respuestas por encuesta.")

    # Validar que las preguntas existan y estén en el set permitido (las primeras 5)
    allowed_questions = fetch_all("SELECT id FROM questions ORDER BY id LIMIT 5")
    allowed_ids = {q["id"] for q in allowed_questions}

    for ans in payload.answers:
        if ans.question_id not in allowed_ids:
            raise HTTPException(
                status_code=400,
                detail=f"question_id inválido o fuera de las primeras 5 preguntas: {ans.question_id}"
            )
        if not ans.value or not ans.value.strip():
            raise HTTPException(status_code=400, detail="No se permiten respuestas vacías.")

    # Crear survey_response
    response_id = execute(
        "INSERT INTO survey_responses (branch_id, created_at) VALUES (?, datetime('now'))",
        (payload.branch_id,),
    )

    # Insertar answers
    for ans in payload.answers:
        execute(
            "INSERT INTO answers (survey_response_id, question_id, value) VALUES (?, ?, ?)",
            (response_id, ans.question_id, ans.value.strip()),
        )

    return {"message": "Saved", "survey_response_id": response_id}


@app.get("/export")
def export_results():
    conn = get_connection()
    cur = conn.cursor()

    # Traemos todo “aplanado” para CSV:
    # una fila por respuesta a una pregunta
    cur.execute("""
        SELECT
            sr.id AS survey_response_id,
            sr.created_at,
            c.name AS country,
            co.name AS company,
            b.name AS branch,
            q.id AS question_id,
            q.text AS question_text,
            a.value AS answer_value
        FROM survey_responses sr
        JOIN branches b ON b.id = sr.branch_id
        JOIN companies co ON co.id = b.company_id
        JOIN countries c ON c.id = co.country_id
        JOIN answers a ON a.survey_response_id = sr.id
        JOIN questions q ON q.id = a.question_id
        ORDER BY sr.id, q.id
    """)
    rows = cur.fetchall()
    conn.close()

    # Armamos CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)

    # Encabezados
    writer.writerow([
        "survey_response_id",
        "created_at",
        "country",
        "company",
        "branch",
        "question_id",
        "question_text",
        "answer_value"
    ])

    # Filas
    for r in rows:
        writer.writerow([
            r["survey_response_id"],
            r["created_at"],
            r["country"],
            r["company"],
            r["branch"],
            r["question_id"],
            r["question_text"],
            r["answer_value"]
        ])

    output.seek(0)

    filename = "survey_results.csv"
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

