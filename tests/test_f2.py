import time
import json
import threading
from src.monitor import ResourceMonitor

#writer_bot: Simulates the Inference App writing logs. 

IPC_FILE = "data/ipc/events.log"
OUT_FILE = "data/logs/resource_usage.jsonl"

def writer_bot():
    time.sleep(1)
    print("\n[Bot] Sending START req_A...")
    with open(IPC_FILE, "a") as f:
        f.write(json.dumps({"event": "start", "request_id": "req_A", "timestamp": time.time()}) + "\n")
    
    time.sleep(2)
    
    print("[Bot] Sending STOP req_A...")
    with open(IPC_FILE, "a") as f:
        f.write(json.dumps({"event": "stop", "request_id": "req_A", "timestamp": time.time()}) + "\n")

def test_watcher():
    with open(IPC_FILE, "w") as f: pass

    monitor = ResourceMonitor(IPC_FILE, OUT_FILE, sampling_interval=0.5)
    
    monitor_thread = threading.Thread(target=monitor.start_optimized)
    monitor_thread.start()
    
    writer_bot()

    time.sleep(1)
    monitor.running = False
    monitor_thread.join()
    print("\n[Test] Finished. Check console output for 'Request req_A finished'.")

if __name__ == "__main__":
    test_watcher()