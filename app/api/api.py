from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.endpoints import users
from app.api.endpoints.auth import auth_router
from app.api.endpoints.ui import (
    homepage,
    workflow_page,
    temporal_workflow_info_query,
    migration_page,
)
from app.api.endpoints.workflows import (
    migration_workflow,
    asana_to_asana_migrator,
)
from app.repositories.base import BaseRepository
from app.core.config import settings
from temporalio.client import Client
from temporalio.worker import Worker
from app.temporal.activities import *
from app.temporal.workflows import *
from app.api.endpoints.rules import discord
from app.api.endpoints.auth import asana_auth_router
from app.api.endpoints.migration import user_mapping_router


app = FastAPI(title="Workino API", version="0.1.0")


@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle all OPTIONS requests for CORS preflight"""
    return {"message": "OK"}


BACKEND_CORS_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:80",
    "http://rabbitmq.localhost",
    "https://api.workino.co",
    "https://app.asana.works",
    "https://app.workino.co",
    "https://app.asana.com",
    "https://app-kf1d0jof8-omtera-dev.vercel.app",
    "https://*.vercel.app",
    "https://*.vercel.app/*",
    "https://app-b2cvht7dd-omtera-dev.vercel.app",
]

# Set all CORS enabled origins.
if BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(homepage.router, prefix="", tags=["ui"])
app.include_router(auth_router)
app.include_router(asana_to_asana_migrator.router, tags=["workflows"])
app.include_router(workflow_page.router, prefix="", tags=["ui"])
app.include_router(temporal_workflow_info_query.router, tags=["ui"])
app.include_router(discord.router, prefix="/rules", tags=["rules"])
app.include_router(migration_page.router, tags=["ui"])
app.include_router(migration_workflow.router, tags=["workflows"])
app.include_router(asana_auth_router, tags=["auth"])
app.include_router(user_mapping_router, prefix="/migration", tags=["migration"])
