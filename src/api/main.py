from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="PBS Arcade.XYZ API",
    description="AI-powered game creation studio",
    version="0.1.0"
)

@app.get("/")
async def root():
    return JSONResponse({"status": "🎮 Arcade.XYZ API ready"})

@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy"})
