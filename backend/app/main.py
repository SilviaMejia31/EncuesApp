from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from .database import get_connection

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
    # 1) crear 
    response_id = execute(
        "INSERT INTO survey_responses (branch_id, created_at) VALUES (?, datetime('now'))",
        (payload.branch_id,),
    )

    # 2) insertar respuestas
    for ans in payload.answers:
        execute(
            "INSERT INTO answers (survey_response_id, question_id, value) VALUES (?, ?, ?)",
            (response_id, ans.question_id, ans.value),
        )

    return {"message": "Saved", "survey_response_id": response_id}
