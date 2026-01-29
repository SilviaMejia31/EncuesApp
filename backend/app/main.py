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
    t = catalog_table()
    resp = t.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "COUNTRY"},
    )
    items = resp.get("Items", [])
    return [{"id": it["sk"], "name": it["name"]} for it in items]

@app.get("/companies")
def get_companies(country_id: str):
    t = catalog_table()
    resp = t.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": f"COMPANY#{country_id}"},
    )
    items = resp.get("Items", [])
    return [{"id": it["sk"], "name": it["name"], "country_id": country_id} for it in items]

@app.get("/branches")
def get_branches(company_id: str):
    t = catalog_table()
    resp = t.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": f"BRANCH#{company_id}"},
    )
    items = resp.get("Items", [])
    return [{"id": it["sk"], "name": it["name"], "company_id": company_id} for it in items]

@app.get("/questions")
def get_questions():
    t = catalog_table()
    resp = t.query(
        KeyConditionExpression="pk = :pk",
        ExpressionAttributeValues={":pk": "QUESTION"},
    )
    items = sorted(resp.get("Items", []), key=lambda x: int(x["sk"]))
    items = items[:5]
    return [{"id": int(it["sk"]), "text": it["text"]} for it in items]


@app.post("/responses")
def create_response(payload: ResponseIn):
    if not payload.branch_id:
        raise HTTPException(status_code=400, detail="branch_id requerido.")
    if not payload.answers or len(payload.answers) == 0:
        raise HTTPException(status_code=400, detail="Debe enviar al menos una respuesta.")
    if len(payload.answers) > 5:
        raise HTTPException(status_code=400, detail="Máximo 5 respuestas.")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    survey_response_id = f"{payload.branch_id}#{now}"

    item = {
        "branch_id": str(payload.branch_id),
        "created_at": now,
        "survey_response_id": survey_response_id,
        "answers": [{"question_id": a.question_id, "value": a.value} for a in payload.answers],
    }

    t = responses_table()
    t.put_item(Item=item)

    return {"message": "Saved", "survey_response_id": survey_response_id}

@app.get("/export")
def export_results():
    import csv, io
    from fastapi.responses import StreamingResponse

    t = responses_table()
    resp = t.scan()
    items = resp.get("Items", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["survey_response_id", "branch_id", "created_at", "question_id", "answer_value"])

    for it in items:
        for ans in it.get("answers", []):
            writer.writerow([
                it.get("survey_response_id", ""),
                it.get("branch_id", ""),
                it.get("created_at", ""),
                ans.get("question_id", ""),
                ans.get("value", ""),
            ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=survey_results.csv"},
    )
    
handler = Mangum(app)

