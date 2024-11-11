import os.path
import json

from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .model import create_db_and_tables, SessionDep, Flow, FlowCreate
from .api import flow, exec_log, ws, test


static_path = os.path.join(os.path.dirname(__file__), 'static')

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=static_path), name='static')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
app.include_router(flow.router)
app.include_router(exec_log.router)
app.include_router(ws.router)
app.include_router(test.router)

@app.get('/')
def index():
    return FileResponse(f'{static_path}/index.html')

