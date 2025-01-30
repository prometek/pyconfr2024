import docker
import json
import csv
from datetime import datetime
import re
import os

client = docker.from_env()

def execute_benchmark(container, command):
    try:
        exec_log = container.exec_run(command, stdout=True, stderr=True)
        output = exec_log.output.decode('utf-8')
        print(output)

        # Check if there's an error (stderr will be captured here)
        if exec_log.exit_code != 0:
            print(f"Error running benchmark in container '{container_name}':")
            print(output)  # Print the error log
            return None

        return json.loads(output)
    except (docker.errors.APIError, json.JSONDecodeError) as e:
        print(f"Error executing benchmark: {e}")
    return None

def save_benchmark_results(library, results, dataset_size, filename='benchmark_results.csv'):
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Library', 'Operation', 'Elapsed Time (seconds)', 'Memory Usage (MB)', 'Dataset Size', 'Timestamp'])
        for operation, data in results.items():
            writer.writerow([
                library,
                operation,
                data['time'],
                data['memory'],
                dataset_size,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])

def run_benchmark(library, container_name, file):
    print(f"\n=== Running {library} Benchmark on {file} ===")
    container = client.containers.get(container_name)
    container.restart()
   
    file_path = os.path.join('data', file)
    dataset_size_bytes = os.path.getsize(file_path)
    dataset_size_mb = dataset_size_bytes / (1000 ** 2)


    command = f"python /app/main.py --file /app/data/{file}"
    results = execute_benchmark(container, command)
    if results:
        save_benchmark_results(library, results, dataset_size_mb)
    else:
        print(f"Failed to get results for {library}")

if __name__ == "__main__":
    import os
    files = [f for f in os.listdir('data') if f.endswith('.parquet')]

    def extract_size(filename):
        match = re.search(r'dataset_(\d+)_10\.parquet', filename)
        if match:
            return int(match.group(1))
        return None

# Extract sizes and sort files by size
    files_with_size = [(file, extract_size(file)) for file in files if extract_size(file) is not None]
    sorted_files = sorted(files_with_size, key=lambda x: x[1])

# Get only the filenames from the sorted list
    sorted_filenames = [file for file, size in sorted_files]
    
    container_name = "pandas_container"  # Assuming a single container for both libraries
    
    for file in sorted_filenames:
        # run_benchmark("Pandas", container_name, file)
        run_benchmark("Pandas", container_name, file)
