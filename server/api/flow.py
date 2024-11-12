import os.path
import json

from datetime import datetime
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select, func
from pydantic import BaseModel

from server.model import (SessionDep, Flow, FlowCreate, FlowRead, FlowDetail, 
                          FlowUpdate, FlowNode, FlowEdge)
from server.util.flow.record import record_ui_flow
from server.util.flow.gen import mk_flow
from server.common.constant import FlowStatus

flow_dir = os.path.join(os.path.dirname(__file__), 'flow_data')

def _update_flow(session: SessionDep, flow: Flow, toUpdateInfo: dict):
    flow.sqlmodel_update(toUpdateInfo)
    session.add(flow)
    if toUpdateInfo.get('info') and toUpdateInfo['info'].get('nodes'):
        flow_info = toUpdateInfo['info']
        FlowNode.multi_create_or_update(session, flow, flow_info['nodes'])
        FlowEdge.multi_create_or_update(session, flow, flow_info.get('edges') or [])

    session.commit()

def ui_ops_to_flow(session: SessionDep, task_uuid: str):
    flow = session.exec(select(Flow).where(Flow.task_uuid == task_uuid)).first()
    if not flow:
        raise Exception(f'flow row not found in db, task_uuid:{task_uuid}')
    status = FlowStatus.ready.value
    work_dir = os.path.join('./flow_data', task_uuid)
    try:
        status = FlowStatus.collecting.value
        _update_flow(session, flow, {'status': status})

        record_ui_flow(work_dir)
        flow_info = mk_flow(work_dir)

        status = FlowStatus.success.value
        _update_flow(session, flow, {'info': flow_info, 'status': status})
    except Exception as e:
        status = FlowStatus.failed.value
        print(f'create flow from ui operations collection error: {e}')
        import traceback;traceback.print_exc()
        _update_flow(session, flow, {'status': status})
    
router = APIRouter(
    prefix='/flows',
    tags=['flows'],
)

class FlowsPagination(BaseModel):
    items: list[FlowRead] = []
    page: int = 1
    page_size: int = 10
    total: int

@router.get('')
async def get_flows(session: SessionDep,
                   page: int=1, page_size: int=10) -> FlowsPagination:
    statement = select(Flow).offset((page-1)*page_size).limit(page_size)
    flows = session.exec(statement).all()
    total = session.exec(select(func.count(Flow.id))).one()
    return {
        'items': flows,
        'page': page,
        'page_size': page_size,
        'total': total
    }
    
@router.post('')
async def create_flow(flow_create: FlowCreate,
                     session: SessionDep, background_tasks: BackgroundTasks,
                     ) -> FlowDetail:
    task_uuid = datetime.now().strftime('%Y%m%d%H%M%S')
    flow = Flow(name=flow_create.name, task_uuid=task_uuid, create_at=datetime.now(), update_at=datetime.now())
    session.add(flow)
    try:
        session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    background_tasks.add_task(ui_ops_to_flow, session=session, task_uuid=task_uuid)
    return flow
    
@router.get('/{flow_id}')
async def get_flow_detail(session: SessionDep,
                         flow_id: int) -> FlowDetail:
    flow = session.exec(select(Flow).where(Flow.id == flow_id)).first()
    return FlowDetail.from_flow_record(flow)

@router.put('/{flow_id}')
async def update_flow(session: SessionDep, flow_id: int, flow_update: FlowUpdate) -> FlowDetail:
    flow = session.exec(select(Flow).where(Flow.id == flow_id)).first()
    flow.sqlmodel_update(flow_update)
    session.add(flow)
    session.commit()
    return flow

@router.delete('/{flow_id}')
async def delete_flow(session: SessionDep, flow_id: int):
    flow = session.exec(select(Flow).where(Flow.id == flow_id)).first()
    pass






