from fastapi import APIRouter, HTTPException
from starlette.requests import Request

from Api.models.Status import StatusReport
from RemoteController.RemoteController import RemoteController

router = APIRouter(
    prefix="/system",
    tags=["System"],
    responses={404: {"description": "Not found"}}
)

@router.get("/status", tags=["System"], response_model=StatusReport)
def get_current_system_status(request: Request) -> StatusReport:
    controller: RemoteController = request.state.controller

    return controller.get_current_status()


@router.get("/ha/lights", tags=["System"], response_model=list[str])
def get_home_assistant_lights(request: Request) -> list[str]:
    controller: RemoteController = request.state.controller

    if controller.ha_manager is None:
        raise HTTPException(status_code=503, detail="HA integration is not configured on this hub.")

    lights = controller.ha_manager.get_lights()
    result: list[str] = []
    for light in lights:
        entity_id = getattr(light, "entity_id", None)
        if isinstance(entity_id, str):
            result.append(entity_id)
        else:
            result.append(str(light))

    return result