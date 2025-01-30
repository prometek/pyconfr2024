import polars as pl
import time
import argparse
import psutil
import os
import json

def get_process_memory(pid):
    try:
        process = psutil.Process(pid)
        return process.memory_info().rss / (1024 * 1024)  # Convert to MB
    except psutil.NoSuchProcess:
        return 0

def get_total_memory_usage():
    current_process = psutil.Process(os.getpid())
    children = current_process.children(recursive=True)
    total_memory = sum(get_process_memory(child.pid) for child in children)
    total_memory += get_process_memory(os.getpid())
    return total_memory

def measure_operation(func, *args, **kwargs):
    start_time = time.time()
    start_memory = get_total_memory_usage()
    
    result = func(*args, **kwargs)
    
    end_time = time.time()
    end_memory = get_total_memory_usage()
    
    elapsed_time = end_time - start_time
    memory_used = end_memory - start_memory
    
    return result, elapsed_time, memory_used

# Polars Implementation
def polars_benchmark(data):

    results = {}
    
    # Read file argument from command line
    args = argparse.ArgumentParser()
    args.add_argument('--file', type=str, required=True)
    args = args.parse_args()
    data = args.file



    # Convert data to Polars DataFrame
    df, loading_time, loading_memory = measure_operation(pl.read_parquet, data)
    results["Data Loading"] = {"time": loading_time, "memory": loading_memory}
    # Filtering rows where num_col_1 > 0
    df_filtered, filtering_time, filtering_memory = measure_operation(df.filter, pl.col('num_col_1') > 0)
    results["Filtering"] = {"time": filtering_time, "memory": filtering_memory}
    # Aggregation (group by category_col and sum num_col_1)
    _, agg_time, agg_memory = measure_operation(lambda df_filtered: df_filtered.group_by('category_col').agg(pl.col('num_col_1')).sum(), df_filtered)
    results["Aggregation"] = {"time": agg_time, "memory": agg_memory}
    # Sorting by num_col_1
    _, sort_time, sort_memory = measure_operation(df.sort, 'num_col_1')
    results["Sorting"] = {"time": sort_time, "memory": sort_memory}
    # Joining (self join on category_col)
    _, join_time, join_memory = measure_operation(df.join, df_filtered, on='category_col', how='inner')
    results["Joining"] = {"time": join_time, "memory": join_memory}
    # Writing to CSV
    _, csv_time, csv_memory =  measure_operation(df.write_csv, 'polars_output.csv', float_precision=4)
    results["Writing CSV"] = {"time": csv_time, "memory": csv_memory}

    # Writing to Parquet
    _, parquet_time, parquet_memory = measure_operation(df.write_parquet, 'polars_output.parquet', compression='snappy')
    results["Writing Parquet"] = {"time": parquet_time, "memory": parquet_memory}

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, required=True)
    args = parser.parse_args()
    
    results = polars_benchmark(args.file)
    print(json.dumps(results))
   
