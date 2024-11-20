import os
from typing import Annotated
from datetime import datetime

from sqlmodel import Session, SQLModel, create_engine
from fastapi import Depends
from .flow import (FlowCreate, FlowUpdate, FlowRead, FlowDetail, Flow,
                  FlowNode, FlowNodeRead, FlowEdge, FlowEdgeRead)
from .exec_log import (ExecLog, ExecLogCreate, ExecLogRead, ExecLogDetail,
                       ExecLogStatus, FlowNodeStatus)
if os.environ.get('UIFLOW_WORK_DIR'):
    sqlite_url = f'sqlite:///{os.environ["UIFLOW_WORK_DIR"]}/db.sqlite'
else:
    sqlite_url = 'sqlite:///db.sqlite'

connect_args = {'check_same_thread': False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]

__all__ = [
    'create_db_and_tables', 'SessionDep',
    'Flow', 'FlowCreate', 'FlowUpdate', 'FlowRead', 'FlowDetail',
    'ExecLog', 'ExecLogCreate', 'ExecLogRead', 'ExecLogDetail', 'ExecNode', 'ExecLogStatus', 'FlowNodeStatus'
]