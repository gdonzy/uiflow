from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column
from server.common.constant import ExecLogStatus, ExecNodeStatus
    
# exec log models
class ExecLogBase(SQLModel):
    flow_info: dict = Field(sa_column=Column(JSON), default={})
    status: int = Field(default=0) # 0:ready 1:running 2:success 3:failed
    result: dict = Field(sa_column=Column(JSON), default={})
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime
    
class ExecLog(ExecLogBase, table=True):
    id: int = Field(default=None, primary_key=True)
    flow_id: int = Field(default=None)
    
    @classmethod
    def create(cls, session, flow_id: int, flow_info: dict):
        log = cls(
            flow_id=flow_id,
            flow_info=flow_info,
            update_at=datetime.now()
        )
        session.add(log)
        session.commit()
        ExecNode.multi_create(session, log.id, flow_info['nodes'])
        session.refresh(log)
        return log
    
class ExecLogCreate(SQLModel):
    flow_id: int = Field(default=None)

class ExecLogRead(SQLModel):
    id: int = Field(default=None, primary_key=True)
    flow_id: int = Field(default=None)
    status: int = Field(default=0) # 0:ready 1:running 2:success 3:failed
    result: dict = Field(sa_column=Column(JSON), default={})
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime
    
class ExecLogDetail(ExecLogRead):
    flow_info: dict = Field(sa_column=Column(JSON), default={})

# exec node models
class ExecNode(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    log_id: int = Field(default=None)
    node_id: int = Field(default=None)
    status: int = Field(default=0) # 0:ready 1:running 2:success 3:failed
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime
    
    @classmethod
    def multi_create(cls, session, log_id: int, nodes: list[dict]):
        for node_info in nodes:
            node_ = cls(
                log_id=log_id,
                node_id=node_info['id'],
                update_at=datetime.now()
            )
            session.add(node_)
        session.commit()



