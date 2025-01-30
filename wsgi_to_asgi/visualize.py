import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from catppuccin import PALETTE

# Load the benchmark data from CSV
csv_path = "output_data/benchmark_concurrency_results.csv"
df = pd.read_csv(csv_path)


concurrency_levels = df['Concurrency'].unique()

# Set the palette for the plots
frappe_palette = PALETTE.frappe.colors

background_color = frappe_palette.base.hex
font_color = frappe_palette.text.hex
fastapi_color = frappe_palette.green.hex
flask_color = frappe_palette.peach.hex
background_color_1 = frappe_palette.surface1.hex

# Set the two colors globally in Seaborn for FastAPI and Flask
sns.set_palette([fastapi_color, flask_color])

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

metrics = [
        ('Overall_Requests_Sec', 'Requests per Second (RPS)', 'Requests per Second'),
        ('Avg_Latency_ms', 'Average Latency', 'Latency (ms)'),
        ('Max_Latency_ms', 'Max Latency', 'Latency (ms)'),
        ('Transfer_Sec_MB', 'Transfer Speed (MB/s)', 'Transfer Speed (MB/s)'),
        ('Avg_CPU_Usage', 'Average CPU Usage (%)', 'Average CPU Usage (%)'),
        ('Avg_Mem_Usage', 'Average Memory Usage (MB)', 'Average Memory Usage (MB)'),
        ('Max_CPU_Usage', 'Max CPU Usage (%)', 'Max CPU Usage (%)'),
        ('Max_Mem_Usage', 'Max Memory Usage (MB)', 'Max Memory Usage (MB)')
    ]
# Plotting bar plots by concurrency levels
for concurrency in concurrency_levels:
    filtered_df = df[df['Concurrency'] == concurrency]
    
    # Define the metrics to plot
    for metric, title, ylabel in metrics:
        plt.figure(figsize=(10, 6))
        sns.barplot(data=filtered_df, x='Endpoint_Type', y=metric, hue='Framework')
        plt.title(title)
        plt.ylabel(ylabel)
        plt.grid(True, axis='y', color=font_color)  # Grid lines to match font color
        plt.savefig(f'output_data/plot/c_{concurrency}_{metric.lower()}.png')
        plt.close()

# Unique endpoint types
endpoint_types = df['Endpoint_Type'].unique()

# Plotting line plots by endpoint types
for endpoint_type in endpoint_types:
    df_sub = df[df['Endpoint_Type'] == endpoint_type]
    
    for metric, title, ylabel in metrics:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_sub, x='Concurrency', y=metric, hue='Framework')
        plt.title(title)
        plt.ylabel(ylabel)
        plt.grid(True, axis='y', color=font_color)  # Grid lines to match font color
        plt.savefig(f'output_data/plot/{metric.lower()}_{endpoint_type}.png')
        plt.close()
