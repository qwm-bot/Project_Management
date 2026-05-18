import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 构造数据集 (根据您提供的表格数据)
data = {
    'Engine': ['pvsync', 'libaio', 'io_uring', 'mmap'] * 4,
    'Workload': (['Seq Read'] * 4 + ['Seq Write'] * 4 + 
                 ['Rand Read'] * 4 + ['Rand Write'] * 4),
    'IOPS': [
        # Seq Read: mmap 表现极其突出
        5656.02, 5759.39, 4892.22, 29350.71,
        # Seq Write
        5660.88, 5485.47, 6196.61, 4602.58,
        # Rand Read
        4505.81, 5640.64, 5441.41, 4488.14,
        # Rand Write
        5874.53, 5585.12, 3673.07, 2438.27
    ],
    'Bandwidth (MiB/s)': [
        # Seq Read
        22.00, 22.40, 19.20, 119.00,
        # Seq Write
        22.20, 21.40, 24.30, 18.10,
        # Rand Read
        17.60, 22.00, 21.00, 17.50,
        # Rand Write
        22.80, 21.80, 14.50, 9.57
    ],
    'Latency (usec)': [
        # Seq Read
        176.26, 172.93, 201.77, 32.65,
        # Seq Write
        174.97, 181.36, 159.73, 213.63,
        # Rand Read
        219.80, 175.65, 183.93, 220.69,
        # Rand Write
        170.06, 177.41, 267.18, 405.10
    ]
}

df = pd.DataFrame(data)

# 2. 设置绘图风格 (学术风格)
sns.set_theme(style="whitegrid", font_scale=1.2)
plt.rcParams['font.family'] = 'serif'  # 使用衬线字体更符合学术规范

# 创建 1 行 3 列的画布
fig, axes = plt.subplots(1, 3, figsize=(22, 7))
plt.subplots_adjust(wspace=0.25)

metrics = ['IOPS', 'Bandwidth (MiB/s)', 'Latency (usec)']
# 使用经典的学术配色方案
colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"] 

# 3. 循环绘制三个指标的子图
for i, metric in enumerate(metrics):
    sns.barplot(
        data=df,
        x='Workload',
        y=metric,
        hue='Engine',
        ax=axes[i],
        palette=colors,
        edgecolor='black',
        linewidth=1.2
    )
    
    # 设置子图标题和坐标轴标签
    axes[i].set_title(f'{metric} Comparison', fontsize=16, fontweight='bold', pad=20)
    axes[i].set_xlabel('Workload Type', fontsize=14)
    axes[i].set_ylabel(metric, fontsize=14)
    
    # 移除子图内部的图例，稍后统一生成
    axes[i].get_legend().remove()

# 4. 在画布上方统一放置图例
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.05), 
           ncol=4, fontsize=14, title='I/O Engines', title_fontsize=15, frameon=True)

# 5. 保存并展示
plt.tight_layout(rect=[0, 0, 1, 0.93]) # 为顶部的图例留出空间
plt.savefig("IO_Engine_Analysis.pdf", format='pdf', bbox_inches='tight')
print("IO_Engine_Analysis.pdf")
plt.show()