from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
socket = None

def get_socket():
    return socket

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

