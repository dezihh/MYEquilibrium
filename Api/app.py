from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from Api.lifespan import lifespan, lifespan_dev
from Api.models.ServerInfo import ServerInfo
from Api.routers import commands, devices, images, scenes, websockets, macros, bluetooth, system


def app_generator(dev: bool = False):
    if dev:
        app = FastAPI(lifespan=lifespan_dev)
    else:
        app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:1420",
            "http://127.0.0.1:1420",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/ui", StaticFiles(directory="web", html=True), name="ui")
    app.include_router(commands.router)
    app.include_router(devices.router)
    app.include_router(bluetooth.router)
    app.include_router(images.router)
    app.include_router(macros.router)
    app.include_router(scenes.router)
    app.include_router(websockets.router)
    app.include_router(system.router)

    @app.get("/", include_in_schema=False)
    def root_info():
        return ServerInfo()

    @app.get("/info", tags=["Info"], response_model=ServerInfo)
    def app_info():
        return ServerInfo()

    return app