import os
import json

def step_group_type(step):
    type_ = None
    if step.get('key'):
        type_ = 'key' if len(step['key']) == 1 else 'control'
    else:
        type_ = 'mouse'
    return type_

def aggregate_steps(steps):
    # key combination
    group_list = []
    if not steps:
        return group_list

    group = {"steps": [steps[0]]}
    group['type'] = step_group_type(steps[0])
    for step in steps[1:]:
        if group['type'] == step_group_type(step):
            group['steps'].append(step)
        else:
            group_list.append(group)
            group = {
                "type": step_group_type(step),
                'steps': [step]
            }
            
    return group_list

def gen_node_by_group(group, curr_id):
    labels = {
        'key': '按键',
        'control': '控制按键或组合按键',
        'mouse': '鼠标点击',
        'sleep': '间隔时间',
    }
    node = {
        "id": str(curr_id),
        "type": "uiop",
        "data": {
            "label": labels[group['type']],
            "status": 0,
            'op_type': group['type'],
            'op_list': group.get('steps') or []
        },
    }
    return node

def mk_flow(work_dir):
    """
    {
        "nodes": [
            {
                "id": "1",
                "type": "start/uiop/end",
                "data": {"label": "Node 1", "op_type": "key", "op_list": []},
            },
            ...
        ]
        "edges": [
            {
                "id": "e1-2",
                "source": "1",
                "target": "2",
            },
            ...
        ]
    }
    """
    with open(os.path.join(work_dir, 'key_records.json')) as f:
        key_steps = json.load(f)
    with open(os.path.join(work_dir, 'mouse_records.json')) as f:
        mouse_steps = json.load(f)
    steps = key_steps + mouse_steps
    steps = sorted(steps, key=lambda x:x['ts'])
    
    group_list = aggregate_steps(steps)
    
    curr_id, node_list, edge_list = 2, [{'id': "1", "type": "start", "data": {"label": "开始", "status": 0}}], []
    last_ts = None
    for group in group_list:
        if last_ts and group.get('steps'):
            node_list.append(gen_node_by_group({
                'type': 'sleep',
                'steps': [{
                    'time': round((group['steps'][0]['ts'] - last_ts), 2),
                    'type':'sleep',
                    'ts': group['steps'][0]['ts']
                }]
            }, curr_id))
            curr_id += 1
        node_list.append(gen_node_by_group(group, curr_id))
        curr_id += 1
        last_ts = group['steps'][-1]['ts'] if group.get('steps') else None
    node_list.append({'id': str(curr_id), 'type': 'end', 'data': {'label': '结束', 'status': 0}})
    for idx, node in enumerate(node_list[:-1]):
        next = node_list[idx+1]
        edge_list.append({'id': f'e{node["id"]}-{next["id"]}', 'source': node["id"], "target": next["id"]})
        
    flow = {
        'nodes': node_list,
        'edges': edge_list
    }
    with open(os.path.join(work_dir, 'flow.json'), 'w') as f:
        json.dump(flow, f)
        
    return flow

if __name__ == '__main__':
    mk_flow('/Users/donzy/stov/uiflow/flow_data/20241010161832')