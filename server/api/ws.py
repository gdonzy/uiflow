from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlmodel import SQLModel

router = APIRouter()
socket = None

def get_socket():
    global socket
    return socket


async def ws_send_msg(msg: dict | SQLModel):
    if isinstance(msg, SQLModel):
        msg = jsonable_encoder(msg)

    socket = get_socket()
    if socket:
        await socket.send_json(msg)

@router.websocket('/ws/flow')
async def ws_flow(websocket: WebSocket):
    global socket
    await websocket.accept()
    socket = websocket
    try:
        while True:
            data = await websocket.receive_text()
            print(f'receive flow ws data: {data}')
    except WebSocketDisconnect:
        del socket

