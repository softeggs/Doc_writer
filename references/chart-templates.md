# 汇报图表模板

本文档提供标准化的数据可视化图表模板，包含饼图和堆叠柱状图的组合布局。

---

## 📊 图表示例

### 示例1：峰值检测方法分析

![峰值来源分析](images/04_Peak_Source_Analysis.png)

**图表说明**：
- 左侧：饼图展示峰值来源的总体分布
- 右侧：堆叠柱状图展示各被试的峰值来源统计

---

### 示例2：心率脉率变化程度分类

![心率脉率变化分类](images/05_HR_PR_Change_Classification.png)

**图表说明**：
- 上排：饼图展示心率和脉率变化程度的总体分布
- 下排：堆叠柱状图展示各被试的变化程度统计

---

## 💻 标准代码模板

### 模板1：1×2布局（饼图 + 堆叠柱状图）

适用于单一维度的分类统计分析。

```python
import os
import json
import numpy as np
import matplotlib.pyplot as plt

def generate_classification_analysis(data, output_dir):
    """
    生成分类分析图表（1×2布局）
    
    参数:
        data: 数据列表
        output_dir: 输出目录
    """
    # 数据分类统计
    category_a = [item for item in data if item['category'] == 'A']
    category_b = [item for item in data if item['category'] == 'B']
    
    # 创建图表 - 1×2布局
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Classification Analysis', fontsize=18, fontweight='bold')
    
    # 1. 饼图 - 总体分布
    ax1 = axes[0]
    sizes = [len(category_a), len(category_b)]
    labels = [f'Category A\n{len(category_a)} cases ({len(category_a)/len(data)*100:.1f}%)',
              f'Category B\n{len(category_b)} cases ({len(category_b)/len(data)*100:.1f}%)']
    colors = ['#66b3ff', '#ff9999']
    explode = (0.05, 0)  # 突出显示第一个扇区
    
    ax1.pie(sizes, explode=explode, labels=labels, colors=colors, 
            autopct='%1.1f%%', shadow=True, startangle=90,
            textprops={'fontsize': 12, 'fontweight': 'bold'})
    ax1.set_title('Distribution', fontsize=14, fontweight='bold')
    
    # 2. 堆叠柱状图 - 按分组统计
    ax2 = axes[1]
    groups = sorted(set(item['group'] for item in data))
    
    a_counts = []
    b_counts = []
    
    for group in groups:
        group_data = [item for item in data if item['group'] == group]
        a_counts.append(sum(1 for item in group_data if item['category'] == 'A'))
        b_counts.append(sum(1 for item in group_data if item['category'] == 'B'))
    
    x = np.arange(len(groups))
    width = 0.6
    
    p1 = ax2.bar(x, a_counts, width, label='Category A', 
                 color='steelblue', alpha=0.8)
    p2 = ax2.bar(x, b_counts, width, bottom=a_counts, 
                 label='Category B', color='coral', alpha=0.8)
    
    ax2.set_xlabel('Group', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax2.set_title('Statistics by Group', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(groups, rotation=45)
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'classification_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")
```

---

### 模板2：2×2布局（多维度分类分析）

适用于两个维度的分类统计分析。

```python
import os
import json
import numpy as np
import matplotlib.pyplot as plt

def generate_multi_classification_analysis(data, output_dir):
    """
    生成多维度分类分析图表（2×2布局）
    
    参数:
        data: 数据列表
        output_dir: 输出目录
    """
    # 维度1数据分类
    dim1_cat_a = [item for item in data if item['dim1_category'] == 'A']
    dim1_cat_b = [item for item in data if item['dim1_category'] == 'B']
    dim1_cat_c = [item for item in data if item['dim1_category'] == 'C']
    
    # 维度2数据分类
    dim2_cat_a = [item for item in data if item['dim2_category'] == 'A']
    dim2_cat_b = [item for item in data if item['dim2_category'] == 'B']
    dim2_cat_c = [item for item in data if item['dim2_category'] == 'C']
    
    # 创建图表 - 2×2布局
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Multi-Dimension Classification Analysis', 
                 fontsize=18, fontweight='bold')
    
    # 1. 维度1饼图
    ax1 = axes[0, 0]
    dim1_sizes = [len(dim1_cat_a), len(dim1_cat_b), len(dim1_cat_c)]
    dim1_labels = [
        f'Category A\n{len(dim1_cat_a)} cases ({len(dim1_cat_a)/len(data)*100:.1f}%)',
        f'Category B\n{len(dim1_cat_b)} cases ({len(dim1_cat_b)/len(data)*100:.1f}%)',
        f'Category C\n{len(dim1_cat_c)} cases ({len(dim1_cat_c)/len(data)*100:.1f}%)'
    ]
    colors = ['#66b3ff', '#ffcc99', '#ff9999']
    explode = (0.05, 0, 0)
    
    ax1.pie(dim1_sizes, explode=explode, labels=dim1_labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax1.set_title('Dimension 1 Classification', fontsize=14, fontweight='bold')
    
    # 2. 维度2饼图
    ax2 = axes[0, 1]
    dim2_sizes = [len(dim2_cat_a), len(dim2_cat_b), len(dim2_cat_c)]
    dim2_labels = [
        f'Category A\n{len(dim2_cat_a)} cases ({len(dim2_cat_a)/len(data)*100:.1f}%)',
        f'Category B\n{len(dim2_cat_b)} cases ({len(dim2_cat_b)/len(data)*100:.1f}%)',
        f'Category C\n{len(dim2_cat_c)} cases ({len(dim2_cat_c)/len(data)*100:.1f}%)'
    ]
    
    ax2.pie(dim2_sizes, explode=explode, labels=dim2_labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('Dimension 2 Classification', fontsize=14, fontweight='bold')
    
    # 3. 维度1堆叠柱状图
    ax3 = axes[1, 0]
    groups = sorted(set(item['group'] for item in data))
    
    dim1_a_counts = []
    dim1_b_counts = []
    dim1_c_counts = []
    
    for group in groups:
        group_data = [item for item in data if item['group'] == group]
        dim1_a_counts.append(sum(1 for item in group_data if item['dim1_category'] == 'A'))
        dim1_b_counts.append(sum(1 for item in group_data if item['dim1_category'] == 'B'))
        dim1_c_counts.append(sum(1 for item in group_data if item['dim1_category'] == 'C'))
    
    x = np.arange(len(groups))
    width = 0.6
    
    p1 = ax3.bar(x, dim1_a_counts, width, label='Category A', 
                 color='#66b3ff', alpha=0.8)
    p2 = ax3.bar(x, dim1_b_counts, width, bottom=dim1_a_counts,
                 label='Category B', color='#ffcc99', alpha=0.8)
    bottom_c = [dim1_a_counts[i] + dim1_b_counts[i] for i in range(len(groups))]
    p3 = ax3.bar(x, dim1_c_counts, width, bottom=bottom_c,
                 label='Category C', color='#ff9999', alpha=0.8)
    
    ax3.set_xlabel('Group', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax3.set_title('Dimension 1 by Group', fontsize=14, fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(groups, rotation=45)
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. 维度2堆叠柱状图
    ax4 = axes[1, 1]
    
    dim2_a_counts = []
    dim2_b_counts = []
    dim2_c_counts = []
    
    for group in groups:
        group_data = [item for item in data if item['group'] == group]
        dim2_a_counts.append(sum(1 for item in group_data if item['dim2_category'] == 'A'))
        dim2_b_counts.append(sum(1 for item in group_data if item['dim2_category'] == 'B'))
        dim2_c_counts.append(sum(1 for item in group_data if item['dim2_category'] == 'C'))
    
    p1 = ax4.bar(x, dim2_a_counts, width, label='Category A',
                 color='#66b3ff', alpha=0.8)
    p2 = ax4.bar(x, dim2_b_counts, width, bottom=dim2_a_counts,
                 label='Category B', color='#ffcc99', alpha=0.8)
    bottom_c = [dim2_a_counts[i] + dim2_b_counts[i] for i in range(len(groups))]
    p3 = ax4.bar(x, dim2_c_counts, width, bottom=bottom_c,
                 label='Category C', color='#ff9999', alpha=0.8)
    
    ax4.set_xlabel('Group', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax4.set_title('Dimension 2 by Group', fontsize=14, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(groups, rotation=45)
    ax4.legend()
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'multi_classification_analysis.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")
```

---

## 🎨 配色方案

### 标准配色（3分类）

```python
# 推荐配色方案
colors = ['#66b3ff', '#ffcc99', '#ff9999']  # 蓝、橙、红

# 含义映射
# 蓝色 (#66b3ff): 正常/无变化/主要类别
# 橙色 (#ffcc99): 中等/轻微变化/次要类别  
# 红色 (#ff9999): 异常/显著变化/警示类别
```

### 标准配色（2分类）

```python
# 推荐配色方案
colors = ['#66b3ff', '#ff9999']  # 蓝、红

# 或者
colors = ['steelblue', 'coral']  # 钢蓝、珊瑚红
```

---

## 📐 图表规格

### 布局尺寸

```python
# 1×2布局
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# 2×2布局
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
```

### 字体设置

```python
# 主标题
fig.suptitle('Title', fontsize=18, fontweight='bold')

# 子图标题
ax.set_title('Subtitle', fontsize=14, fontweight='bold')

# 坐标轴标签
ax.set_xlabel('Label', fontsize=12, fontweight='bold')
ax.set_ylabel('Label', fontsize=12, fontweight='bold')

# 饼图文本
textprops={'fontsize': 11, 'fontweight': 'bold'}
```

### 输出设置

```python
# 高分辨率输出
plt.savefig(output_path, dpi=300, bbox_inches='tight')
```

---

## 🔧 关键参数说明

### 饼图参数

```python
ax.pie(
    sizes,              # 数据大小列表
    explode=explode,    # 突出显示，如 (0.05, 0, 0)
    labels=labels,      # 标签列表
    colors=colors,      # 颜色列表
    autopct='%1.1f%%',  # 百分比格式
    shadow=True,        # 阴影效果
    startangle=90,      # 起始角度
    textprops={...}     # 文本属性
)
```

### 堆叠柱状图参数

```python
ax.bar(
    x,                  # x轴位置
    heights,            # 柱高度
    width,              # 柱宽度，如 0.6
    bottom=bottom,      # 堆叠起始位置
    label='Label',      # 图例标签
    color='color',      # 颜色
    alpha=0.8          # 透明度
)
```

---

## 📝 使用示例

### 示例：峰值检测方法分析

```python
import os
import json
import numpy as np
import matplotlib.pyplot as plt

# 加载数据
with open('data.json', 'r') as f:
    all_cases = json.load(f)

# 分类统计
svm_cases = [c for c in all_cases if c['peak_source'] == 'svm_max']
algo_cases = [c for c in all_cases if c['peak_source'] == 'algorithm']

# 创建图表
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Peak Detection Method Analysis', fontsize=18, fontweight='bold')

# 饼图
ax1 = axes[0]
sizes = [len(svm_cases), len(algo_cases)]
labels = [f'SVM Maximum\n{len(svm_cases)} cases ({len(svm_cases)/len(all_cases)*100:.1f}%)',
          f'Algorithm Peak\n{len(algo_cases)} cases ({len(algo_cases)/len(all_cases)*100:.1f}%)']
colors = ['#66b3ff', '#ff9999']
explode = (0.05, 0)

ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
        shadow=True, startangle=90, textprops={'fontsize': 12, 'fontweight': 'bold'})
ax1.set_title('Peak Source Distribution', fontsize=14, fontweight='bold')

# 堆叠柱状图
ax2 = axes[1]
subjects = sorted(set(c['subject'] for c in all_cases))

svm_counts = []
algo_counts = []

for subject in subjects:
    subject_cases = [c for c in all_cases if c['subject'] == subject]
    svm_counts.append(sum(1 for c in subject_cases if c['peak_source'] == 'svm_max'))
    algo_counts.append(sum(1 for c in subject_cases if c['peak_source'] == 'algorithm'))

x = np.arange(len(subjects))
width = 0.6

p1 = ax2.bar(x, svm_counts, width, label='SVM Maximum', color='steelblue', alpha=0.8)
p2 = ax2.bar(x, algo_counts, width, bottom=svm_counts, label='Algorithm Peak', color='coral', alpha=0.8)

ax2.set_xlabel('Subject', fontsize=12, fontweight='bold')
ax2.set_ylabel('Count', fontsize=12, fontweight='bold')
ax2.set_title('Peak Source Statistics by Subject', fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(subjects, rotation=45)
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('peak_analysis.png', dpi=300, bbox_inches='tight')
plt.close()
```

---

## ✅ 最佳实践

### 1. 数据准备

- 确保数据完整性和有效性
- 提前进行数据分类和统计
- 计算好百分比和标签

### 2. 颜色选择

- 使用对比鲜明的颜色
- 保持配色一致性
- 考虑色盲友好性

### 3. 标签设置

- 饼图标签包含数量和百分比
- 坐标轴标签清晰明确
- 图例位置合理

### 4. 布局优化

- 使用 `plt.tight_layout()` 自动调整
- 设置合适的图表尺寸
- 旋转过长的x轴标签

### 5. 输出质量

- 使用 `dpi=300` 确保高清输出
- 使用 `bbox_inches='tight'` 避免裁剪
- 选择合适的文件格式（PNG/PDF）

---

## 📚 相关文件

- `generate_hr_change_classification.py` - 心率脉率变化分类脚本（英文版）
- `generate_hr_change_classification_cn.py` - 心率脉率变化分类脚本（中文版）
- `generate_analysis_report_en.py` - 完整分析报告生成脚本

---

**创建时间**: 2025年12月10日  
**版本**: V1.0  
**适用场景**: 数据分类统计、对比分析、汇报展示
