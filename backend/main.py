from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from backend.routers import scan, clipforge

load_dotenv()

app = FastAPI(
    title="ChimeraShield API",
    description="AI-powered cybersecurity analysis backend",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",  # Vite dev server (ClipForge Studio)
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan.router)
app.include_router(clipforge.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "ChimeraShield API", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
