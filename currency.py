import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Data Construction
# We combine Jobs and Queue Depth into a single "Concurrency" label for the X-axis
def create_df():
    data = []
    # Structure: (OpType, Jobs, QD, IOPS, Bandwidth, Latency)
    raw_data = [
        # Sequential Read
        ('Seq Read', 1, 1, 5533.93, 21.42, 181.35), ('Seq Read', 1, 16, 5691.46, 22.23, 175.06), ('Seq Read', 1, 64, 1618.29, 6.32, 624.29),
        ('Seq Read', 4, 1, 8635.49, 33.54, 465.26), ('Seq Read', 4, 16, 13588.68, 52.70, 295.01), ('Seq Read', 4, 64, 12899.66, 50.40, 308.38),
        ('Seq Read', 8, 1, 11383.22, 44.27, 704.58), ('Seq Read', 8, 16, 9799.37, 38.28, 813.19), ('Seq Read', 8, 64, 12718.31, 49.48, 629.75),
        # Sequential Write
        ('Seq Write', 1, 1, 6193.85, 24.19, 161.90), ('Seq Write', 1, 16, 6368.80, 24.88, 156.03), ('Seq Write', 1, 64, 4546.83, 17.76, 218.57),
        ('Seq Write', 4, 1, 9277.81, 36.24, 428.00), ('Seq Write', 4, 16, 11440.68, 44.69, 346.99), ('Seq Write', 4, 64, 14044.42, 54.86, 285.57),
        ('Seq Write', 8, 1, 11265.46, 44.01, 711.31), ('Seq Write', 8, 16, 10556.56, 41.23, 758.46), ('Seq Write', 8, 64, 12187.15, 47.61, 651.73),
        # Random Read
        ('Rand Read', 1, 1, 6228.98, 24.33, 159.80), ('Rand Read', 1, 16, 5542.61, 21.65, 179.17), ('Rand Read', 1, 64, 2964.92, 11.58, 336.42),
        ('Rand Read', 4, 1, 11939.95, 46.64, 333.14), ('Rand Read', 4, 16, 13308.68, 51.99, 310.19), ('Rand Read', 4, 64, 11338.75, 44.29, 352.97),
        ('Rand Read', 8, 1, 10191.12, 39.81, 779.59), ('Rand Read', 8, 16, 10293.97, 40.21, 777.91), ('Rand Read', 8, 64, 11716.71, 45.77, 673.68),
        # Random Write
        ('Rand Write', 1, 1, 4944.83, 19.31, 201.16), ('Rand Write', 1, 16, 4355.36, 17.01, 378.57), ('Rand Write', 1, 64, 4453.80, 17.40, 224.85),
        ('Rand Write', 4, 1, 11476.93, 44.83, 344.30), ('Rand Write', 4, 16, 12022.85, 46.96, 331.59), ('Rand Write', 4, 64, 13874.75, 54.00, 289.29),
        ('Rand Write', 8, 1, 10305.75, 40.26, 771.27), ('Rand Write', 8, 16, 10441.42, 40.79, 764.59), ('Rand Write', 8, 64, 9325.83, 36.43, 967.18),
    ]
    columns = ['Operation', 'Jobs', 'QueueDepth', 'IOPS', 'Bandwidth (MiB/s)', 'Latency (usec)']
    df = pd.DataFrame(raw_data, columns=columns)
    # Create a combined label for X-axis
    df['Configuration'] = 'J' + df['Jobs'].astype(str) + '-Q' + df['QueueDepth'].astype(str)
    return df

df = create_df()

# 2. Plotting Settings
sns.set_theme(style="whitegrid", font_scale=1.1)
metrics = ['IOPS', 'Bandwidth (MiB/s)', 'Latency (usec)']
ops = df['Operation'].unique()

fig, axes = plt.subplots(len(metrics), len(ops), figsize=(18, 12), sharex=True)
plt.subplots_adjust(hspace=0.3, wspace=0.3)

# 3. Generating the Matrix of Plots
# Muted academic palette for Queue Depth groups
palette = sns.color_palette(["#1b9e77", "#d95f02", "#7570b3"])

for row_idx, metric in enumerate(metrics):
    for col_idx, op in enumerate(ops):
        ax = axes[row_idx, col_idx]
        subset = df[df['Operation'] == op]
        
        sns.barplot(
            data=subset, 
            x='Jobs', 
            y=metric, 
            hue='QueueDepth', 
            ax=ax, 
            palette=palette,
            edgecolor=".2"
        )
        
        # Set titles and labels only where necessary for cleanliness
        if row_idx == 0:
            ax.set_title(f"{op}", fontweight='bold', fontsize=14)
        if col_idx == 0:
            ax.set_ylabel(metric, fontweight='bold')
        else:
            ax.set_ylabel("")
            
        ax.set_xlabel("")
        ax.legend().remove() # Remove individual legends

# Add a shared legend and a main title
handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, title='Queue Depth', loc='upper right', bbox_to_anchor=(0.98, 0.95))
fig.suptitle('Storage Performance Analysis: Impact of Concurrency (Jobs & Queue Depth)', 
             fontsize=46, fontweight='bold', y=0.98)

# Set common X-label
for ax in axes[-1, :]:
    ax.set_xlabel("Number of Jobs", fontweight='bold')

# 4. Final Polish and Save
plt.tight_layout(rect=[0, 0.03, 0.92, 0.95])
plt.savefig("Concurrency_Performance_Matrix.pdf", dpi=300)
print("Visualization saved as Concurrency_Performance_Matrix.pdf")
plt.show()
