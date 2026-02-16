from fastapi import APIRouter, HTTPException
from sqlmodel import select
from starlette.requests import Request

from Api.models.Command import Command, CommandBase, CommandWithRelationships
from Api.models.Device import Device
from Api.models.CommandType import CommandType
from Api.models.IntegrationAction import IntegrationAction
from DbManager.DbManager import SessionDep
from IrManager.IrProtocolDetector import detect_protocol
from RemoteController.RemoteController import RemoteController

router = APIRouter(
    prefix="/commands",
    tags=["Commands"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", tags=["Commands"], response_model=CommandWithRelationships)
def create_command(command: CommandBase, session: SessionDep) -> CommandWithRelationships:
    db_command = Command.model_validate(command)
    if db_command.type == CommandType.IR and not db_command.ir_action:
        raise HTTPException(status_code=400, detail="IR commands can only be created via WebSocket. Please use the /ws/commands endpoint.")
    elif db_command.type == CommandType.NETWORK and not db_command.host:
        raise HTTPException(status_code=400, detail="Network commands require a host to be set.")
    elif db_command.type == CommandType.NETWORK and not db_command.method:
        raise HTTPException(status_code=400, detail="Network commands require a method to be set.")
    elif db_command.type == CommandType.BLUETOOTH and not db_command.bt_action and not db_command.bt_media_action:
        raise HTTPException(status_code=400, detail="Bluetooth commands require either an action or a media action.")
    elif db_command.type == CommandType.INTEGRATION and not db_command.integration_action:
        raise HTTPException(status_code=400, detail="Integration commands require an integration action.")
    elif db_command.integration_action == IntegrationAction.TOGGLE_LIGHT and not db_command.integration_entity:
        raise HTTPException(status_code=400, detail="A toggle_light command requires an entity.")

    if command.device_id is not None:
        db_device = session.get(Device, command.device_id)
        if not db_device:
            raise HTTPException(status_code=400, detail=f"There is no device with id {command.device_id}.")
        db_command.device = db_device

    session.add(db_command)
    session.commit()
    session.refresh(db_command)
    return db_command

@router.get("/", tags=["Commands"], response_model=list[CommandWithRelationships])
def list_commands(session: SessionDep) -> list[CommandWithRelationships]:
    commands = session.exec(select(Command)).all()
    return commands

@router.get("/search/{query}", tags=["Commands"])
def search_commands(query: str, session: SessionDep) -> list[CommandWithRelationships]:
    """
    Search commands by name or device.
    Returns all matching commands with their device info.
    """
    commands = session.exec(select(Command)).all()
    query_lower = query.lower()
    
    results = []
    for cmd in commands:
        cmd_match = query_lower in cmd.name.lower()
        device_match = cmd.device and query_lower in cmd.device.name.lower()
        if cmd_match or device_match:
            results.append(cmd)
    
    return results

@router.get("/{command_id}/ir-code", tags=["Commands"])
def get_ir_code(command_id: int, session: SessionDep):
    """
    Get IR code of a command with protocol detection.
    
    Returns:
    - code: IR code as array of mark/space microseconds
    - protocol: Detected protocol (NEC, JVC, SONY_SIRC, etc.)
    - confidence: Detection confidence (0..1)
    - device: Associated device name
    """
    command = session.get(Command, command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    if command.type != CommandType.IR:
        raise HTTPException(status_code=400, detail="Command is not an IR command")
    
    if not command.ir_action:
        raise HTTPException(status_code=400, detail="Command has no IR code")
    
    # Detect protocol
    protocol_info = detect_protocol(command.ir_action)
    
    return {
        "command_id": command.id,
        "command_name": command.name,
        "device_id": command.device_id,
        "device_name": command.device.name if command.device else None,
        "code": command.ir_action,
        "code_length": len(command.ir_action),
        "protocol": protocol_info["protocol"],
        "confidence": protocol_info["confidence"],
        "details": protocol_info["details"]
    }

@router.get("/{command_id}", tags=["Commands"], response_model=CommandWithRelationships)
def show_command(command_id: int, session: SessionDep) -> CommandWithRelationships:
    command = session.get(Command, command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    return command

@router.post("/{command_id}/send", tags=["Commands"])
async def send_command(command_id: int, request: Request):
    controller: RemoteController = request.state.controller
    return await controller.send_command(command_id)

@router.delete("/{command_id}", tags=["Commands"])
def delete_command(command_id: int, session: SessionDep):
    command = session.get(Command, command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    session.delete(command)
    session.commit()
    return {"ok": True}