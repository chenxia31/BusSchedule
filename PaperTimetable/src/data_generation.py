# 2023-06-08 运行成功，保存数据集
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import copy
import sys
sys.path.append('../')
sys.path.append('../../')
sys.path.append('')
from utils.originalTimetableParsing import *
from utils.timetableVisual import *
import os
import pickle
import copy

def workmodeTimeFromTimetableChain(timetableChain,runningPoint,runningTime):
    ''' 
    获取司机两头班的开始时间和结束时间

    input:
    timetableChain: 原始时刻表解析的dataframe格式,填充-1下班 -2上班 -3两头班
    runningPoint: 获取周转时间的时间点
    runningTime: 获取周转时间的具体时间

    return:
    workmodeList: 工作模式的清单
    '''
    workmodeList=[]
    for i in range(1,len(timetableChain)):
        workmode=[]
        flag=1
        for j in range(len(timetableChain.iloc[i,:])):
            # 对于每一行
            if timetableChain.iloc[i,j]==-3 and flag==1:
                workmode.append(datetime2int(timetableChain.iloc[i,j-1])+get_moment_direction(runningPoint,runningTime,datetime2int(timetableChain.iloc[i,j-1]),1))
                flag=0
            if timetableChain.iloc[i,j]!=-3 and flag==0:
                workmode.append(datetime2int(timetableChain.iloc[i,j]))
                flag=1
        if workmode:
            workmodeList.append(copy.deepcopy(workmode))
    return workmodeList

def rawTimetableParsingPath(path):
    ''' 用于对原始的嘉定公交行车计划进行结构化的解析,通常利用sheet=3来进行操作。此处的代码使用的是后端的view的方式,返回上行时刻表和下行时刻表
    input:
    path 原始时刻表的路径

    output:
    df_weekday: 原始时刻表工作日的df
    df_weekend: 原始时刻表休息日的df
    '''
    choiceSheet=2
    # utils.originalTimetableParsing.chooseIndexFromOrigin  从原始时刻表中选择可以解析的区域
    rawdfTimetable=pd.read_excel(path,sheet_name=choiceSheet)
    # utils.originalTimetableParsing.splitTimetale 从解析区域中选择 weekend和weekday之间的区域
    df1=chooseIndexFromOrigin(rawdfTimetable) 
    df_weekday,df_weekend=splitTimetable(df1)
    return df_weekday,df_weekend

def HRMDfromTimetable(timetableDF):
    ''' 
    从结构的timetable数据文件夹中进行分析,返回 车次链、发车间隔节点、发车间隔时间、周转时间间隔、周转时间节点
    就餐时长、就餐次数统计、工作模式、工作模式计数

    input:
    timetableDF:解析之后的pandas.dataframe格式的timetableDF

    output:
    res.timetableChain
    res.headwayPoint
    res.headwayTime
    res.runningPoint
    res.runningTime
    res.mealInterval
    res.mealCount
    res.workmodelInterval
    res.workmodeCount
    '''
    # 返回新的timetable 和runningTimeArray 的解析
    timetableChain,runningTimeArray=reshapeTimeTable(df_weekday)
    # 由此得到departure time
    timetableArray,departureTime,headway=formatTimetaleArray(timetableChain,runningTimeArray)

    # 由此得到running和headway
    runningPoint,runningTime=formatTurnningTime(departureTime)
    headwayPoint,headwayTime=departureTime2Headway(departureTime)

    # meal time
    mealTimeList=[]
    for driver in timetableArray:
        meal_time=[]
        for i in range(len(driver)-1):
            if driver[i+1][0]-driver[i][0] > 30+get_moment_direction(runningPoint,runningTime,driver[i][0],driver[i][1]):
                # 选用前面的时间点
                meal_time.append(driver[i][0]+get_moment_direction(runningPoint,runningTime,driver[i][0],driver[i][1])+10)
                meal_time.append(meal_time[-1]+25)
                break
        mealTimeList.append(copy.deepcopy(meal_time))
    mealInterval,mealCount=countListTime(mealTimeList=mealTimeList)

    timetableChain=timetableChainFill(timetableChain)
    workmodeList=workmodeTimeFromTimetableChain(timetableChain,runningPoint,runningTime)
    workmodeInterval,workmodeCount=countListTime(mealTimeList=workmodeList)

    featureList = []
    for driver in timetableArray:
        for bus in driver:
            curr = copy.deepcopy(bus)

            # 添加班次的周转时间
            curr.append(get_moment_direction(runningPoint, runningTime, curr[0],curr[1]))

            #TODO 后续在添加虚拟班次
            # -1 下班、-2上班、-3两头班、0表示正常班次
            featureList.append(curr)

    columns = ['depature time','direction','index','running time']
    seqTimetable = pd.DataFrame(featureList,columns=columns)
    print(seqTimetable.shape)
    res={
        'timetableChain':timetableChain,
        'headwayPoint':headwayPoint,
        'headwayTime':headwayTime,
        'runningPoint':runningPoint,
        'runningTime':runningTime,
        'mealInterval':mealInterval,
        'mealCount':mealCount,
        'workmodeInterval':workmodeInterval,
        'workmodeCount':workmodeCount,
        'seqTimetable':seqTimetable
    }
    return res

# 测试使用
# path='data/DrivingPlanJDBUS/嘉定1路 行车时刻表2021.4.xls'
# df_weekday,df_weekend=rawTimetableParsingPath(path=path)
# HRMDfromTimetable(df_weekday)


pathFolder='data/schedule/'
filePaths=os.walk(pathFolder)
dataset={}
print('解析成功时刻表列表')
for path,dirs,files in filePaths:
    for file in files:
        fullname=os.path.join(path,file)
        try:
            newFilename=file.split(' ')
            df_weekday,df_weekend=rawTimetableParsingPath(fullname)
            dataset[newFilename[0]+'weekday']=HRMDfromTimetable(df_weekday)
            dataset[newFilename[0]+'weekend']=HRMDfromTimetable(df_weekend)
            print(fullname)
        except:
            pass

fw=open('data/generated_timetables/timetableDataset.pkl','wb')
pickle.dump(dataset,fw)



