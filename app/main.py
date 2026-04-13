from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.devices import router as devices_router
from app.api.imports import router as imports_router
from app.api.rides import router as rides_router
from app.config import settings
from app.db import init_db
from app.services.device_service import device_service
from app.services.ride_service import ride_service


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    templates = Jinja2Templates(directory="app/templates")

    @app.on_event("startup")
    def startup_event() -> None:
        init_db()
        device_service.refresh_devices()

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    app.include_router(devices_router, prefix="/api")
    app.include_router(rides_router, prefix="/api")
    app.include_router(imports_router, prefix="/api")

    @app.get("/", response_class=HTMLResponse)
    def dashboard(request: Request):
        device_service.refresh_devices()
        devices = device_service.list_devices()
        rides = ride_service.list_rides()

        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "app_name": settings.app_name,
                "devices": [dict(device) for device in devices],
                "rides": [dict(ride) for ride in rides],
            },
        )

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    return app


app = create_app()