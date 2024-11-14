from datetime import datetime
from sqlmodel import Field, SQLModel, select, Relationship
from sqlalchemy import JSON, Column

class FlowBase(SQLModel):
    name: str = Field(index=True, unique=True)
    task_uuid: str | None = Field(index=True, unique=True, default=None)
    status: int = Field(default=0) # 0:ready 1:collecting ui operations 2:success 3:failed
    create_at: datetime = Field(default_factory=datetime.now)
    update_at: datetime = Field(default_factory=datetime.now)

class Flow(FlowBase, table=True):
    id: int = Field(default=None, primary_key=True)
    nodes: list["FlowNode"] = Relationship(back_populates='flow')
    edges: list["FlowEdge"] = Relationship(back_populates='flow')
    
    def update_nodes_edges(self, session):
        self.nodes = session.exec(
            select(FlowNode).where(FlowNode.flow_id == self.id)
        ).all()
        self.edges = session.exec(
            select(FlowEdge).where(FlowEdge.flow_id == self.id)
        ).all()
    
class FlowCreate(SQLModel):
    name: str = Field(index=True, unique=True)
    
class FlowUpdate(SQLModel):
    info: dict = Field(sa_column=Column(JSON), default={})
    
class FlowRead(FlowBase):
    id: int = Field(default=None, primary_key=True)
    
class FlowNodeBase(SQLModel):
    type: str = Field(default='uiop')
    status: int = Field(default=0) # 0:ready 1:running 2:success 3:failed
    label: str = Field(default='')
    position: dict = Field(sa_column=Column(JSON), default={})
    extra: dict = Field(sa_column=Column(JSON), default={})

class FlowNode(FlowNodeBase, table=True):
    id: int = Field(index=True, primary_key=True, unique=True) # 前端页面不用id, 用node_id
    node_id: str = Field()
    flow_id: int = Field(default=None, foreign_key='flow.id')
    flow: Flow = Relationship(back_populates='nodes')
    
    @classmethod
    def multi_create_or_update(cls, session, flow, nodes, commit=False):
        node_records = flow.nodes
        nodeid_record_map = {
            nr.node_id: nr
            for nr in node_records
        }
        for node_info in nodes:
            node_id = node_info.get('node_id')
            if nodeid_record_map.get(node_id):
                node_record = nodeid_record_map.pop(node_id)
            else:
                node_record = cls(
                    flow=flow,
                    node_id=node_id,
                )
            node_record.sqlmodel_update(node_info)
            session.add(node_record)
        for node_record in nodeid_record_map.values():
            session.delete(node_record)
        if commit:
            session.commit()
    
class FlowNodeRead(FlowNodeBase):
    id: str
    data: dict
    
    @classmethod
    def from_flow_nodes(cls, flow_nodes):
        resp_node_list = []
        for flow_node_record in flow_nodes:
            resp_node_list.append(cls(
                id=flow_node_record.node_id,
                type=flow_node_record.type,
                label=flow_node_record.label,
                status=flow_node_record.status,
                position=flow_node_record.position,
                extra=flow_node_record.extra,
                data={'status': flow_node_record.status, 'id': flow_node_record.node_id}
            ))
        return resp_node_list
        
class FlowEdgeBase(SQLModel):
    source: str = Field() # node_id
    target: str = Field() # node_id

class FlowEdge(FlowEdgeBase, table=True):
    id: int = Field(index=True, primary_key=True, unique=True) # 前端页面不用id, 用edge_id
    edge_id: str = Field()
    flow_id: int = Field(default=None, foreign_key='flow.id')
    flow: Flow = Relationship(back_populates='edges')

    @classmethod
    def multi_create_or_update(cls, session, flow, edges, commit=False):
        edge_records = flow.edges
        edgeid_record_map = {
            er.edge_id: er
            for er in edge_records
        }
        for edge_info in edges:
            edge_id = edge_info.get('edge_id')
            if edgeid_record_map.get(edge_id):
                edge_record = edgeid_record_map.pop(edge_id)
            else:
                edge_record = cls(
                    flow=flow,
                    edge_id=edge_id,
                )
            edge_record.sqlmodel_update(edge_info)
            session.add(edge_record)
        for edge_record in edgeid_record_map.values():
            session.delete(edge_record)
        if commit:
            session.commit()
    
class FlowEdgeRead(FlowEdgeBase):
    id: str
    
    @classmethod
    def from_flow_edges(cls, flow_edges):
        resp_edge_list = []
        for flow_edge_record in flow_edges:
            resp_edge_list.append(cls(
                id=flow_edge_record.edge_id,
                source=flow_edge_record.source,
                target=flow_edge_record.target
            ))
        return resp_edge_list

class FlowDetail(FlowBase):
    id: int
    nodes: list[FlowNodeRead] = []
    edges: list[FlowEdgeRead] = []
    
    @classmethod
    def from_flow_record(cls, flow_record):
        return cls(
            id=flow_record.id,
            name=flow_record.name,
            task_uuid=flow_record.task_uuid,
            status=flow_record.status,
            create_at=flow_record.create_at,
            update_at=flow_record.update_at,
            nodes=FlowNodeRead.from_flow_nodes(flow_record.nodes),
            edges=FlowEdgeRead.from_flow_edges(flow_record.edges),
        )
    