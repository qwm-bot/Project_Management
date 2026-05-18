# 这里是B3的第一处修改
import matplotlib.pyplot as plt
import numpy as np

# ----------------------
# 你的精确数据
# ----------------------
labels = ['seq_read', 'seq_write', 'rand_read', 'rand_write']
iops =     [2305.41, 2760.59, 3441.59, 3153.71]
bw =       [8.99, 10.78, 13.44, 12.32]
latency =  [409.53, 342.32, 272.21, 298.51]

# ----------------------
# 统一风格（更清爽、对比更好、学术风）
# ----------------------
colors = ['#3B6FB6', '#E28F5B', '#4BAA6D', '#C0576E']
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 12.5,
    'axes.facecolor': '#F7F8FA',
    'figure.facecolor': 'white',
    'axes.edgecolor': '#D0D0D0',
    'axes.linewidth': 0.8,
    'axes.grid': True,
    'grid.color': '#DADDE2',
    'grid.linestyle': '--',
    'grid.alpha': 0.6,
    'axes.titleweight': 'semibold',
})


def draw_bar(labels, values, title, ylabel, filename):
    fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=120)
    bars = ax.bar(
        labels,
        values,
        color=colors,
        edgecolor='white',
        linewidth=1.2,
        zorder=3,
    )
    ax.set_title(title, pad=10)
    ax.set_ylabel(ylabel)
    ax.grid(axis='y')
    ax.grid(axis='x', visible=False)

    # 去掉上/右边框，让画面更干净
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 留出顶部空间，显示数值标签
    max_val = max(values)
    ax.set_ylim(0, max_val * 1.18)

    for b, v in zip(bars, values):
        ax.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + max_val * 0.03,
            f'{v:.2f}',
            ha='center',
            va='bottom',
            fontsize=10.5,
            color='#3C3C3C'
        )

    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    return fig, ax
# 你标记了一处修改
# ----------------------------------------------------
# 图 1：IOPS
# ----------------------------------------------------
draw_bar(
    labels,
    iops,
    'IOPS across I/O Patterns',
    'IOPS',
    'iops_comparison.pdf'
)

# ----------------------------------------------------
# 图 2：Bandwidth
# ----------------------------------------------------
draw_bar(
    labels,
    bw,
    'Bandwidth across I/O Patterns',
    'Bandwidth (MiB/s)',
    'bandwidth_comparison.pdf'
)

# ----------------------------------------------------
# 图 3：Latency
# ----------------------------------------------------
draw_bar(
    labels,
    latency,
    'Average Latency across I/O Patterns',
    'Latency (usec)',
    'latency_comparison.pdf'
)

plt.show()
