import json
from fastapi import APIRouter, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlmodel import SQLModel, select

from server.api.ws import get_socket
from server.model import SessionDep, Flow

router = APIRouter(
    prefix='/test',
    tags=['test'],
)

socket = get_socket()

async def ws_send_flow_msg(msg: dict | SQLModel):
    global socket
    if isinstance(msg, SQLModel):
        msg = jsonable_encoder(msg)
    if not socket:
        socket = get_socket()
    if socket:
        await socket.send_json(msg)

@router.post('')
async def test_bg_task(session: SessionDep, bg_tasks: BackgroundTasks):
    flow = session.exec(select(Flow)).first()
    bg_tasks.add_task(ws_send_flow_msg, flow)