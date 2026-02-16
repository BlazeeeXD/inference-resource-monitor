import subprocess
import time
import os
import sys

def main():
    ipc_file = os.path.join("data", "ipc", "events.log")
    log_file = os.path.join("data", "logs", "resource_usage.jsonl")

    print("--- Cleaning up old data ---")
    if os.path.exists(ipc_file):
        os.remove(ipc_file)
    if os.path.exists(log_file):
        os.remove(log_file)
    
    os.makedirs(os.path.dirname(ipc_file), exist_ok=True)

    print("--- Starting Resource Monitor ---")
    
    monitor_code = (
        f"from src.monitor import ResourceMonitor; "
        f"ResourceMonitor(r'{ipc_file}', r'{log_file}').start_optimized()"
    )
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()

    monitor_process = subprocess.Popen(
        [sys.executable, "-c", monitor_code],
        env=env
    )

    time.sleep(2)

    try:
        print("--- Starting Inference Workload ---")
        subprocess.run([sys.executable, "tests\dummy_inference.py"], check=True)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    except subprocess.CalledProcessError:
        print("Inference simulation failed!")
    finally:
        print(f"--- Workload finished. Stopping Monitor (PID {monitor_process.pid}) ---")
        monitor_process.terminate()
        monitor_process.wait()

    print("\n--- DEMO COMPLETE ---")
    print(f"Results stored in {log_file}:")
    print("-" * 30)

    
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            print(f.read())
            print(" -Blaze")
    else:
        print("No logs found. Something went wrong.")

if __name__ == "__main__":
    main()