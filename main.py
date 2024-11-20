import os
import sys
import platform
import uvicorn
import random
import socket
import threading
import webview
import uvicorn
import multiprocessing
import signal

def get_dirs_by_system():
    if hasattr(sys, '_MEIPASS'):  # PyInstaller 解包目录
        base_dir = sys._MEIPASS
        work_dir = None
    else:
        base_dir = os.path.dirname(__file__)
        work_dir = base_dir
    frontend_static = os.path.join(base_dir, 'static')
        
    if work_dir is None:
        os_system = platform.system()
        sys_workdir_funcs = {
            'Darwin': lambda: os.path.expanduser('~/Library/Application Support/uiflow'),
            'Windows': lambda: '',
            'Linux': lambda: '',
        }
        if os_system not in sys_workdir_funcs:
            raise Exception(f'not support system({os_system})')
        work_dir = sys_workdir_funcs[os_system]()
        
    if not os.path.exists(work_dir):
        os.makedirs(work_dir, exist_ok=True)

    print('work_dir:', work_dir)
    return frontend_static, work_dir

frontend_static, work_dir = get_dirs_by_system()
os.environ.update({
    'UIFLOW_STATIC_DIR': frontend_static,
    'UIFLOW_WORK_DIR': work_dir,
})

from logging import getLogger

from server.server import app

logger = getLogger(__name__)

class LOG():
    def info(self, msg):
        logger.info(msg)

def get_unused_port():
    while True:
        port = random.randint(1024, 65535)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(('localhost', port))
            sock.close()
            return port
        except OSError:
            pass
        
def run_fastapi(port):
    uvicorn.run(app, port=port)

def run_webview(port, main_pid):
    try:
        webview.create_window('UIFlow', f'http://localhost:{port}/static/flow')
        webview.start(debug=True)
    except Exception as e:
        print(e)
    finally:
        os.kill(main_pid, signal.SIGUSR1)

        
def main():
    main_pid = os.getpid()
    port = get_unused_port()
    
    # webview退出后，主进程退出
    signal.signal(signal.SIGUSR1, lambda sig_num, event: sys.exit(0))
    
    # 使用线程会有异常，选择使用进程
    process = multiprocessing.Process(target=run_webview, 
                                      kwargs={'port': port, 'main_pid': main_pid},
                                      daemon=True)
    multiprocessing.freeze_support() # pyinstaller打包要求，没有该语句会异常
    process.start()
    
    run_fastapi(port) # 不能放到multiprocessing中，pyinstaller打包后，无法启动background_tasks

if __name__ == '__main__':
    #main()
    #uvicorn.run(app, port=8009, log_level='info')
