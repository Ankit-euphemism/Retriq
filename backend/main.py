from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
import uvicorn

app = FastAPI(title="Retriq Query System")

# CORS — allow frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Lock to your frontend URL in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
# Run: uvicorn main:app --reload --port 8000

# Health check — Render pings this to verify deploy success
@app.get("/health")
async def health():
    return {"status": "ok", "app": "Retriq Query System"}

@app.get("/")
async def root():
    return {"message": "Welcome to Retriq Query System!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True, log_level="info")
