from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import JSON, Column
from server.common.constant import ExecLogStatus, FlowNodeStatus
from server.model import Flow
    
# exec log models
class ExecLogBase(SQLModel):
    status: int = Field(default=0) # 0:ready 1:running 2:success 3:failed
    result: dict = Field(sa_column=Column(JSON), default={})
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)
    
class ExecLog(ExecLogBase, table=True):
    id: int = Field(default=None, primary_key=True)
    flow_id: int = Field(default=None, foreign_key='flow.id')
    flow: Flow = Relationship(back_populates='exec_logs')
    
    @property
    def flow_name(self):
        return self.flow.name
    
    @classmethod
    def create(cls, session, flow):
        log = cls(
            flow_id=flow.id,
        )
        session.add(log)
        session.commit()
        return log
    
class ExecLogCreate(SQLModel):
    flow_id: int = Field(default=None)

class ExecLogRead(SQLModel):
    id: int = Field(default=None, primary_key=True)
    flow_id: int = Field(default=None)
    flow_name: str
    status: int = Field(default=0) # 0:ready 1:running 2:success 3:failed
    result: dict = Field(sa_column=Column(JSON), default={})
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime
    
class ExecLogDetail(ExecLogRead):
    pass

