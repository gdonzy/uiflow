import asyncio

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlmodel import select, func

from server.model import SessionDep, Flow, FlowNode, FlowNodeRead, FlowEdgeRead, ExecLog, ExecLogCreate, ExecLogRead, ExecLogDetail, ExecLogStatus, FlowNodeStatus
from server.util.flow.execute import exec_flow
from server.api.ws import ws_send_msg

def exec_flow_task(session: SessionDep, log_id: int):

    log = session.get(ExecLog, log_id)
    flow = session.get(Flow, log.flow_id)
    nodes = session.exec(select(FlowNode).where(FlowNode.flow_id == log.flow_id)).all()
    id_node_map = {
        node.node_id: node for node in nodes
    }

    def update_node_indb(node_list: list[FlowNode]):
        if not node_list:
            return
        for node in node_list:
            session.add(node)
        session.commit()
        asyncio.run(
            ws_send_msg({
                'msg_type': 'node_status',
                'flow_id': str(node_list[0].flow_id),
                'nodes': jsonable_encoder(FlowNodeRead.from_flow_nodes(node_list))
            })
        )
    
    flow_info = {
        'nodes': flow.nodes,
        'edges': flow.edges,
    }
    # 初始化所有节点状态为ready
    for node in flow_info['nodes']:
        node.status = FlowNodeStatus.ready.value
    update_node_indb(flow_info['nodes'])
    # 执行
    succ = exec_flow(flow_info, update_node_indb_func=update_node_indb)
    log.sqlmodel_update({
        'status': ExecLogStatus.success.value if succ else ExecLogStatus.failed.value,
        'result': {
            'nodes': jsonable_encoder(FlowNodeRead.from_flow_nodes(flow_info['nodes'])),
            'edges': jsonable_encoder(FlowEdgeRead.from_flow_edges(flow_info['edges'])),
        },
    })
    session.commit()

router = APIRouter(
    prefix='/exec',
    tags=['exec'],
)

class LogsPagination(BaseModel):
    items: list[ExecLogRead] = [],
    page: int = 1,
    page_size: int = 10,
    total: int

@router.get('')
async def get_exec_logs(session: SessionDep,
                        page: int=1, page_size: int=10) -> LogsPagination:
    statement = select(ExecLog).offset((page-1)*page_size).limit(page_size)
    logs = session.exec(statement).all()
    total = session.exec(select(func.count(ExecLog.id))).one()
    return {
        'items': logs,
        'page': page,
        'page_size': page_size,
        'total': total
    }
    
@router.post('')
async def exec_flow_to_record(session: SessionDep, background_tasks: BackgroundTasks,
                             exec_create: ExecLogCreate) -> ExecLogDetail:
    statement = select(Flow).where(Flow.id == exec_create.flow_id)
    flow = session.exec(statement).first()
    exec_log = ExecLog.create(session, flow)
    background_tasks.add_task(exec_flow_task, session=session, log_id=exec_log.id)
    return exec_log

@router.delete('/{log_id}')
async def delete_exec_log(session: SessionDep, log_id: int):
    log = session.get(ExecLog, log_id)
    if not log:
        raise HTTPException(status_code=404, detail='log not found')
    session.delete(log)
    session.commit()
