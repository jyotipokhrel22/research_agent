from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path

# .env loading logic
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.api.routes import auth, papers, reports
from app.core.config import API_KEY

app = FastAPI(title="Research Agent API")

# Updated Middleware with Bypass for Localhost
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    path = request.url.path
    
    PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/redoc", "/favicon.ico"}
    if path in PUBLIC_PATHS or path.startswith("/docs") or "openapi.json" in path:
        return await call_next(request)

    #to take api key from header
    api_key_header = request.headers.get("x-api-key")
    
    # DEBUG PRINT
    print(f"DEBUG -> Path: {path} | Header: {api_key_header} | Env: {API_KEY}")

    if not api_key_header:
        # Check if it's local development
        host = request.url.hostname
        if host == "127.0.0.1" or host == "localhost":
            return await call_next(request)
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Missing API key"},
        )
    

    if api_key_header != API_KEY:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid API key"},
        )
        
    return await call_next(request)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, tags=["Auth"])
app.include_router(papers.router, tags=["Papers"])
app.include_router(reports.router, tags=["Reports"])

# Custom OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Research Agent API",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "x-api-key",
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [
        {"APIKeyHeader": []},
        {"BearerAuth": []}
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/", tags=["Health"])
def home():
    return {"message": "Research Agent API running"}