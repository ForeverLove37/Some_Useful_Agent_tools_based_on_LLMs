import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict

# --- 解决中文显示问题 ---
plt.rcParams['font.sans-serif'] = ['SimHei']  # 或者 'Microsoft YaHei', 'Heiti TC', 等
plt.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# --- 设置整体图表风格和字体大小 ---
plt.style.use('seaborn-v0_8-paper')  # 使用更专业的 seaborn 风格
plt.rcParams.update({
    'font.size': 12,          # 基础字体大小
    'axes.labelsize': 14,     # 坐标轴标签字体大小
    'axes.titlesize': 16,     # 子图标题字体大小
    'xtick.labelsize': 12,    # X轴刻度标签字体大小
    'ytick.labelsize': 12,    # Y轴刻度标签字体大小
    'legend.fontsize': 12,    # 图例字体大小
    'figure.titlesize': 20    # 整个图表的总标题字体大小
})

# ----------------------------------------------------------------------
# 1：数学规范 - 常量与定义
# ----------------------------------------------------------------------
X_MIN_NM = -2.0
X_MAX_NM = 2.0
Y_MIN_NM = -1.0
Y_MAX_NM = 1.0

D0_METERS = 110.0
ALPHA_DEG = 1.5
THETA_DEG = 120.0
NM_TO_M = 1852.0

# 预计算值
alpha_rad = np.radians(ALPHA_DEG)
theta_rad = np.radians(THETA_DEG)
tan_alpha = np.tan(alpha_rad)
tan_half_theta = np.tan(theta_rad / 2)

# 用于精确宽度计算的离散化网格
DELTA_X_NM = 0.005
X_GRID = np.arange(X_MIN_NM, X_MAX_NM + DELTA_X_NM, DELTA_X_NM)

# ----------------------------------------------------------------------
# 2：复用的测带宽度函数
# ----------------------------------------------------------------------
def get_swath_width(x_coordinate_nm: float) -> float:
    """
    Calculates the sonar swath width in nautical miles at a given
    East-West coordinate.
    """
    x_meters = x_coordinate_nm * NM_TO_M
    depth_meters = D0_METERS - x_meters * tan_alpha
    width_meters = 2 * depth_meters * tan_half_theta
    width_nm = width_meters / NM_TO_M
    return width_nm

# 预先计算网格上所有测带宽度以提高效率
W_GRID = np.array([get_swath_width(x) for x in X_GRID])

# ----------------------------------------------------------------------
# 3：重构的可视化与分析核心函数
# ----------------------------------------------------------------------
def plot_survey_swaths_and_centerlines(ax: plt.Axes, survey_lines: pd.DataFrame):
    """
    Plots the individual survey swaths and their centerlines onto the axes.
    """
    for _, line in survey_lines.iterrows():
        y = line['y_coordinate_nm']
        x_start = line['x_start_nm']
        x_end = line['x_end_nm']

        # 找到与此段对应的网格索引
        j_start = np.searchsorted(X_GRID, x_start)
        j_end = np.searchsorted(X_GRID, x_end)
        
        # 获取此特定段的x和宽度值
        x_segment = X_GRID[j_start:j_end+1]
        w_segment = W_GRID[j_start:j_end+1]

        # 定义覆盖测带（多边形）的顶点
        swath_bottom = y - w_segment / 2
        swath_top = y + w_segment / 2
        
        vertices = list(zip(x_segment, swath_bottom)) + list(zip(x_segment[::-1], swath_top[::-1]))
        
        # 绘制半透明测带多边形
        swath_patch = patches.Polygon(vertices, closed=True, facecolor='mediumaquamarine', alpha=0.3, edgecolor='none')
        ax.add_patch(swath_patch)
        
        # 绘制勘测中心线
        ax.plot([x_start, x_end], [y, y], color='steelblue', lw=1.5, linestyle='--')

def calculate_and_plot_coverage_boundary(ax: plt.Axes, survey_lines: pd.DataFrame):
    """
    Calculates and plots the final northern coverage boundary.
    This is the most critical diagnostic plot, as it will reveal any gaps.
    """
    # 从勘测区域的南部边界开始
    B_boundary = np.full_like(X_GRID, Y_MIN_NM)

    # 按顺序将每条勘测线的覆盖范围应用于边界
    for _, line in survey_lines.iterrows():
        y = line['y_coordinate_nm']
        x_start = line['x_start_nm']
        x_end = line['x_end_nm']

        j_start = np.searchsorted(X_GRID, x_start)
        j_end = np.searchsorted(X_GRID, x_end)

        # 新边界是此段测带的顶部
        new_boundary_segment = y + W_GRID[j_start:j_end+1] / 2
        
        # 更新整体边界，取每个点的最大y值
        B_boundary[j_start:j_end+1] = np.maximum(B_boundary[j_start:j_end+1], new_boundary_segment)

    # 绘制最终边界
    ax.plot(X_GRID, B_boundary, color='orangered', lw=3, label='最终覆盖边界', zorder=10)
    
    # 检查间隙（遗漏）并打印诊断信息
    min_final_coverage = np.min(B_boundary)
    if min_final_coverage < Y_MAX_NM:
        print(f"WARNING: 发现覆盖间隙！最小覆盖范围仅达到 {min_final_coverage:.4f} 海里 (目标为 {Y_MAX_NM:.4f} 海里)。")
    else:
        print(f"成功！实现完全覆盖。最小最终覆盖范围为 {min_final_coverage:.4f} 海里。")


def plot_single_survey_diagnostic(ax: plt.Axes, csv_filepath: str, plot_title: str):
    """
    Helper function to load a survey plan from a CSV and plot it on a given Matplotlib Axes.
    """
    try:
        survey_df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        ax.text(0.5, 0.5, f"文件未找到:\n'{csv_filepath}'\n请运行原始算法脚本(o3.py)生成计划。",
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
                color='red', fontsize=14, wrap=True)
        ax.set_title(plot_title)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_frame_on(False)
        print(f"Error: 文件 '{csv_filepath}' 未找到。请先运行主算法脚本 (o3.py) 生成勘测计划。")
        return

    # 1. 绘制勘测区域边界
    boundary_rect = patches.Rectangle((X_MIN_NM, Y_MIN_NM), X_MAX_NM - X_MIN_NM, Y_MAX_NM - Y_MIN_NM,
                                      linewidth=2, edgecolor='black', facecolor='none', label='勘测区域', zorder=5)
    ax.add_patch(boundary_rect)

    # 2. 绘制勘测测带和中心线
    plot_survey_swaths_and_centerlines(ax, survey_df)
    
    # 3. 计算并绘制关键的最终覆盖边界
    calculate_and_plot_coverage_boundary(ax, survey_df)

    # 4. 最终绘图样式设置
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim(X_MIN_NM - 0.1, X_MAX_NM + 0.1)
    ax.set_ylim(Y_MIN_NM - 0.1, Y_MAX_NM + 0.1)
    ax.set_xlabel("东西坐标（海里）")
    ax.set_ylabel("南北坐标（海里）")
    ax.set_title(plot_title)
    ax.grid(True, linestyle=':', alpha=0.7) # 更精细的网格线
    
    # 为图例创建代理艺术家
    swath_proxy = patches.Patch(color='mediumaquamarine', alpha=0.3, label='声呐测带覆盖')
    centerline_proxy = plt.Line2D([0], [0], color='steelblue', lw=1.5, linestyle='--', label='勘测中心线')
    
    handles, labels = ax.get_legend_handles_labels()
    handles.extend([swath_proxy, centerline_proxy])
    ax.legend(handles=handles, loc='upper right', frameon=True, fancybox=True, shadow=True, borderpad=0.8)

# ----------------------------------------------------------------------
# 4：主执行块 - 生成多子图
# ----------------------------------------------------------------------
if __name__ == '__main__':
    # 创建一个包含两个子图的图表 (1行2列)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9)) # 调整图表大小以适应两个并排子图

    # 设置整个图表的总标题
    fig.suptitle('勘测计划诊断可视化：原始算法与修正算法对比', fontsize=22, y=0.98) 

    print("="*80)
    print("正在运行勘测计划诊断：可视化分析覆盖性能")
    print("="*80)

    # --- 诊断1：可视化原始有缺陷代码的输出 ---
    print("\n--- 诊断结果：原始缺陷算法 ---")
    original_csv_file = "problem3_east_west_survey_plan_REVISED.csv"
    plot_single_survey_diagnostic(
        ax=ax1,
        csv_filepath=original_csv_file,
        plot_title="原始缺陷算法结果 (可能存在间隙)"
    )

    # --- 诊断2：可视化已更正代码的输出 ---
    print("\n--- 诊断结果：修正算法 ---")
    corrected_csv_file = "problem3_survey_plan_PARTITIONED.csv" 
    plot_single_survey_diagnostic(
        ax=ax2,
        csv_filepath=corrected_csv_file,
        plot_title="修正算法结果 (理想覆盖情况)"
    )
    
    # 调整子图布局以防止重叠，并为总标题留出空间
    plt.tight_layout(rect=[0, 0, 1, 0.98]) 
    plt.show()