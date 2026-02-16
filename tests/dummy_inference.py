import time
import json
import os
import random
import uuid

IPC_FILE = "data/ipc/events.log"
TOTAL_REQUESTS = 5

def log_event(event_type, req_id):
    payload = {
        "event": event_type,
        "request_id": req_id,
        "timestamp": time.time()
    }
    with open(IPC_FILE, "a") as f:
        f.write(json.dumps(payload) + "\n")

def simulate_inference_work(req_id, duration, intensity_mb):

    print(f"[{req_id}] Started. Allocating {intensity_mb}MB...")
    log_event("start", req_id)
    
    dummy_data = b'0' * (intensity_mb * 1024 * 1024)
    
    end_time = time.time() + duration
    while time.time() < end_time:
        _ = 21321 * 321321 
        time.sleep(0.01)   
        
    log_event("stop", req_id)
    print(f"[{req_id}] Finished.")
    
    del dummy_data

def main():
    os.makedirs(os.path.dirname(IPC_FILE), exist_ok=True)
    
    print("--- Dummy Inference Server Starting ---")
    print(f"Writing events to: {IPC_FILE}")
    
    try:
        for i in range(TOTAL_REQUESTS):
            req_id = f"req_{uuid.uuid4().hex[:6]}"
            
            duration = random.uniform(1.0, 3.0)
            intensity = random.randint(100, 500) 
            
            simulate_inference_work(req_id, duration, intensity)
            
            time.sleep(random.uniform(0.5, 1.5))
            
    except KeyboardInterrupt:
        print("\nStopping server.")

if __name__ == "__main__":
    main()