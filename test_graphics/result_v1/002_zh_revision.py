import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- 解决中文显示问题 ---
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# --------------------------

# --- 数据生成 ---
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
data = {
    'Month': months,
    'Product_A_Sales': np.random.randint(100, 500, size=12),
    'Product_B_Sales': np.random.randint(150, 600, size=12),
    'Product_C_Sales': np.random.randint(80, 450, size=12)
}
sales_df = pd.DataFrame(data)
sales_df.set_index('Month', inplace=True)

# --- 数据处理 ---
total_sales = sales_df.sum()

# 为图表创建更友好的产品名称映射
product_display_names = {
    'Product_A_Sales': '产品A',
    'Product_B_Sales': '产品B',
    'Product_C_Sales': '产品C'
}
# 为柱状图准备带有友好名称的数据
bar_chart_labels = [product_display_names[col] for col in total_sales.index]
total_sales_for_plot = pd.Series(total_sales.values, index=bar_chart_labels)

# --- 可视化 ---
# 应用Seaborn风格，选择'notebook'风格以获得更好的默认字体大小，并手动调整
plt.style.use('seaborn-v0_8-notebook')

# 定义统一的字体大小
TITLE_FONTSIZE = 20
LABEL_FONTSIZE = 16
TICK_FONTSIZE = 14
LEGEND_FONTSIZE = 14
BAR_LABEL_FONTSIZE = 12

# 创建子图：使用1行2列布局，使图表更紧凑和专业
fig, axes = plt.subplots(1, 2, figsize=(16, 7)) # 调整整体图表尺寸

# 子图1：总销量对比柱状图
ax1 = axes[0]
# 使用plt.cm.Paired调色板，使颜色搭配更专业和谐
bars = ax1.bar(total_sales_for_plot.index, total_sales_for_plot.values,
               color=plt.cm.Paired(np.arange(len(total_sales_for_plot))))

ax1.set_title('产品年度总销量对比', fontsize=TITLE_FONTSIZE)
ax1.set_ylabel('总销量 (单位)', fontsize=LABEL_FONTSIZE)
ax1.set_xlabel('产品名称', fontsize=LABEL_FONTSIZE)
ax1.tick_params(axis='x', labelsize=TICK_FONTSIZE)
ax1.tick_params(axis='y', labelsize=TICK_FONTSIZE)
# 调整Y轴上限，为数据标签留出空间
ax1.set_ylim(0, total_sales_for_plot.max() * 1.15)

# 在柱状图上方添加数据标签
for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2, yval + (total_sales_for_plot.max() * 0.03), # 动态调整标签位置
             f'{yval:.0f}', ha='center', va='bottom', fontsize=BAR_LABEL_FONTSIZE)

# 子图2：月度销售趋势折线图
ax2 = axes[1]
# 修改DataFrame的列名，以便绘图时图例显示友好名称
sales_df_renamed = sales_df.rename(columns=product_display_names)
sales_df_renamed.plot(ax=ax2, marker='o', linewidth=2) # 增加线宽使线条更清晰

ax2.set_title('月度销售趋势', fontsize=TITLE_FONTSIZE)
ax2.set_ylabel('月度销量 (单位)', fontsize=LABEL_FONTSIZE)
ax2.set_xlabel('月份', fontsize=LABEL_FONTSIZE)
ax2.tick_params(axis='x', rotation=45, labelsize=TICK_FONTSIZE)
ax2.tick_params(axis='y', labelsize=TICK_FONTSIZE)
ax2.legend(title='产品', fontsize=LEGEND_FONTSIZE, title_fontsize=LEGEND_FONTSIZE) # 添加图例标题
ax2.grid(True, linestyle='--', alpha=0.7) # 添加网格线，增强可读性

# 确保布局紧凑且不重叠，并增加边距
plt.tight_layout(pad=3.0)

# 显示生成的图表
plt.show()