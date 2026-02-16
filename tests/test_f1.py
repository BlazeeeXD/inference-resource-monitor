import time
from src.probes import SystemProbe, GPUProbe

def test_hardware():
    print("--- Initializing Probes ---")
    sys_probe = SystemProbe()
    gpu_probe = GPUProbe()

    print("\n--- Starting 3-second Hardware Test ---")
    for i in range(3):
        sys_stats = sys_probe.get_metrics()
        gpu_stats = gpu_probe.get_metrics()
        
        print(f"Tick {i+1}:")
        print(f"  CPU: {sys_stats['cpu_pct']}% | RAM: {sys_stats['ram_gb']} GB")
        print(f"  GPU: {gpu_stats['gpu_util_pct']}% | VRAM: {gpu_stats['vram_gb']} GB")
        
        time.sleep(1)

    print("\n--- Shutting Down ---")
    gpu_probe.shutdown()
    print("Success.")

if __name__ == "__main__":
    test_hardware()