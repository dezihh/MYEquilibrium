from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest

from Api.lifespan import lifespan, lifespan_dev
from Api.models.ServerInfo import ServerInfo
from Api.routers import commands, devices, images, scenes, websockets, macros, bluetooth, system


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and "." not in path.rsplit("/", 1)[-1]:
                return await super().get_response("index.html", scope)
            raise
        if response.status_code == 404 and "." not in path.rsplit("/", 1)[-1]:
            return await super().get_response("index.html", scope)
        return response


class CrossOriginIsolationMiddleware(BaseHTTPMiddleware):
    """Sets COOP/COEP headers required by Flutter skwasm renderer."""
    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        path = request.url.path
        if path.startswith("/gui"):
            response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
            response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        return response


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
    app.add_middleware(CrossOriginIsolationMiddleware)

    app.mount("/ui", SPAStaticFiles(directory="web", html=True), name="ui")
    app.mount("/gui", SPAStaticFiles(directory="www", html=True), name="gui")
    app.include_router(commands.router)
    app.include_router(devices.router)
    app.include_router(bluetooth.router)
    app.include_router(images.router)
    app.include_router(macros.router)
    app.include_router(scenes.router)
    app.include_router(websockets.router)
    app.include_router(system.router)

    @app.get("/", include_in_schema=False)
    def root_redirect():
        return RedirectResponse(url="/ui/")

    @app.get("/info", tags=["Info"], response_model=ServerInfo)
    def app_info():
        return ServerInfo()

    return app