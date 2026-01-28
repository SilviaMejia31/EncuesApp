from fastapi import FastAPI

app = FastAPI(title="Survey API")

@app.get("/")
def root():
    return {"message": "Survey API is running"}
