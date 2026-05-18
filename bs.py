import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Data Preparation
data = {
    "Block Size": ["4k", "8k", "16k", "32k", "64k"] * 4,
    "Operation": (["Seq Read"] * 5 + ["Seq Write"] * 5 + 
                  ["Rand Read"] * 5 + ["Rand Write"] * 5),
    "IOPS": [
        3995.58, 3929.34, 3577.86, 6074.24, 5451.00,
        6198.95, 5166.32, 5791.22, 5220.20, 4971.85,
        3292.29, 3444.07, 5225.92, 5940.64, 5196.08,
        5119.81, 3970.81, 5123.88, 5455.91, 4597.57
    ],
    "Bandwidth (MiB/s)": [
        15.60, 30.56, 55.91, 189.82, 340.69,
        24.21, 40.36, 90.49, 163.13, 308.79,
        12.86, 26.91, 81.65, 184.03, 324.76,
        20.00, 30.95, 80.06, 170.50, 287.36
    ],
    "Latency (usec)": [
        249.09, 255.57, 278.07, 163.22, 182.37,
        162.01, 191.90, 171.74, 191.00, 200.99,
        302.45, 289.29, 190.47, 168.21, 190.83,
        193.25, 249.74, 193.94, 180.86, 217.76
    ]
}

df = pd.DataFrame(data)

# 2. Visual Settings
sns.set_theme(style="whitegrid")
custom_palette = {
    "Seq Read": "#2ecc71",   # Green
    "Seq Write": "#e74c3c",  # Red
    "Rand Read": "#3498db",  # Blue
    "Rand Write": "#f1c40f"  # Yellow
}

# Changed to 1 row, 3 columns. Width=20, Height=6
fig, axes = plt.subplots(1, 3, figsize=(20, 6))
metrics = ["IOPS", "Bandwidth (MiB/s)", "Latency (usec)"]

# 3. Plotting
for i, metric in enumerate(metrics):
    sns.lineplot(
        data=df, 
        x="Block Size", 
        y=metric, 
        hue="Operation", 
        marker="o", 
        markersize=8,
        ax=axes[i],
        palette=custom_palette,
        linewidth=2.5,
        legend=(i == 2) # Only show legend on the last plot to save space
    )
    
    # Customizing each subplot
    axes[i].set_title(f"{metric} vs. Block Size", fontsize=14, fontweight='bold')
    axes[i].set_xlabel("Block Size", fontsize=11)
    axes[i].set_ylabel(metric, fontsize=11)

# Adjust legend for the last plot
axes[2].legend(title="Operation Type", bbox_to_anchor=(1.05, 1), loc='upper left')

# 4. Final Polish and Save
plt.tight_layout()
plt.savefig("IO_Performance_Horizontal.pdf", format='pdf', bbox_inches='tight')
print("Horizontal report saved: IO_Performance_Horizontal.pdf")
plt.show()