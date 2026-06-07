from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from app.core.config import settings
from app.api.endpoints import router as api_router

def create_app() -> FastAPI:
    """Application factory for IDD."""
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
    )

    # Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(api_router, prefix=settings.api_prefix)

    # Static Files for Frontend
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/")
    def read_root():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/static/index.html")

    return app

app = create_app()
