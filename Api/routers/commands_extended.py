"""
Extended Commands Router - Search & IR Code Operations
"""

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from Api.models.Command import Command, CommandWithRelationships
from DbManager.DbManager import SessionDep

import json

router = APIRouter(
    prefix="/commands",
    tags=["Commands"],
    responses={404: {"description": "Not found"}}
)


@router.get("/search", response_model=list[dict])
def search_commands(name: str = None, device_id: int = None, command_type: str = None, session: SessionDep = None):
    """
    Search for commands with optional filters.
    
    **Beispiele:**
    - GET `/commands/search?name=moon` – Findet alle Commands mit "moon" im Namen
    - GET `/commands/search?device_id=2` – Alle Commands für Device ID 2
    - GET `/commands/search?command_type=CommandType.IR` – Nur IR Commands
    
    Args:
        name: Filter by command name (partial match, case-insensitive)
        device_id: Filter by device ID
        command_type: Filter by command type (e.g., "CommandType.IR", "CommandType.BLUETOOTH")
    
    Returns:
        List of commands with device information and action types
    """
    query = select(Command)
    
    if name:
        query = query.where(Command.name.ilike(f"%{name}%"))
    if device_id is not None:
        query = query.where(Command.device_id == device_id)
    if command_type:
        query = query.where(Command.type == command_type)
    
    commands = session.exec(query).all()
    
    result = []
    for cmd in commands:
        result.append({
            "id": cmd.id,
            "name": cmd.name,
            "device_id": cmd.device_id,
            "device_name": cmd.device.name if cmd.device else "Unknown",
            "type": str(cmd.type),
            "has_ir_code": bool(cmd.ir_action),
            "has_bt_action": bool(cmd.bt_action),
            "has_network_action": bool(cmd.host and cmd.method),
            "has_integration_action": bool(cmd.integration_action)
        })
    
    return result


@router.get("/{command_id}/ir-code", tags=["Commands"])
def get_command_ir_code(command_id: int, session: SessionDep):
    """
    Get the IR code array for a specific command.
    
    **Beispiel:**
    - GET `/commands/5/ir-code` – Holt den Moon IR-Code
    
    Args:
        command_id: ID of the command
    
    Returns:
        IR code as array of mark/space values (microseconds),
        code length, and device information
    """
    command = session.get(Command, command_id)
    if not command:
        raise HTTPException(status_code=404, detail="Command not found")
    
    if not command.ir_action:
        raise HTTPException(status_code=400, detail="Command has no IR code")
    
    try:
        ir_code = json.loads(command.ir_action) if isinstance(command.ir_action, str) else command.ir_action
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse IR code")
    
    return {
        "command_id": command.id,
        "command_name": command.name,
        "device_id": command.device_id,
        "device_name": command.device.name if command.device else "Unknown",
        "ir_code": ir_code,
        "code_length": len(ir_code),
        "code_description": f"Mark/Space array: {len(ir_code)} values in microseconds"
    }
