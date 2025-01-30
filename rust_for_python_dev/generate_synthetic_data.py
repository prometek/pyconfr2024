import numpy as np
import pandas as pd
import random
import string

def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def generate_synthetic_data(rows, cols):
    """
    Generates a synthetic dataset with specified number of rows and columns.
    The dataset will contain numerical, categorical, and date columns.
    """
    np.random.seed(42)  # For reproducibility
    
    # Create random numerical data
    data = {f'num_col_{i}': np.random.randn(rows) for i in range(cols)}
    
    # Add a few categorical columns
    data['category_col'] = [random_string(8) for _ in range(rows)]
    
    # Add a date column
    data['date_col'] = pd.date_range(start='2020-01-01', periods=rows, freq='T')  # Minute intervals
    
    return pd.DataFrame(data)

# Sizes: small, medium, large, and very large datasets
dataset_sizes = {
    "small": (1000, 10),        # 1K rows, 10 columns
    "medium": (100000, 20),     # 100K rows, 20 columns
    "large": (10000000, 50),    # 10M rows, 50 columns
    "very_large": (100000000, 50)  # 100M rows, 100 columns
}

# Generate and save datasets to Parquet files
n_cols = 10
n_rows_start = 1000
n_rows_end = 100000000
nb_data = 50
n_rows = np.linspace(n_rows_start, n_rows_end, nb_data).astype(int)
# for size_name, (rows, cols) in dataset_sizes.items():
#     print(f"Generating {size_name} dataset with {rows} rows and {cols} columns...")
#     df = generate_synthetic_data(rows, cols)
#     file_name = f'data/{size_name}_dataset.parquet'
#     df.to_parquet(file_name, index=False, compression='snappy')  # Save as Parquet with snappy compression
#     print(f"{size_name.capitalize()} dataset saved to {file_name}")
#
print(n_rows)
for rows in n_rows:
    print(f"Generating dataset with {rows} rows and {n_cols} columns...")
    df = generate_synthetic_data(rows, n_cols)
    file_name = f'data/dataset_{rows}_{n_cols}.parquet'
    df.to_parquet(file_name, index=False, compression='snappy')  # Save as Parquet with snappy compression
    print(f"Dataset saved to {file_name}")
print("All datasets generated and saved successfully!")

