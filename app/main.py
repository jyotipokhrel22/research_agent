from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv
import os

load_dotenv()

from app.api.routes import auth, papers, reports
from app.core.config import API_KEY_NAME, API_KEY

app = FastAPI(title="Research Agent API")

# Include routers
app.include_router(auth.router, tags=["Auth"])
app.include_router(papers.router, tags=["Papers"])
app.include_router(reports.router, tags=["Reports"])

# Public paths
PUBLIC_PATHS = {"/", "/docs", "/openapi.json", "/redoc"}

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
        }
    }
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Middleware
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    api_key = request.headers.get(API_KEY_NAME)
    if not api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Missing API key"},
        )
    if api_key != API_KEY:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Invalid API key"},
        )
    return await call_next(request)

# Exception handlers
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred."},
    )

@app.get("/", tags=["Health"])
def home():
    return {"message": "Research Agent API running"}