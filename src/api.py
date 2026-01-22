from fastapi import FastAPI
from main import main as run_bot

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/run")
def run():
    run_bot()
    return {"status": "bot executed"}
