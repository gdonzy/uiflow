from enum import Enum

class FlowStatus(Enum):
    ready = 0
    collecting = 1
    success = 2
    failed = 3

class ExecLogStatus(Enum):
    ready = 0
    running = 1
    success = 2
    failed = 3
    
class ExecNodeStatus(Enum):
    ready = 0
    running = 1
    success = 2
    failed = 3