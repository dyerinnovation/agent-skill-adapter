from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controllers import skills, training, evaluation

app = FastAPI(title="Skill Adapter API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(training.router, prefix="/api/training", tags=["training"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["evaluation"])


@app.get("/health")
async def health():
    return {"status": "ok"}
