from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlmodel import select, func

from server.model import SessionDep, Flow, ExecLog, ExecLogCreate, ExecLogRead, ExecLogDetail, ExecNode, ExecLogStatus, ExecNodeStatus
from server.util.flow.execute import exec_flow

def exec_flow_task(session: SessionDep, log_id: int):
    log = session.get(ExecLog, log_id)
    nodes = session.exec(select(ExecNode).where(ExecNode.log_id == log_id)).all()
    id_node_map = {
        node.node_id: node for node in nodes
    }

    def update_node_indb(nodes_: list[ExecNode]):
        if not nodes_:
            return
        for node_ in nodes_:
            id_node_map[node_['id']].sqlmodel_update({
                'status': node_['status'],
            })
            session.add(id_node_map[node_['id']])
        session.commit()

    flow_info = log.flow_info
    succ = exec_flow(flow_info, update_node_indb_func=update_node_indb)
    nodes = session.exec(select(ExecNode).where(ExecNode.log_id == log_id)).all()
    id_node_map = {
        node.node_id: node for node in nodes
    }
    for node in flow_info['nodes']:
        node['status'] = id_node_map[node['id']].status
    log.sqlmodel_update({
        'status': ExecLogStatus.success.value if succ else ExecLogStatus.failed.value,
        'flow_info': flow_info
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
    exec_log = ExecLog.create(session, flow.id, flow.info)
    background_tasks.add_task(exec_flow_task, session=session, log_id=exec_log.id)
    return exec_log

@router.get('/{log_id}')
async def get_exec_log_detail(session: SessionDep,
                              log_id: int) -> ExecLogDetail:
    log = session.get(ExecLog, log_id)
    if log.status not in (ExecLogStatus.success, ExecLogStatus.failed):
        nodes = session.exec(select(ExecNode).where(ExecNode.log_id == log_id)).all()
        id_node_map = {
            node.node_id: node for node in nodes
        }
        for node in log.info['nodes']:
            node['status'] = id_node_map[node['id']].status
            node['result'] = id_node_map[node['id']].result
        
    return log
