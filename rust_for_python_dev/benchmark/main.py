import pandas as pd
import polars as pl

# Pandas Implementation
def pandas_benchmark(data, dataset_size):
    print("\n=== Pandas Numpy Benchmark ===")

    # Load data into Pandas DataFrame
    df, elapsed_time, peak_memory = measure_time("Pandas: Data Loading", pd.read_parquet, data)
    save_benchmark_results('Pandas(Numpy)', 'Data Loading', elapsed_time, peak_memory, dataset_size)
    # Filtering rows where num_col_1 > 0
    df_filtered, elapsed_time, peak_memory = measure_time("Pandas: Filtering", lambda df: df[df['num_col_1'] > 0], df)
    save_benchmark_results('Pandas (Numpy)', 'Filtering', elapsed_time, peak_memory, dataset_size)

    # Aggregation (group by category_col and sum num_col_1)
    df_agg, elapsed_time, peak_memory = measure_time("Pandas: Aggregation", lambda df_filtered: df_filtered.groupby('category_col')['num_col_1'].sum(), df_filtered)
    save_benchmark_results('Pandas (Numpy)', 'Aggregation', elapsed_time, peak_memory, dataset_size)
    # Sorting by num_col_1
    df_sorted, elapsed_time, peak_memory = measure_time("Pandas: Sorting", df.sort_values, by='num_col_1')
    save_benchmark_results('Pandas (Numpy)', 'Sorting', elapsed_time, peak_memory, dataset_size)
    # Joining (self join on category_col)
    df_joined, elapsed_time, peak_memory = measure_time("Pandas: Joining", pd.merge, df, df_filtered, on='category_col', how='inner')
    save_benchmark_results('Pandas (Numpy)', 'Joining', elapsed_time, peak_memory, dataset_size)

    # Writing to CSV
    _, elapsed_time, peak_memory =  measure_time("Pandas: Writing CSV", df.to_csv, 'pandas_output.csv', index=False, float_format='%.4f')
    save_benchmark_results('Pandas (Numpy)', 'Writing CSV', elapsed_time,  peak_memory, dataset_size)
    # Writing to Parquet
    _, elapsed_time, peak_memory = measure_time("Pandas: Writing Parquet", df.to_parquet, 'pandas_output.parquet', compression='snappy')
    save_benchmark_results('Pandas (Numpy)', 'Writing Parquet', elapsed_time,  peak_memory, dataset_size)

    return df_sorted

def pandas_with_pyarrow_benchmark(data, dataset_size):
    print("\n=== Pandas PyArrow Benchmark ===")

    # Load data into Pandas DataFrame
    df, elapsed_time, peak_memory = measure_time("Pandas: Data Loading", pd.read_parquet, data, engine='pyarrow')
    save_benchmark_results('Pandas (PyArrow)', 'Data Loading', elapsed_time,  peak_memory, dataset_size)
    df = df.convert_dtypes(dtype_backend="pyarrow")

    # Filtering rows where num_col_1 > 0
    df_filtered, elapsed_time, peak_memory = measure_time("Pandas: Filtering", lambda df: df[df['num_col_1'] > 0], df)
    save_benchmark_results('Pandas (PyArrow)', 'Filtering', elapsed_time,  peak_memory, dataset_size)

    # Aggregation (group by category_col and sum num_col_1)
    df_agg, elapsed_time, peak_memory = measure_time("Pandas: Aggregation", lambda df_filtered: df_filtered.groupby('category_col')['num_col_1'].sum(), df_filtered)
    save_benchmark_results('Pandas (PyArrow)', 'Aggregation', elapsed_time, peak_memory, dataset_size)
    # Sorting by num_col_1
    df_sorted, elapsed_time, peak_memory = measure_time("Pandas: Sorting", df.sort_values, by='num_col_1')
    save_benchmark_results('Pandas (PyArrow)', 'Sorting', elapsed_time, peak_memory, dataset_size)
    # Joining (self join on category_col)
    df_joined, elapsed_time, peak_memory = measure_time("Pandas: Joining", pd.merge, df, df_filtered, on='category_col', how='inner')
    save_benchmark_results('Pandas (PyArrow)', 'Joining', elapsed_time, peak_memory, dataset_size)

    # Writing to CSV
    _, elapsed_time, peak_memory =  measure_time("Pandas (PyArrow): Writing CSV", df.to_csv, 'pandas_output.csv', index=False, float_format='%.4f')
    save_benchmark_results('Pandas (PyArrow)', 'Writing CSV', elapsed_time,  peak_memory, dataset_size)
    # Writing to Parquet
    _, elapsed_time, peak_memory = measure_time("Pandas (PyArrow): Writing Parquet", df.to_parquet, 'pandas_output.parquet', compression='snappy', engine='pyarrow')
    save_benchmark_results('Pandas (PyArrow)', 'Writing Parquet', elapsed_time,  peak_memory, dataset_size)

    return df_sorted



# Polars Implementation
def polars_benchmark(data, dataset_size):
    print("\n=== Polars Benchmark ===")

    # Convert data to Polars DataFrame
    df, elapsed_time, peak_memory = measure_time("Polars: Data Loading", pl.read_parquet, data)
    save_benchmark_results('Polars', 'Data Loading', elapsed_time,  peak_memory, dataset_size)
    # Filtering rows where num_col_1 > 0
    df_filtered, elapsed_time, peak_memory = measure_time("Polars: Filtering", df.filter, pl.col('num_col_1') > 0)
    save_benchmark_results('Polars', 'Filtering', elapsed_time,  peak_memory, dataset_size)
    # Aggregation (group by category_col and sum num_col_1)
    df_agg, elapsed_time, peak_memory = measure_time("Polars: Aggregation", lambda df_filtered: df_filtered.group_by('category_col').agg(pl.col('num_col_1')).sum(), df_filtered)
    save_benchmark_results('Polars', 'Aggregation', elapsed_time,  peak_memory, dataset_size)
    # Sorting by num_col_1
    df_sorted, elapsed_time, peak_memory = measure_time("Polars: Sorting", df.sort, 'num_col_1')
    save_benchmark_results('Polars', 'Sorting', elapsed_time,  peak_memory, dataset_size)
    # Joining (self join on category_col)
    df_joined, elapsed_time, peak_memory = measure_time("Polars: Joining", df.join, df_filtered, on='category_col', how='inner')
    save_benchmark_results('Polars', 'Joining', elapsed_time,  peak_memory, dataset_size)
    # Writing to CSV
    _, elapsed_time, peak_memory = measure_time("Polars: Writing CSV", df_sorted.write_csv, 'polars_output.csv', float_precision=4)
    save_benchmark_results('Polars', 'Writing CSV', elapsed_time,  peak_memory, dataset_size)

    # Writing to Parquet
    _, elapsed_time, peak_memory = measure_time("Polars: Writing Parquet", df_sorted.write_parquet, 'polars_output.parquet', compression='snappy')
    save_benchmark_results('Polars', 'Writing Parquet', elapsed_time,  peak_memory, dataset_size)

    return df_sorted

