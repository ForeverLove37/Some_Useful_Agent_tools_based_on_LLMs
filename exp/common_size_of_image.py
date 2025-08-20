import matplotlib.pyplot as plt
import numpy as np

# 使用更具科学感的样式
plt.style.use('seaborn-v0_8-paper')

# --- 图表与字体尺寸设置 (基于通用期刊指南) ---

# 图表尺寸（英寸）。常见的单栏宽度为3.5英寸。
# 高度可以根据图表的长宽比进行调整。
fig_width_in = 3.5
fig_height_in = 2.5

# 字体大小（磅）。通常建议在8到12磅之间。
# 标题通常比坐标轴标签稍大，坐标轴标签又比刻度标签稍大。
title_fontsize = 12
label_fontsize = 10
tick_fontsize = 8
legend_fontsize = 8

# 设置全局字体参数
plt.rcParams.update({
    'font.size': label_fontsize,
    'axes.titlesize': title_fontsize,
    'axes.labelsize': label_fontsize,
    'xtick.labelsize': tick_fontsize,
    'ytick.labelsize': tick_fontsize,
    'legend.fontsize': legend_fontsize,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial'] # 一种普遍接受的无衬线字体
})


# --- 创建图表与坐标轴 ---

# 以指定尺寸和高DPI创建图表，以获得良好的分辨率
fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in), dpi=300)

# --- 生成示例数据 ---

x = np.linspace(0, 10, 100)
y1 = np.sin(x)
y2 = np.cos(x)

# --- 绘制数据 ---

# 使用清晰的线条样式、颜色和标记来区分数据系列。
# 线条宽度（lw）应足够粗以确保清晰。
ax.plot(x, y1, label='sin(x)', lw=1.5, marker='o', markersize=3, markevery=10)
ax.plot(x, y2, label='cos(x)', lw=1.5, marker='s', markersize=3, markevery=10)

# --- 设置标签、标题和刻度 ---

ax.set_title('Example Publication-Quality Plot')
ax.set_xlabel('X-axis Label (units)')
ax.set_ylabel('Y-axis Label (units)')

# --- 添加图例 ---

# 添加图例以识别绘制的线条
ax.legend()

# --- 调整布局并保存图表 ---

# 调整布局以防止标签被截断
fig.tight_layout()

# 以矢量格式（PDF）和位图格式（PNG）保存图表。
# DPI设置确保了PNG的高分辨率。
plt.savefig('publication_quality_figure.pdf', bbox_inches='tight')
plt.savefig('publication_quality_figure.png', bbox_inches='tight', dpi=300)

print("已生成 publication_quality_figure.png 和 publication_quality_figure.pdf")