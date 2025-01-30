import time
import docker
import subprocess
import re
import os
import pandas as pd
import numpy as np
import threading

os.environ["DOCKER_HOST"] = "unix:///var/run/docker.sock"

client = docker.from_env()
# Function to convert time units to milliseconds
def convert_to_ms(value, unit):
    if unit == "us":
        return float(value) / 1000  # Convert microseconds to milliseconds
    elif unit == "ms":
        return float(value)  # Already in milliseconds
    elif unit == "s":
        return float(value) * 1000  # Convert seconds to milliseconds
    return None  # If unit is not recognized

# Function to convert requests per second values, handling "k" suffix
def convert_to_num(value):
    if 'k' in value:
        return float(value.replace('k', '')) * 1000  # Convert "k" to thousands
    return float(value)

def convert_to_mb(value, unit):
    if unit == "MB":
        return float(value)  # Already in megabytes
    elif unit == "KB":
        return float(value) / 1024  # Convert kilobytes to megabytes
    return None  # If unit is not recognized

# Function to capture CPU usage inside a Docker container concurrently
def capture_container_cpu_usage(container_name, duration, interval=1):
    container = client.containers.get(container_name)
    client.containers.get(container_name).restart()
    cpu_percentages = []
    memory_usages = []

    def monitor_cpu():
        nonlocal cpu_percentages, memory_usages
        start_time = time.time()
        while time.time() - start_time < duration:
            stats = container.stats(stream=False)
            cpu_usage = stats['cpu_stats']['cpu_usage']['total_usage']
            system_cpu_usage = stats['cpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_usage / system_cpu_usage) * 100 if system_cpu_usage > 0 else 0
            cpu_percentages.append(cpu_percent)

            # Capture memory usage
            mem_usage = stats['memory_stats']['usage']
            memory_usages.append(mem_usage / (1024 * 1024))  # Convert to MB
    # Run the monitor function in a separate thread
    thread = threading.Thread(target=monitor_cpu)
    thread.start()
    return thread, cpu_percentages, memory_usages

# Function to run wrk and capture the results
def run_wrk(url, framework_name, concurrency, endpoint_type, container_name):
    duration = 30  # Duration of the test in seconds
    threads = 10
    if concurrency < 10:
        threads = concurrency
    command = f"wrk -t{threads} -c{concurrency} -d{duration}s -s no-cache.lua -- {url}"
    print(f"Running command: {command}")

    cpu_monitor_thread, cpu_percentages, memory_usages = capture_container_cpu_usage(container_name, duration)

    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout
    print(output)

     # Wait for the CPU monitoring thread to complete
    cpu_monitor_thread.join()
    # Calculate average and max CPU usage
    avg_cpu_usage = sum(cpu_percentages) / len(cpu_percentages) if cpu_percentages else None
    max_cpu_usage = max(cpu_percentages) if cpu_percentages else None

    # Calculate average and max memory usage
    avg_mem_usage = sum(memory_usages) / len(memory_usages) if memory_usages else None
    max_mem_usage = max(memory_usages) if memory_usages else None


    # Extract values using refined regex patterns
    latency_stats = re.search(r"Latency\s+([0-9.]+)(us|ms|s)\s+([0-9.]+)(us|ms|s)\s+([0-9.]+)(us|ms|s)\s+([0-9.]+)%", output)
    req_sec_stats = re.search(r"Req/Sec\s+([0-9.]+k?)\s+([0-9.]+k?)\s+([0-9.]+k?)\s+([0-9.]+)%", output)
    
    overall_requests_sec = re.search(r"Requests/sec:\s+([0-9.]+)", output)
    transfer_sec = re.search(r"Transfer/sec:\s+([0-9.]+)(MB|KB)", output)

    # Convert latency values to milliseconds
    avg_latency = convert_to_ms(latency_stats.group(1), latency_stats.group(2)) if latency_stats else None
    stdev_latency = convert_to_ms(latency_stats.group(3), latency_stats.group(4)) if latency_stats else None
    max_latency = convert_to_ms(latency_stats.group(5), latency_stats.group(6)) if latency_stats else None
    stdev_latency_percent = float(latency_stats.group(7)) if latency_stats else None

    avg_req_sec = convert_to_num(req_sec_stats.group(1)) if req_sec_stats else None
    stdev_req_sec = convert_to_num(req_sec_stats.group(2)) if req_sec_stats else None
    max_req_sec = convert_to_num(req_sec_stats.group(3)) if req_sec_stats else None
    stdev_req_sec_percent = float(req_sec_stats.group(4)) if req_sec_stats else None
    
    # Handle transfer/sec units (KB to MB if necessary)
    transfer_sec = convert_to_mb(transfer_sec.group(1), transfer_sec.group(2)) if transfer_sec else None
    # Extract values using refined regex patterns
    return {
        "Framework": framework_name,
        "Endpoint_Type": endpoint_type,
        "Concurrency": concurrency,
        "Avg_Latency_ms": avg_latency,
        "Stdev_Latency_ms": stdev_latency,
        "Max_Latency_ms": max_latency,
        "+/-_Stdev_Latency_%": stdev_latency_percent,
        "Avg_Req_Sec": avg_req_sec,
        "Stdev_Req_Sec": stdev_req_sec,
        "Max_Req_Sec": max_req_sec,
        "+/-_Stdev_Req_Sec_%": stdev_req_sec_percent,
        "Overall_Requests_Sec": float(overall_requests_sec.group(1)) if overall_requests_sec else None,
        "Transfer_Sec_MB": transfer_sec,
        "Avg_CPU_Usage": avg_cpu_usage,
        "Max_CPU_Usage": max_cpu_usage,
        "Avg_Mem_Usage": avg_mem_usage,
        "Max_Mem_Usage": max_mem_usage
    }

# Define concurrency levels to test
# concurrency_levels = [10, 50, 100, 500, 1000]
# concurrency_levels = np.arange(1, 1000, 20  0, dtype=int)
concurrency_levels = [1, 10, 50, 100, 500, 1000]
# Storage for all results
results = []

# URLs for FastAPI and Flask endpoints
endpoints = [
    ("http://127.0.0.1:8000/", "FastAPI (ASGI)", "asgi_container"),
    ("http://127.0.0.1:8001/", "Flask (WSGI)", "wsgi_container")
]

endopoints_types= [("", "simple"),("io-bound", "IO Bound"), ("cpu-bound", "CPU Bound")]

# Run tests for each concurrency level and each framework
for url, framework, container_name in endpoints:
    for endpoint_url, endpoint_type in endopoints_types:
        for concurrency in concurrency_levels:
            print(f"Running wrk for {framework} with concurrency level {concurrency} and endpoint type {endpoint_type}...")
            result_data = run_wrk(url + endpoint_url, framework, concurrency, endpoint_type, container_name)
            output_dir = "output_data"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            csv_path = os.path.join(output_dir, f"benchmark_concurrency_results.csv")
# Save to CSV (append mode if file exists)

            df = pd.DataFrame([result_data])
# Check if file exists, if not, include headers
            if os.path.exists(csv_path):
                df.to_csv(csv_path, mode='a', index=False, header=False)  # Append to existing file
            else:
                df.to_csv(csv_path, mode='w', index=False, header=True)  # Create new file with headers

            print(f"Results saved to {csv_path}")




