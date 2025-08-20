
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    'font.size': 8,
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica'],
    'axes.titlesize': 12,
    'axes.labelsize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8
})
plt.rcParams['font.sans-serif'].insert(0, 'SimHei')
plt.rcParams['axes.unicode_minus'] = False

x = np.linspace(0, 2 * np.pi, 400)
y1 = np.sin(x)
y2 = np.cos(x)
y3 = np.tan(x)
y4 = np.sinc(x)

fig, axs = plt.subplots(2, 2, figsize=(7.08, 4.0))
axs = axs.flatten()

axs[0].plot(x, y1, 'r-')
axs[0].set_title("正弦波")
axs[0].set_xlabel("角度 [弧度]")
axs[0].set_ylabel("值")
axs[0].grid(True)

axs[1].plot(x, y2, 'g-')
axs[1].set_title("余弦波")
axs[1].set_xlabel("角度 [弧度]")
axs[1].set_ylabel("值")
axs[1].grid(True)

axs[2].plot(x, y3, 'b-')
axs[2].set_title("正切波")
axs[2].set_ylim(-5, 5)
axs[2].set_xlabel("角度 [弧度]")
axs[2].set_ylabel("值")
axs[2].grid(True)

axs[3].plot(x, y4, 'k-')
axs[3].set_title("Sinc函数")
axs[3].set_xlabel("角度 [弧度]")
axs[3].set_ylabel("值")
axs[3].grid(True)

plt.tight_layout()
plt.savefig('001_figure.svg', bbox_inches='tight')
plt.show()