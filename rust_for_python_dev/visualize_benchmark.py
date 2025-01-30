import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load benchmark results from the CSV file
df_results = pd.read_csv('benchmark_results.csv', sep=';')

# Set plot style and colors (using a cohesive Catppuccin palette)
from catppuccin import PALETTE
sns.set(style="whitegrid")

# Extract the frappe palette colors and pick two for different libraries
frappe_palette = PALETTE.frappe.colors
first_library_color = frappe_palette.green.hex  # Choose a color for Library A (e.g., Pandas)
second_library_color = frappe_palette.red.hex  # Choose a color for Library B (e.g., Polars)


background_color = frappe_palette.base.hex
font_color = frappe_palette.text.hex
fastapi_color = frappe_palette.green.hex
flask_color = frappe_palette.peach.hex
background_color_1 = frappe_palette.surface1.hex

# Set the two colors globally in Seaborn for FastAPI and Flask

# Update matplotlib settings for global plot style
plt.rcParams.update({
    'figure.facecolor': background_color,      # Background color of the figure
    'axes.facecolor': background_color_1,        # Background color of the axes
    'axes.labelcolor': font_color,             # Color of the axis labels
    'text.color': font_color,                  # Color of text
    'xtick.color': font_color,                 # Color of x-axis ticks
    'ytick.color': font_color,                 # Color of y-axis ticks
    'legend.facecolor': background_color,      # Background color of legend
    'legend.edgecolor': font_color,            # Color of legend edge
    'axes.titlecolor': font_color,
    'axes.edgecolor': background_color_1# Title color
})


# Set the two colors globally in Seaborn
sns.set_palette([first_library_color, second_library_color])

# Group by Operation, Dataset Size, and Library to calculate mean elapsed time
df_means = df_results.groupby(['Operation', 'Dataset Size', 'Library'], as_index=False)['Elapsed Time (seconds)'].mean()
df_means['Dataset Size'] = df_means['Dataset Size'].apply(lambda x: float(f"""{(x / 1000):.2f}"""))
# Get unique operations and dataset sizes
operations = df_means['Operation'].unique()
datasets = df_means['Dataset Size'].unique()

# Create a plot for each operation (line plots for dataset sizes)
for operation in operations:
    # Filter the data for this operation
    operation_data = df_means[df_means['Operation'] == operation]
    
    plt.figure(figsize=(10, 6))
    
    # Create a line plot with Dataset Size on x and Mean Elapsed Time on y
    sns.lineplot(data=operation_data, x='Dataset Size', y='Elapsed Time (seconds)', hue='Library', marker='o')
    
    # Set plot labels and title
    plt.title(f'Mean Elapsed Time for {operation}')
    plt.ylabel('Mean Elapsed Time (seconds)')
    plt.xlabel('Dataset Size (GB)')
    # plt.xticks(rotation=45)
    
    # Save the plot
    plt.tight_layout()
    plt.savefig(f'output/{operation}_benchmark.png')
    plt.close()

# Create bar plots for each operation and dataset size
for operation in operations:
    operation_data = df_means[df_means['Operation'] == operation]
    
    for dataset in datasets:
        dataset_data = operation_data[operation_data['Dataset Size'] == dataset]
        
        # Check if there's data for this combination
        if not dataset_data.empty:
            plt.figure(figsize=(10, 6))
            sns.barplot(data=dataset_data, x='Library', y='Elapsed Time (seconds)', hue='Library')
            plt.title(f'Mean Elapsed Time for {operation} (Dataset Size: {dataset} GB)')
            plt.ylabel('Mean Elapsed Time (seconds)')
            plt.xlabel('Library')
            # plt.xticks(rotation=45)
            
            # Save the plot
            plt.tight_layout()
            plt.savefig(f'output/{operation}_{dataset}_benchmark.png')
            plt.close()

