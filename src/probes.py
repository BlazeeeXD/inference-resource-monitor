import psutil
import pynvml
import logging

#logging.basicConfig: Shows us what's happening
#SystemProbe: Monitors CPU and System RAM using psutil.
#get_metrics: Returns a dictionary with current CPU pct and RAM usage in GB.
#GPUProbe: Monitors NVIDIA GPU using pynvml.
#get_metrics: Returns dictionary with VRAM used in GB and GPU Utilization in %. 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SystemProbe:
    def __init__(self):
        psutil.cpu_percent(interval=None)

    def get_metrics(self):
        cpu_usage = psutil.cpu_percent(interval=None)
        mem_info = psutil.virtual_memory()
        ram_gb = round(mem_info.used / (1024 ** 3), 2)
        
        return {
            "cpu_pct": cpu_usage,
            "ram_gb": ram_gb
        }

class GPUProbe:
    def __init__(self, gpu_index=0):
        self.gpu_index = gpu_index
        self.handle = None
        self.is_available = False

        try:
            pynvml.nvmlInit()
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(self.gpu_index)
            self.gpu_name = pynvml.nvmlDeviceGetName(self.handle)
            self.is_available = True
            logging.info(f"GPU Probe initialized. Monitoring: {self.gpu_name}")
        except pynvml.NVMLError as e:
            logging.warning(f"Failed to initialize NVML: {e}. GPU metrics will be 0.")
            self.is_available = False

    def get_metrics(self):
        if not self.is_available:
            return {"vram_gb": 0.0, "gpu_util_pct": 0}

        try:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            vram_gb = round(mem_info.used / (1024 ** 3), 2)

            util_info = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            gpu_util = util_info.gpu

            return {
                "vram_gb": vram_gb,
                "gpu_util_pct": gpu_util
            }
        except pynvml.NVMLError:
            return {"vram_gb": 0.0, "gpu_util_pct": 0}

    def shutdown(self):
        if self.is_available:
            try:
                pynvml.nvmlShutdown()
            except pynvml.NVMLError:
                pass