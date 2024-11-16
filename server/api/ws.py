import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from sqlmodel import SQLModel

router = APIRouter()
sockets = {}

async def ws_send_msg(msg: dict | SQLModel):
    if isinstance(msg, SQLModel):
        msg = jsonable_encoder(msg)

    global sockets
    for socket in sockets.values():
        try:
            await socket.send_json(msg)
        except Exception as e:
            print(f'websocket send msg error:{e}')

@router.websocket('/ws/flow')
async def ws_flow(websocket: WebSocket):
    socket_id = str(uuid.uuid1())
    await websocket.accept()
    sockets[socket_id] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            print(f'receive flow ws data: {data}')
    except WebSocketDisconnect:
        if socket_id in sockets:
            del sockets[socket_id]

