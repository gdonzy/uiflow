import os
import json
import time

from PIL import ImageGrab
from datetime import datetime
from pynput import mouse, keyboard
from multiprocessing import Process


class MouseListener(object):
    
    def __init__(self, base_dir, task_uuid=None):
        if not task_uuid:
            task_uuid = datetime.now().strftime('%Y%m%d%H%M%S')
        self.base_dir = base_dir
        self.work_dir = os.path.join(self.base_dir, task_uuid)
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
        self.records = []
        
    def record_operation(self, op_info, screen_shot=False):
        """
        param:op_info示例{"type": "click", "x": 20.22, "y": 10.11, "ts": "时间戳"}
        """
        self.records.append(op_info)
        with open(os.path.join(self.work_dir, 'mouse_records.json'), 'w') as f:
            json.dump(self.records, f)
        if screen_shot:
            shot_name = f'ts{op_info["ts"]}_{op_info["type"]}_{op_info["x"]}_{op_info["y"]}.png'
            shot_path = os.path.join(self.work_dir, shot_name)
            op_info['screen_shot'] = shot_name
            screenshot = ImageGrab.grab()
            screenshot.save(shot_path)
            screenshot.close()
    
    def on_move(self, x, y):
        # ignore this operation
        pass
    
    def on_click(self, x, y, button, pressed):
        print(f'x:{x}, y:{y}, button:{button}, pressed:{pressed}, {type(button)}')
        op_type = 'press' if pressed else 'release'
        op_info = {'ts': time.time(), "type": op_type, "x": x, "y": y, 'button': str(button)}
        if pressed:
            self.record_operation(op_info, screen_shot=True)
        else:
            self.record_operation(op_info, screen_shot=False)
    
    def on_scroll(self, x, y, dx, dy):
        # ignore this operation
        pass
    
    def block_listen(self):
        with mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        ) as listener:
            listener.join()
            
    def nonblock_listen(self):
        listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        listener.start()
        
class KeyboardListener(object):
    
    def __init__(self, base_dir, task_uuid=None):
        if not task_uuid:
            task_uuid = datetime.now().strftime('%Y%m%d%H%M%S')
        self.base_dir = base_dir
        self.work_dir = os.path.join(self.base_dir, task_uuid)
        if not os.path.exists(self.work_dir):
            os.makedirs(self.work_dir)
        self.records = []

    def record_operation(self, op_info, screen_shot=False):
        """
        param:op_info示例 {"key": "a", "type": "press", "ts": "时间戳"} # 其中type值press/release
        """
        self.records.append(op_info)
        with open(os.path.join(self.work_dir, 'key_records.json'), 'w') as f:
            json.dump(self.records, f)
        if screen_shot:
            shot_name = f'ts{op_info["ts"]}_{op_info["type"]}_{op_info["key"]}.png'
            shot_path = os.path.join(self.work_dir, shot_name)
            op_info['screen_shot'] = shot_name
            screenshot = ImageGrab.grab()
            screenshot.save(shot_path)
            screenshot.close()

    def on_press(self, key):
        ts = time.time()
        try:
            key_char = str(key.char)
        except AttributeError:
            key_char = str(key) # 特殊按键
        self.record_operation({'ts': ts, "type": "press", "key": key_char}, screen_shot=False)
    
    def on_release(self, key):
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        ts = time.time()
        try:
            key_char = str(key.char)
        except AttributeError:
            key_char = str(key) # 特殊按键
        self.record_operation({'ts': ts, "type": "release", "key": key_char}, screen_shot=False)
    
    def block_listen(self):
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            listener.join()
    
    def nonblock_listen(self):
        listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        listener.start()
    
def record_ui_flow():
    p = Process(target=MouseListener('./flow_data').block_listen)
    p.daemon = True
    p.start()
    KeyboardListener('./flow_data').block_listen()

if __name__ == '__main__':
    record_ui_flow()
 