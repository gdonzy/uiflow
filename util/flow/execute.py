import os
import json
import time

from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyController

mouse = MouseController()
keyboard = KeyController()

def _exec_mouse(op_info):
    mouse.position = (op_info['x'], op_info['y'])
    mouse.move(0, 0)
    if 'left' in op_info['button']:
        button = Button.left
    elif 'right' in op_info['button']:
        button = Button.right
    if op_info['type'] == 'press':
        mouse.press(button)
    elif op_info['type'] == 'release':
        mouse.release(button)

def _exec_key(op_info):
    if op_info['type'] == 'press':
        keyboard.press(op_info['key'])
    elif op_info['type'] == 'release':
        keyboard.release(op_info['key'])
        
def _exec_control(op_info):
    if op_info['type'] == 'press':
        keyboard.press(getattr(Key, op_info['key'][4:]))
    elif op_info['type'] == 'release':
        keyboard.release(getattr(Key, op_info['key'][4:]))
        
    time.sleep(op_info.get('time') or 0)
    
def _exec_sleep(op_info):
    time.sleep(op_info.get('time') or 0)

def exec_node(node):
    op_exec = {
        'mouse': _exec_mouse,
        'key': _exec_key,
        'control': _exec_control,
        'sleep': _exec_sleep,
    }

    if not node.get('data') or not node['data'].get('op_list'):
        return

    op_type = node['data'].get('op_type')
    op_list = node['data'].get('op_list')
    prev_base_ts, prev_orig_ts = round(time.time(), 2), round(op_list[0]['ts'], 2)
    for op_info in op_list:
        sleep_duration = (round(op_info['ts'], 2) - prev_orig_ts) - (round(time.time(), 2) - prev_base_ts)
        # 第一次sleep_duration小于0
        if sleep_duration > 0.0:
            time.sleep(sleep_duration)
        prev_base_ts, prev_orig_ts = round(time.time(), 2), round(op_info['ts'], 2)
        op_exec[op_type](op_info)

def exec_flow(work_dir):
    with open(os.path.join(work_dir, 'flow.json')) as f:
        flow = json.load(f)
    node_list, edge_list = flow['nodes'], flow['edges']

    # 一个node可能有多个输入边，一个node只能有一个输出边
    edge_map = {
        's2t': {}, # source to target
        't2s': {} # target to source
    }
    for edge in edge_list:
        edge_map['s2t'][edge['source']] = edge['target']
        if edge['target'] not in edge_map['t2s']:
            edge_map['t2s'][edge['target']] = []
        edge_map['t2s'][edge['target']].append(edge['source'])
    node_map = {
        node['id']: node
        for node in node_list
    }

    relay_nodes = {node_list[0]['id']: node_list[0]}
    prev_node_ts = None
    while len(relay_nodes) > 0:
        print(relay_nodes)
        # 遍历已完成节点，后续节点添加到relay_nodes，清理之前已完成节点
        done = {
            id_: node
            for id_, node in relay_nodes.items()
            if node.get('status') == 'done'
        }
        done_ids = list(done.keys())
        for s_id in done_ids:
            t_id = edge_map['s2t'].get(s_id)
            if not t_id or \
               t_id in relay_nodes:
                # 完成节点后没有输出边 或 输出边的节点已经添加到relay_nodes了
                del relay_nodes[s_id]
            all_s_ids = edge_map['t2s'].get(t_id) or []
            # 一个node可能有多个输入边，一个node只能有一个输出边
            if all_s_ids and set(all_s_ids) & set(done_ids) == set(all_s_ids):
                relay_nodes[t_id] = node_map[t_id]
                del relay_nodes[s_id]

        # 遍历未执行节点，执行至完成
        todo = {
            id_: node
            for id_, node in relay_nodes.items()
            if not node.get('status') or node['status'] == 'todo'
        }
        for _, node in todo.items():
            try:
                exec_node(node)
                relay_nodes[node['id']]['status'] = 'done'
            except Exception as e:
                print(f'exec node error: {e}')
                relay_nodes[node['id']]['status'] = 'fail'
                
        # 如果有节点执行失败，则停止
        fail = {
            id_: node
            for id_, node in relay_nodes.items()
            if node.get('status') == 'fail'
        }
        if fail:
            break

if __name__ == '__main__':
    exec_flow('/Users/donzy/stov/uiflow/flow_data/20241010161832')