import time
import json
import os
import logging
from .probes import SystemProbe, GPUProbe

#__init__: Does the probes and double checks the pathing.
#_record_metrics: Grab current hardware stats and attach them to all active requests.

class ResourceMonitor:
    def __init__(self, event_file_path, output_file_path, sampling_interval=0.1):
        self.event_file = event_file_path
        self.output_file = output_file_path
        self.interval = sampling_interval
        
        self.active_requests = {} 
        self.running = False
        
        self.sys_probe = SystemProbe()
        self.gpu_probe = GPUProbe()
        
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        
        os.makedirs(os.path.dirname(self.event_file), exist_ok=True)
        
        logging.info(f"Monitor initialized. Watching: {self.event_file}")
        
        from .aggregator import calculate_stats
        self.calculate_stats = calculate_stats

    def _record_metrics(self):
        sys_stats = self.sys_probe.get_metrics()
        gpu_stats = self.gpu_probe.get_metrics()
        
        concurrency_count = len(self.active_requests)
        
        if concurrency_count == 0:
            return

        sample = {
            "timestamp": time.time(),
            "cpu_pct": sys_stats['cpu_pct'],
            "ram_gb": sys_stats['ram_gb'],
            "vram_gb": gpu_stats['vram_gb'],
            "gpu_util": gpu_stats['gpu_util_pct'],
            "concurrency": concurrency_count
        }

        for req_id in self.active_requests:
            self.active_requests[req_id].append(sample)

    def _handle_event(self, line):
        try:
            data = json.loads(line)
            event_type = data.get("event")
            req_id = data.get("request_id")

            if event_type == "start":
                logging.info(f"Detected START: {req_id}")
                self.active_requests[req_id] = []
                
            elif event_type == "stop":
                logging.info(f"Detected STOP: {req_id}")
                if req_id in self.active_requests:
                    raw_data = self.active_requests.pop(req_id)
                    self._process_completed_request(req_id, raw_data)
                    
        except json.JSONDecodeError:
            logging.error(f"Failed to parse log line: {line}")

    def _process_completed_request(self, req_id, samples):
        if samples:
            start_time = samples[0]['timestamp']
            end_time = samples[-1]['timestamp']
        else:
            start_time = time.time()
            end_time = time.time()

        final_record = self.calculate_stats(req_id, start_time, end_time, samples)
        
        try:
            with open(self.output_file, 'a') as f:
                f.write(json.dumps(final_record) + "\n")
            logging.info(f"Logged request {req_id}: {final_record['duration_sec']}s")
        except Exception as e:
            logging.error(f"Failed to write log for {req_id}: {e}")

    def start_optimized(self):
        self.running = True
        self._last_sample_time = time.time()
        logging.info("Monitor Service Started (Polling Mode)...")
        try:
            self._main_loop_step()
        except KeyboardInterrupt:
            self.stop()

    def _main_loop_step(self):
        while self.running and not os.path.exists(self.event_file):
            time.sleep(0.5)
            if not os.path.exists(self.event_file):
                 with open(self.event_file, 'w') as f: pass

        with open(self.event_file, 'r') as f:
            f.seek(0, 2) 
            
            while self.running:
                line = f.readline()
                if line:
                    self._handle_event(line)
                
                if time.time() - self._last_sample_time >= self.interval:
                    self._record_metrics()
                    self._last_sample_time = time.time()
                
                if not line:
                    time.sleep(0.01)

    def stop(self):
        self.running = False
        self.sys_probe.get_metrics() 
        self.gpu_probe.shutdown()
        logging.info("Monitor Stopped.")