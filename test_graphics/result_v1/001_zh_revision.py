import matplotlib.pyplot as plt
import numpy as np

# --- 解决中文显示问题 ---
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# --------------------------

# --- 应用专业图表风格 ---
plt.style.use('seaborn-v0_8-paper')
# ------------------------

# 生成数据
x = np.linspace(0, 2 * np.pi, 400)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)
y4 = np.sinc(x)

# 创建2x2子图布局
# 调整figsize以适应2x2布局，使其更宽且高度适中，保证视觉效果
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10)) # 调整图表尺寸

# 正弦函数子图 (axes[0, 0] - 左上角)
ax00 = axes[0, 0]
ax00.plot(x, y1, color='red', linewidth=2) # 调整颜色和线宽
ax00.set_title("正弦波", fontsize=16) # 增大标题字体
ax00.set_xlabel("角度 [弧度]", fontsize=12) # 增大标签字体
ax00.set_ylabel("值", fontsize=12)
ax00.grid(True, linestyle='--', alpha=0.7) # 调整网格线样式

# 余弦函数子图 (axes[0, 1] - 右上角)
ax01 = axes[0, 1]
ax01.plot(x, y2, color='green', linewidth=2)
ax01.set_title("余弦波", fontsize=16)
ax01.set_xlabel("角度 [弧度]", fontsize=12)
ax01.set_ylabel("值", fontsize=12)
ax01.grid(True, linestyle='--', alpha=0.7)

# 正切函数子图 (axes[1, 0] - 左下角)
ax10 = axes[1, 0]
ax10.plot(x, y3, color='blue', linewidth=2)
ax10.set_title("正切波", fontsize=16)
ax10.set_ylim(-5, 5) # 保留Y轴限制
ax10.set_xlabel("角度 [弧度]", fontsize=12)
ax10.set_ylabel("值", fontsize=12)
ax10.grid(True, linestyle='--', alpha=0.7)

# Sinc 函数子图 (axes[1, 1] - 右下角)
ax11 = axes[1, 1]
ax11.plot(x, y4, color='black', linewidth=2)
ax11.set_title("Sinc 函数", fontsize=16)
ax11.set_xlabel("角度 [弧度]", fontsize=12)
ax11.set_ylabel("值", fontsize=12)
ax11.grid(True, linestyle='--', alpha=0.7)

# 调整布局以避免重叠，并增加一些填充
plt.tight_layout(pad=3.0) # 增加pad参数，确保标题和标签不重叠

# 显示图
plt.show()