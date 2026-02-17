from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from pathlib import Path
import logging

from Api.lifespan import lifespan, lifespan_dev
from Api.models.ServerInfo import ServerInfo
from Api.routers import commands, devices, images, scenes, websockets, macros, bluetooth, system


def app_generator(dev: bool = False):
    if dev:
        app = FastAPI(lifespan=lifespan_dev)
    else:
        app = FastAPI(lifespan=lifespan)

    app.mount("/ui", StaticFiles(directory="web", html=True), name="ui")

    gui_dist = Path("gui/dist")
    if gui_dist.is_dir():
        app.mount("/gui", StaticFiles(directory=str(gui_dist), html=True), name="gui")
    else:
        logging.getLogger("equilibrium.gui").warning(
            "GUI build missing: %s (run 'cd gui && npm run build' to enable /gui)",
            gui_dist,
        )
    app.include_router(commands.router)
    app.include_router(devices.router)
    app.include_router(bluetooth.router)
    app.include_router(images.router)
    app.include_router(macros.router)
    app.include_router(scenes.router)
    app.include_router(websockets.router)
    app.include_router(system.router)

    landing_path = Path(__file__).with_name("landing.html")

    @app.get("/", include_in_schema=False)
    def landing():
        return HTMLResponse(landing_path.read_text(encoding="utf-8"))

    @app.get("/info", tags=["Info"], response_model=ServerInfo)
    def app_info():
        return ServerInfo()

    return app