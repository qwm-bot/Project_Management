import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import glob
from pathlib import Path
# 这里是B2的第一处修改
# Set up matplotlib for better visualization
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10

class FIOResultParser:
    def __init__(self, base_path):
        self.base_path = base_path
        self.data = []
        
    def extract_metrics(self, file_path, file_name):
        """Extract IOPS, BW and latency from FIO output file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract metrics using regex
            iops_match = re.search(r'IOPS=(\d+)', content)
            bw_match = re.search(r'BW=([0-9.]+)([KMG]i?B/s)', content)
            lat_match = re.search(r'avg=(\d+\.?\d*)', content)
            
            if iops_match and bw_match and lat_match:
                iops = int(iops_match.group(1))
                bw_value = float(bw_match.group(1))
                bw_unit = bw_match.group(2)
                latency = float(lat_match.group(1))  # in microseconds
                
                # Convert BW to MiB/s for consistency
                if 'KiB/s' in bw_unit or 'KB/s' in bw_unit:
                    bw_mbs = bw_value / 1024
                elif 'GiB/s' in bw_unit or 'GB/s' in bw_unit:
                    bw_mbs = bw_value * 1024
                else:  # MiB/s or MB/s
                    bw_mbs = bw_value
                
                return {
                    'iops': iops,
                    'bw': bw_mbs,
                    'latency': latency
                }
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return None
    
    def parse_directory(self, dir_path, category):
        """Parse all files in a directory"""
        files = glob.glob(os.path.join(dir_path, '*.txt'))
        
        for file_path in sorted(files):
            file_name = os.path.basename(file_path)
            metrics = self.extract_metrics(file_path, file_name)
            
            if metrics:
                # Parse file name for attributes
                parts = file_name.replace('.txt', '').split('_')
                
                operation = 'read' if 'read' in file_name else 'write'
                
                # Determine test type
                if 'read' in parts[0] or 'write' in parts[0]:
                    test_type = parts[0]
                
                entry = {
                    'file': file_name,
                    'category': category,
                    'operation': operation,
                    **metrics
                }
                
                # Add category-specific attributes
                if category == 'baseline':
                    if 'rand' in file_name:
                        entry['pattern'] = 'Random'
                    else:
                        entry['pattern'] = 'Sequential'
                
                elif category == 'block_size':
                    # Extract block size
                    bs_match = re.search(r'bs_(\d+)([k])', file_name)
                    if bs_match:
                        entry['block_size'] = f"{bs_match.group(1)}{bs_match.group(2)}"
                    if 'rand' in file_name:
                        entry['pattern'] = 'Random'
                    else:
                        entry['pattern'] = 'Sequential'
                
                elif category == 'concurrency':
                    # Extract jobs and depth
                    jobs_match = re.search(r'jobs_(\d+)', file_name)
                    depth_match = re.search(r'depth_(\d+)', file_name)
                    if jobs_match:
                        entry['jobs'] = int(jobs_match.group(1))
                    if depth_match:
                        entry['depth'] = int(depth_match.group(1))
                    if 'rand' in file_name:
                        entry['pattern'] = 'Random'
                    else:
                        entry['pattern'] = 'Sequential'
                
                elif category == 'ioengine':
                    # Extract IO engine
                    engines = ['uring', 'libaio', 'mmap', 'pvsync']
                    for engine in engines:
                        if engine in file_name:
                            entry['engine'] = engine
                            break
                    if 'rand' in file_name:
                        entry['pattern'] = 'Random'
                    else:
                        entry['pattern'] = 'Sequential'
                
                self.data.append(entry)
    
    def load_all_data(self):
        """Load data from all directories"""
        base = self.base_path
        
        # Define directory mappings
        dirs = {
            'baseline': os.path.join(base, 'baseline_results'),
            'block_size': os.path.join(base, 'bs_test_results'),
            'concurrency': os.path.join(base, 'concurrency_results'),
            'ioengine': os.path.join(base, 'ioengine_results')
        }
        
        for category, dir_path in dirs.items():
            if os.path.exists(dir_path):
                print(f"Parsing {category}...")
                self.parse_directory(dir_path, category)
        
        return pd.DataFrame(self.data)

def create_visualizations(df, base_path):
    """Create comprehensive visualizations from FIO data"""
    
    # Create PDF with multiple pages
    pdf_path = os.path.join(base_path, 'fio_analysis.pdf')
    
    with PdfPages(pdf_path) as pdf:
        
        # ============ Page 1: Baseline Comparison ==============
        baseline_df = df[df['category'] == 'baseline'].copy()
        if len(baseline_df) > 0:
            baseline_df = baseline_df.sort_values('operation')
            
            fig, axes = plt.subplots(2, 3, figsize=(16, 10))
            fig.suptitle('Baseline Performance Comparison (4KB, 1 Job, Depth 1)', fontsize=14, fontweight='bold')
            
            # IOPS comparison
            ax = axes[0, 0]
            colors = ['#FF6B6B' if op == 'read' else '#4ECDC4' for op in baseline_df['operation']]
            bars = ax.bar(baseline_df['file'], baseline_df['iops'], color=colors, alpha=0.7, edgecolor='black')
            ax.set_ylabel('IOPS', fontsize=11, fontweight='bold')
            ax.set_title('IOPS Performance', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)
            
            # BW comparison
            ax = axes[0, 1]
            bars = ax.bar(baseline_df['file'], baseline_df['bw'], color=colors, alpha=0.7, edgecolor='black')
            ax.set_ylabel('Bandwidth (MiB/s)', fontsize=11, fontweight='bold')
            ax.set_title('Bandwidth Performance', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=9)
            
            # Latency comparison
            ax = axes[0, 2]
            bars = ax.bar(baseline_df['file'], baseline_df['latency'], color=colors, alpha=0.7, edgecolor='black')
            ax.set_ylabel('Latency (µs)', fontsize=11, fontweight='bold')
            ax.set_title('Latency Performance', fontweight='bold')
            ax.tick_params(axis='x', rotation=45)
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=9)
            
            # Table with values
            ax = axes[1, 0]
            ax.axis('off')
            table_data = []
            table_data.append(['Test Type', 'IOPS', 'BW (MiB/s)', 'Latency (µs)'])
            for idx, row in baseline_df.iterrows():
                table_data.append([
                    row['file'].replace('.txt', ''),
                    f"{int(row['iops'])}",
                    f"{row['bw']:.2f}",
                    f"{row['latency']:.2f}"
                ])
            table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                           colWidths=[0.3, 0.23, 0.23, 0.24])
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 2)
            for i in range(len(table_data)):
                if i == 0:
                    table[(i, 0)].set_facecolor('#40466e')
                    table[(i, 1)].set_facecolor('#40466e')
                    table[(i, 2)].set_facecolor('#40466e')
                    table[(i, 3)].set_facecolor('#40466e')
                    for j in range(4):
                        table[(i, j)].set_text_props(weight='bold', color='white')
            
            # IOPS/Latency trade-off scatter plot
            ax = axes[1, 1]
            for op in baseline_df['operation'].unique():
                data = baseline_df[baseline_df['operation'] == op]
                color = '#FF6B6B' if op == 'read' else '#4ECDC4'
                ax.scatter(data['latency'], data['iops'], s=300, color=color, alpha=0.6, 
                          label=op.capitalize(), edgecolor='black', linewidth=2)
            ax.set_xlabel('Latency (µs)', fontsize=11, fontweight='bold')
            ax.set_ylabel('IOPS', fontsize=11, fontweight='bold')
            ax.set_title('IOPS vs Latency Trade-off', fontweight='bold')
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # BW/Latency correlation
            ax = axes[1, 2]
            for op in baseline_df['operation'].unique():
                data = baseline_df[baseline_df['operation'] == op]
                color = '#FF6B6B' if op == 'read' else '#4ECDC4'
                ax.scatter(data['latency'], data['bw'], s=300, color=color, alpha=0.6,
                          label=op.capitalize(), edgecolor='black', linewidth=2)
            ax.set_xlabel('Latency (µs)', fontsize=11, fontweight='bold')
            ax.set_ylabel('Bandwidth (MiB/s)', fontsize=11, fontweight='bold')
            ax.set_title('Bandwidth vs Latency', fontweight='bold')
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
        
        # ============ Page 2: Block Size Impact ==============
        bs_df = df[df['category'] == 'block_size'].copy()
        if len(bs_df) > 0:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            fig.suptitle('Impact of Block Size on Performance', fontsize=14, fontweight='bold')
            
            # Extract block size in numeric form for sorting
            def extract_bs_value(bs_str):
                match = re.search(r'(\d+)', bs_str)
                return int(match.group(1)) if match else 0
            
            bs_df['bs_numeric'] = bs_df['block_size'].apply(extract_bs_value)
            
            for idx, (op, ax) in enumerate(zip(['read', 'write'], axes.flat[:2])):
                op_data = bs_df[bs_df['operation'] == op].sort_values('bs_numeric')
                if len(op_data) > 0:
                    x_labels = op_data['block_size'].values
                    x_pos = np.arange(len(x_labels))
                    
                    ax2 = ax.twinx()
                    
                    bars = ax.bar(x_pos - 0.2, op_data['iops'], width=0.4, 
                                 label='IOPS', color='#FF6B6B', alpha=0.7, edgecolor='black')
                    line = ax2.plot(x_pos, op_data['latency'], 'o-', color='#4ECDC4',
                                   linewidth=2.5, markersize=8, label='Latency', markeredgecolor='black')
                    
                    ax.set_xlabel('Block Size', fontsize=11, fontweight='bold')
                    ax.set_ylabel('IOPS', fontsize=11, fontweight='bold', color='#FF6B6B')
                    ax2.set_ylabel('Latency (µs)', fontsize=11, fontweight='bold', color='#4ECDC4')
                    ax.set_title(f'{op.capitalize()} - Block Size Impact', fontweight='bold')
                    ax.set_xticks(x_pos)
                    ax.set_xticklabels(x_labels)
                    ax.tick_params(axis='y', labelcolor='#FF6B6B')
                    ax2.tick_params(axis='y', labelcolor='#4ECDC4')
                    ax.grid(True, alpha=0.3)
                    
                    # Add value labels
                    for i, (bar, lat) in enumerate(zip(bars, op_data['latency'])):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{int(height)}', ha='center', va='bottom', fontsize=9)
            
            # Bandwidth vs Block Size
            for idx, op in enumerate(['read', 'write']):
                ax = axes.flat[2 + idx]
                op_data = bs_df[bs_df['operation'] == op].sort_values('bs_numeric')
                if len(op_data) > 0:
                    x_labels = op_data['block_size'].values
                    x_pos = np.arange(len(x_labels))
                    bars = ax.bar(x_pos, op_data['bw'], color='#6C5CE7', alpha=0.7, edgecolor='black')
                    ax.set_xlabel('Block Size', fontsize=11, fontweight='bold')
                    ax.set_ylabel('Bandwidth (MiB/s)', fontsize=11, fontweight='bold')
                    ax.set_title(f'{op.capitalize()} - Bandwidth vs Block Size', fontweight='bold')
                    ax.set_xticks(x_pos)
                    ax.set_xticklabels(x_labels)
                    ax.grid(True, alpha=0.3, axis='y')
                    
                    for bar in bars:
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                               f'{height:.1f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
        
        # ============ Page 3: Concurrency Impact ==============
        conc_df = df[df['category'] == 'concurrency'].copy()
        if len(conc_df) > 0:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            fig.suptitle('Impact of Concurrency on Performance', fontsize=14, fontweight='bold')
            
            # Plot for each pattern (Random/Sequential) x (Read/Write)
            for pattern_idx, pattern in enumerate(['Random', 'Sequential']):
                for op_idx, op in enumerate(['read', 'write']):
                    ax = axes[pattern_idx, op_idx]
                    
                    pattern_data = conc_df[(conc_df['pattern'] == pattern) & 
                                         (conc_df['operation'] == op)].copy()
                    
                    if len(pattern_data) > 0:
                        # Group by jobs and depth
                        for depth in sorted(pattern_data['depth'].unique()):
                            depth_data = pattern_data[pattern_data['depth'] == depth].sort_values('jobs')
                            ax.plot(depth_data['jobs'], depth_data['iops'], marker='o',
                                   linewidth=2.5, markersize=8, label=f'Depth={depth}',
                                   markeredgecolor='black', markeredgewidth=1)
                        
                        ax.set_xlabel('Number of Jobs', fontsize=11, fontweight='bold')
                        ax.set_ylabel('IOPS', fontsize=11, fontweight='bold')
                        ax.set_title(f'{pattern} {op.capitalize()} - Impact of Concurrency', fontweight='bold')
                        ax.legend(fontsize=10)
                        ax.grid(True, alpha=0.3)
                        ax.set_xticks(sorted(pattern_data['jobs'].unique()))
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
        
        # ============ Page 4: IO Engine Comparison ==============
        engine_df = df[df['category'] == 'ioengine'].copy()
        if len(engine_df) > 0:
            fig, axes = plt.subplots(2, 2, figsize=(16, 10))
            fig.suptitle('IO Engine Comparison', fontsize=14, fontweight='bold')
            
            # IOPS by engine
            ax = axes[0, 0]
            engine_iops = engine_df.groupby(['engine', 'operation'])['iops'].first().unstack()
            engine_iops.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4'], alpha=0.7, edgecolor='black')
            ax.set_ylabel('IOPS', fontsize=11, fontweight='bold')
            ax.set_title('IOPS by IO Engine', fontweight='bold')
            ax.set_xlabel('IO Engine', fontsize=11, fontweight='bold')
            ax.legend(title='Operation', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            ax.tick_params(axis='x', rotation=45)
            
            # BW by engine
            ax = axes[0, 1]
            engine_bw = engine_df.groupby(['engine', 'operation'])['bw'].first().unstack()
            engine_bw.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4'], alpha=0.7, edgecolor='black')
            ax.set_ylabel('Bandwidth (MiB/s)', fontsize=11, fontweight='bold')
            ax.set_title('Bandwidth by IO Engine', fontweight='bold')
            ax.set_xlabel('IO Engine', fontsize=11, fontweight='bold')
            ax.legend(title='Operation', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            ax.tick_params(axis='x', rotation=45)
            
            # Latency by engine
            ax = axes[1, 0]
            engine_lat = engine_df.groupby(['engine', 'operation'])['latency'].first().unstack()
            engine_lat.plot(kind='bar', ax=ax, color=['#FF6B6B', '#4ECDC4'], alpha=0.7, edgecolor='black')
            ax.set_ylabel('Latency (µs)', fontsize=11, fontweight='bold')
            ax.set_title('Latency by IO Engine', fontweight='bold')
            ax.set_xlabel('IO Engine', fontsize=11, fontweight='bold')
            ax.legend(title='Operation', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            ax.tick_params(axis='x', rotation=45)
            
            # Overall engine ranking
            ax = axes[1, 1]
            ax.axis('off')
            
            # Calculate composite score (IOPS weight 40%, BW weight 40%, Latency weight 20% inverse)
            engine_df['iops_norm'] = engine_df['iops'] / engine_df['iops'].max() * 40
            engine_df['bw_norm'] = engine_df['bw'] / engine_df['bw'].max() * 40
            engine_df['lat_norm'] = (1 - engine_df['latency'] / engine_df['latency'].max()) * 20
            engine_df['score'] = engine_df['iops_norm'] + engine_df['bw_norm'] + engine_df['lat_norm']
            
            ranking = engine_df.groupby('engine')['score'].mean().sort_values(ascending=False)
            
            text_str = "Performance Score Ranking\n(IOPS: 40%, BW: 40%, Latency: 20%)\n\n"
            for rank, (engine, score) in enumerate(ranking.items(), 1):
                text_str += f"{rank}. {engine.upper():10} - {score:.1f}/100\n"
            
            ax.text(0.1, 0.5, text_str, fontsize=12, fontfamily='monospace',
                   verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            ax.set_title('Performance Ranking', fontweight='bold', fontsize=12)
            
            plt.tight_layout()
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()
        
        # ============ Page 5: Summary Statistics ==============
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle('Summary Statistics and Insights', fontsize=14, fontweight='bold')
        
        gs = fig.add_gridspec(3, 2, hspace=0.4, wspace=0.3)
        
        # Overall statistics table
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('off')
        
        stats_data = []
        stats_data.append(['Metric', 'Min', 'Max', 'Mean', 'Std Dev'])
        stats_data.append(['IOPS', f"{df['iops'].min():.0f}", f"{df['iops'].max():.0f}", 
                          f"{df['iops'].mean():.0f}", f"{df['iops'].std():.0f}"])
        stats_data.append(['Bandwidth (MiB/s)', f"{df['bw'].min():.2f}", f"{df['bw'].max():.2f}",
                          f"{df['bw'].mean():.2f}", f"{df['bw'].std():.2f}"])
        stats_data.append(['Latency (µs)', f"{df['latency'].min():.2f}", f"{df['latency'].max():.2f}",
                          f"{df['latency'].mean():.2f}", f"{df['latency'].std():.2f}"])
        
        table = ax1.table(cellText=stats_data, cellLoc='center', loc='center', colWidths=[0.2, 0.2, 0.2, 0.2, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.5)
        for i in range(len(stats_data)):
            for j in range(5):
                if i == 0:
                    table[(i, j)].set_facecolor('#40466e')
                    table[(i, j)].set_text_props(weight='bold', color='white')
                else:
                    table[(i, j)].set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
        
        # Distribution plots
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.hist(df['iops'], bins=20, color='#FF6B6B', alpha=0.7, edgecolor='black')
        ax2.set_xlabel('IOPS', fontweight='bold')
        ax2.set_ylabel('Frequency', fontweight='bold')
        ax2.set_title('IOPS Distribution', fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.hist(df['latency'], bins=20, color='#4ECDC4', alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Latency (µs)', fontweight='bold')
        ax3.set_ylabel('Frequency', fontweight='bold')
        ax3.set_title('Latency Distribution', fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Read vs Write comparison
        ax4 = fig.add_subplot(gs[2, 0])
        read_data = df[df['operation'] == 'read']
        write_data = df[df['operation'] == 'write']
        
        metrics = ['IOPS', 'BW', 'Latency']
        read_vals = [read_data['iops'].mean(), read_data['bw'].mean(), read_data['latency'].mean()]
        write_vals = [write_data['iops'].mean(), write_data['bw'].mean(), write_data['latency'].mean()]
        
        # Normalize latency for comparison (inverse)
        read_vals[2] = 1000 / read_vals[2]  # Convert to operations/ms
        write_vals[2] = 1000 / write_vals[2]
        
        x_pos = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax4.bar(x_pos - width/2, read_vals, width, label='Read', color='#FF6B6B', alpha=0.7, edgecolor='black')
        bars2 = ax4.bar(x_pos + width/2, write_vals, width, label='Write', color='#4ECDC4', alpha=0.7, edgecolor='black')
        
        ax4.set_ylabel('Performance (normalized)', fontweight='bold')
        ax4.set_title('Read vs Write Performance Comparison', fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(metrics)
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3, axis='y')
        
        # Category breakdown
        ax5 = fig.add_subplot(gs[2, 1])
        category_counts = df['category'].value_counts()
        colors_pie = ['#FF6B6B', '#4ECDC4', '#6C5CE7', '#FDA7DF']
        wedges, texts, autotexts = ax5.pie(category_counts.values, labels=category_counts.index.str.upper(),
                                            autopct='%1.1f%%', colors=colors_pie[:len(category_counts)],
                                            startangle=90, textprops={'fontsize': 10, 'weight': 'bold'})
        for autotext in autotexts:
            autotext.set_color('white')
        ax5.set_title('Test Distribution by Category', fontweight='bold')
        
        plt.suptitle('Summary Statistics and Insights', fontsize=14, fontweight='bold', y=0.995)
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    print(f"\n✓ PDF report saved: {pdf_path}")
    return pdf_path

# Main execution
if __name__ == "__main__":
    base_path = r'd:\fio_test'
    
    # Parse all FIO results
    parser = FIOResultParser(base_path)
    df = parser.load_all_data()
    
    print(f"\nTotal tests parsed: {len(df)}")
    print(f"\nData categories:")
    print(df['category'].value_counts())
    print(f"\nOperations breakdown:")
    print(df['operation'].value_counts())
    
    print("\n" + "="*60)
    print("Generating visualizations...")
    print("="*60)
    
    # Create visualizations and save to PDF
    create_visualizations(df, base_path)
    
    print("\n✓ Analysis complete!")
    print(f"✓ Total data points analyzed: {len(df)}")
