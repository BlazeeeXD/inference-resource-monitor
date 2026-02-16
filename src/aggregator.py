import statistics

#calculate_stats: Consumes a list of raw hardware samples and returns a summarized dictionary.
#stats: Calculate Aggregates. We round to 2 decimal places for cleanlinesss

def calculate_stats(request_id, start_time, end_time, samples):

    duration = end_time - start_time
    
    if not samples:
        return {
            "request_id": request_id,
            "duration_sec": round(duration, 3),
            "error": "No samples collected (request too fast)"
        }

    adj_cpu = []
    adj_ram = []
    adj_vram = []
    adj_gpu_util = []

    for s in samples:
        count = max(1, s['concurrency'])
        
        adj_cpu.append(s['cpu_pct'] / count)
        adj_ram.append(s['ram_gb'] / count)
        adj_vram.append(s['vram_gb'] / count)
        adj_gpu_util.append(s['gpu_util'] / count)

    stats = {
        "request_id": request_id,
        "duration_sec": round(duration, 3),
        "sample_count": len(samples),
        
        "cpu_avg_pct": round(statistics.mean(adj_cpu), 2),
        "cpu_max_pct": round(max(adj_cpu), 2),
        
        "ram_avg_gb": round(statistics.mean(adj_ram), 2),
        "ram_max_gb": round(max(adj_ram), 2),
        
        "vram_avg_gb": round(statistics.mean(adj_vram), 2),
        "vram_max_gb": round(max(adj_vram), 2),
        
        "gpu_util_avg_pct": round(statistics.mean(adj_gpu_util), 2),
    }
    
    return stats