from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON, Column

class FlowBase(SQLModel):
    name: str = Field(index=True, unique=True)
    task_uuid: str | None = Field(index=True, unique=True, default=None)
    status: int = Field(default=0) # 0:ready 1:collecting ui operations 2:success 3:failed
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime

class Flow(FlowBase, table=True):
    id: int = Field(default=None, primary_key=True)
    info: dict = Field(sa_column=Column(JSON), default={})
    
class FlowCreate(SQLModel):
    name: str = Field(index=True, unique=True)
    
class FlowUpdate(SQLModel):
    info: dict = Field(sa_column=Column(JSON), default={})
    
class FlowRead(FlowBase):
    id: int = Field(default=None, primary_key=True)

class FlowDetail(FlowBase):
    id: int = Field(default=None, primary_key=True)
    info: dict = Field(sa_column=Column(JSON), default={})
