import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 中文
plt.rcParams['axes.unicode_minus'] = False  # 负号
from IPython.core.pylabtools import figsize  # import figsize

# figsize(12.5, 4) # 设置 figsize
plt.rcParams['savefig.dpi'] = 300  # 图片像素
plt.rcParams['figure.dpi'] = 300
plt.figure()


def min2hour(datalist):
    return [round(data / 60, 2) for data in datalist]


turning_point = [[[0, 421, 1150, 1440], [0, 421, 1150, 1440]],
                 [[0, 421, 1150, 1440], [0, 421, 1150, 1440]]]

turning_time = [[[40, 40, 45, 40], [40, 40, 45, 40]],
                [[45, 45, 45, 45], [45, 45, 45, 45]]]

plt.step(min2hour(turning_point[0][1]), turning_time[0][1], label='设置的running time')
plt.step(min2hour(turning_point[1][1]), turning_time[1][1], label='实际时刻表')
plt.ylabel('行程时间')
plt.legend()
plt.show()
