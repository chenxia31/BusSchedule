import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys
sys.path.append('../../')
from utils.originalTimetableParsing import *
from utils.timetableVisual import *
mm = 1/25.4
plt.rcParams['font.family']= "Times New Roman"
mpl.rcParams['xtick.labelsize'] = 10
mpl.rcParams['ytick.labelsize'] = 10
plt.rcParams['mathtext.fontset']='cm'
plt.style.use('tableau-colorblind10')

def get_moment_direction(point,time,moment,direction):
    """ 取阶梯形状的时间点

    Args:
    moment : 时间点
    direction : 方向，0代表上行、1代表下行

    Return:
    返回对应的时间点
    """
    try:
        for i in range(len(point[direction])):
            if moment<=point[direction][i]:
                return time[direction][i-1]
    except:
        print(i)
        raise ('Step time error!')
        
def timetableArrayView(timetableArray,turning_point,turning_time,title):
    '''
    timetableArray: [[[],[],[]],[[],[],[]]]
    对timetableArray进行可视化
    '''

    max_index = 0
    plt.plot([500,500],[0,0],color='b',label='up')
    plt.plot([500,500],[0,0],color='r',label='down')
    plt.legend()
    for index in timetableArray:
        for bus in index:
            c = ['b', 'r']
            plt.hlines(y=bus[2], xmin=bus[0], xmax=bus[0] +get_moment_direction(turning_point,turning_time,bus[0], bus[1]), colors=c[bus[1]])
            max_index = max(max_index, bus[2])
    plt.yticks(list(range(1, max_index + 1)))
    plt.ylabel('Index for every bus')
    plt.xlabel('Time')
    plt.title(title)
    plt.show()


# running time可视化
def runningTimeView(turning_point,turning_time,title):
    """
    turning_point:转折点
    turning_time:转折时间
    """
    import matplotlib.pyplot as plt
    plt.figure()
    # point 和time的修正
    for i in range(2):
        turning_point[i].insert(0,0)
        turning_time[i].insert(0,turning_time[i][0])
        turning_point[i].append(2000)
        turning_time[i].append(turning_time[i][-1])
        turning_time[i].append(turning_time[i][-1])
    print(turning_time)
    print(turning_point)
    for i in range(2):
        plt.step(turning_point[i],turning_time[i])
    plt.xlabel('time')
    plt.xlim(0,1440)
    plt.ylabel('time')
    plt.title(title)
    plt.show()