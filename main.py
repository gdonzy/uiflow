import uvicorn
import random
import socket
import threading
import webview
import uvicorn

from server.server import app

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
        
def main():
    port = get_unused_port()
    t = threading.Thread(target=uvicorn.run, args=(app,), kwargs={'port': port})
    t.daemon = True
    t.start()
    
    webview.create_window('UIFlow', f'http://localhost:{port}')
    webview.start(debug=True)

if __name__ == '__main__':
    #main()
    uvicorn.run(app, port=8009, log_level='info')
