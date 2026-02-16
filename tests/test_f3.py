import time
import json
import threading
from monitor import ResourceMonitor

IPC_FILE = "data/ipc/events.log"
OUT_FILE = "data/logs/resource_usage.jsonl"

def batch_simulator():
    time.sleep(1)

    print("[ Simon ] Starting Request A")
    with open(IPC_FILE, "a") as f:
        f.write(json.dumps({"event": "start", "request_id": "req_A", "timestamp": time.time()}) + "\n")
    
    time.sleep(2)

    print("[ Simon ] Starting Request B (Overlap)")
    with open(IPC_FILE, "a") as f:
        f.write(json.dumps({"event": "start", "request_id": "req_B", "timestamp": time.time()}) + "\n")
        
    time.sleep(2)

    print("[ Simon ] Stopping Request A")
    with open(IPC_FILE, "a") as f:
        f.write(json.dumps({"event": "stop", "request_id": "req_A", "timestamp": time.time()}) + "\n")
        
    time.sleep(1)

    print("[ Simon ] Stopping Request B")
    with open(IPC_FILE, "a") as f:
        f.write(json.dumps({"event": "stop", "request_id": "req_B", "timestamp": time.time()}) + "\n")

def test_full_stack():
    with open(IPC_FILE, "w") as f: pass
    with open(OUT_FILE, "w") as f: pass

    monitor = ResourceMonitor(IPC_FILE, OUT_FILE, sampling_interval=0.2)
    t = threading.Thread(target=monitor.start_optimized)
    t.start()

    batch_simulator()

    time.sleep(1)
    monitor.running = False
    t.join()
    
    print("\n--- Final Log Contents ---")
    with open(OUT_FILE, 'r') as f:
        for line in f:
            print(line.strip())

if __name__ == "__main__":
    test_full_stack()
