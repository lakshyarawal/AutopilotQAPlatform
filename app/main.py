from fastapi import FastAPI

from app.api.routes import router
from app.db.init_db import init_db

app = FastAPI(title="Autopilot AI Tooling MVP")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router, prefix="/api")
