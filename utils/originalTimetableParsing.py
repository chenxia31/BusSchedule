# 完整的时刻表的修改
import numpy as np
import pandas as pd
import pandas
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
        raise ('Step time error!')

def sheetChoose(sheetDf):
    '''
    sheetDF: 原始的时刻表文件
    return: 可解析的时刻表的sheet

    选择可以解析的时刻表的sheet
    '''
    sizes = []
    for sheet in sheetDf:
        sizes.append(sheetDf[sheet].size)
    # return sizes.index(max(sizes))
    return 2

def chooseIndexFromOrigin(df: pandas.DataFrame) -> pandas.DataFrame:
    '''
    从行车计划读取的脏乱差的时刻表中拆分
    df: 可解析的时刻表的sheet
    return: 可解析的时刻表的sheet中的路牌的行
    仅保留具有路牌号的行
    '''
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)
    return df[df.iloc[:, 0].str.contains('\d+|路牌', na=False)]


def splitTimetable(df_index: pandas.DataFrame):
    '''
    df_index: 可解析的时刻表的sheet中的路牌的行
    return: df_weekday, df_weekend

    将时刻表分为工作日和周末两个部分
    '''
    logic = df_index.iloc[:, 0].str.contains('实施', na=False)
    logic = logic.astype(int)
    logic = logic.cumsum()
    df_weekday = df_index[logic == 1]
    df_weekday = df_weekday[df_weekday.iloc[:, 0].str.contains('^\d+|^路牌', na=False)]

    if max(logic) >= 2:
        df_weekend = df_index[logic == 2]
        df_weekend = df_weekend[df_weekend.iloc[:, 0].str.contains('^\d+|^路牌', na=False)]
    else:
        df_weekend = df_weekday
    return df_weekday, df_weekend


def reshapeTimeTable(df):
    '''
    df: 可解析的时刻表的sheet中的路牌的行
    return: df_target2, df_time

    将时刻表转化为[[[start_time,pattern,index]],[]]的形式
    '''
    logic = df.iloc[:, 0].str.contains('路牌', na=False)
    logic = logic.astype(int)
    logic = logic.cumsum()
    df_target = pd.DataFrame()
    for i in range(max(logic)):
        df_temp = df[logic == (i + 1)]
        df_temp.index = df_temp.iloc[:, 0]
        df_temp = df_temp.drop(df_temp.columns[0], axis=1)
        df_target = pd.concat([df_target, df_temp], axis=1)

    str_count = df_target.iloc[0, :].value_counts()
    if str_count[0] > (str_count[1] + 5):
        str_count = str_count.drop(index=[str_count.index[0]])
    station1 = str_count.index[0]
    station2 = str_count.index[1]
    # 需要排除可能在行程时间上面加文字
    logic = df_target.iloc[0, :].str.contains(station1 + '|' + station2, na=False)
    df_target1 = df_target.T[logic].T
    logic2 = logic.to_frame().apply(np.roll, shift=1)
    df_time = df_target.T[logic2.iloc[:, 0]].T
    df_time.columns = df_target1.columns
    # 只有有时间的才不会被消灭
    for i in range(df_time.shape[0]):
        for j in range(df_time.shape[1]):
            if type(df_time.iloc[i, j]) == type('str'):
                df_time.iloc[i, j] = np.nan
    df_target2 = df_target1[df_time.notnull()]
    df_target2.iloc[0, :] = df_target1.iloc[0, :]
    df_time.iloc[0, :] = df_target1.iloc[0, :]
    return df_target2, df_time


def formatTimetaleArray(df_bus, df_time):
    '''
    输入规整之后的时刻表dataframe格式，来将其转化为之前的[[[start_time,pattern,index]],[]]的形式
    start_time是对应值、pattern是station1还是station2的问题、index是路牌编号的问题
    '''
    stationUpstream = df_bus.iloc[0, 0]
    stationDownstream = df_bus.iloc[0, 1]
    timetable_array = []
    travel_times = []
    start_hour = []
    for row in range(1, df_bus.shape[0]):
        logic = df_bus.iloc[row, :].notnull()
        bus_index = []

        for col in range(0, df_bus.shape[1]):
            if logic[col]:
                bus = []
                travel_time = []
                # 之前的判别是根据后面有数字来表示这辆车是可以运行的
                # 但是7路和102路中出现新的问题包括这里的可能会存在奇奇怪怪的数字
                try:
                    df_bus.iloc[row,col] = pd.to_datetime(df_bus.iloc[row,col])
                except:
                    pass
                if df_bus.iloc[row, col].hour == 0:
                    bus.append(
                        df_bus.iloc[row, col].hour * 60 + df_bus.iloc[row, col].minute + 24 * 60)  # start at 6:00
                else:
                    bus.append(df_bus.iloc[row, col].hour * 60 + df_bus.iloc[row, col].minute)  # start at 6:00
                if df_bus.iloc[0, col] == stationUpstream:
                    pattern = 0
                else:
                    pattern = 1
                bus.append(pattern)
                bus.append(row)
                travel_time.append(df_bus.iloc[row, col].hour * 60 + df_bus.iloc[row, col].minute)
                travel_time.append(int(df_time.iloc[row, col]))
                travel_time.append(pattern)
                bus_index.append(bus)
                travel_times.append(travel_time)  # still loop in nan ,so let it in if
                start_hour.append(df_bus.iloc[row, col].hour)

        timetable_array.append(bus_index)

    return timetable_array, travel_times, start_hour

def formatTurnningTime(travel_times):
    '''
    返回行程时间对应的转折点和对应的行程时间
    '''
    travel_times = np.array(travel_times)
    travel_times[:, 0] = travel_times[:, 0]
    turn = travel_times[travel_times[:, 0].argsort()]
    turn_point = []
    turn_time = []
    for j in range(2):
        turn_point_up = [0]
        turn_time_up = []
        turn_up = turn[turn[:, 2] == j, :]
        for i in range(turn_up.shape[0] - 1):  # attention for boundary
            if turn_up[i, 1] != turn_up[i + 1, 1]:
                turn_point_up.append(turn_up[i, 0])
                turn_time_up.append(turn_up[i, 1])
        # last change not be mentioned
        turn_time_up.append(turn_up[-1, 1])
        turn_point_up.append(2000)
        turn_point.append(turn_point_up)
        turn_time.append(turn_time_up)
    return turn_point, turn_time


def formatAxis(tt_array):
    '''
    生成对应的横轴（路牌数量），纵轴（路牌时间的分类）
    '''
    index_number = tt_array.__len__()
    start_hour = []
    for index in tt_array:
        for bus in index:
            start_hour.append(int(bus[0] / 60))

    start = min(start_hour)
    end = max(start_hour) + 1
    return index_number, [start, end]

def timetableChainFill(timetableChain):
    # -1 下班
    # -2 上班
    # -3 两头班
    for i in range(len(timetableChain)):
        for j in range(len(timetableChain.iloc[i,:])-1,-1,-1):
            if pd.isna(timetableChain.iloc[i,j]):
                timetableChain.iloc[i,j]=-1
            else:
                break
            
    for i in range(len(timetableChain)):
        for j in range(len(timetableChain.iloc[i,:])):
            if pd.isna(timetableChain.iloc[i,j]):
                timetableChain.iloc[i,j]=-2
            else:
                break

    for i in range(len(timetableChain)):
        for j in range(len(timetableChain.iloc[i,:])):
            if pd.isna(timetableChain.iloc[i,j]):
                timetableChain.iloc[i,j]=-3
    return timetableChain

def departureTime2Headway(departureTime):
    ''' 
    返回headway和headway time

    args:
    departureTime:每个班次的出发时间

    returns:
    return:headwayPoint和headwayTime
    '''
    depTimeDF=pd.DataFrame(departureTime)
    # upstream
    upDepTimeDF=depTimeDF[depTimeDF.iloc[:,2]==0]
    # downstream
    downDepTimeDF=depTimeDF[depTimeDF.iloc[:,2]==1]
    upHeaadwayPoint=list(upDepTimeDF.iloc[:,0].sort_values())
    upHeaadwayTime=[upHeaadwayPoint[i+1] - upHeaadwayPoint[i] for i in range(len(upHeaadwayPoint)-1)]
    downHeadwayPoint=list(downDepTimeDF.iloc[:,0].sort_values())
    downHeadwayTime=[downHeadwayPoint[i+1] - downHeadwayPoint[i] for i in range(len(downHeadwayPoint)-1)]
    return [upHeaadwayPoint,downHeadwayPoint],[upHeaadwayTime,downHeadwayTime]

def countListTime(mealTimeList):
    ''' 
    统计司机的吃饭时间和对应的数量

    args:
    mealTimeList:吃饭时间[[i,o],[i,o],...]

    return:
    mealIntervals:分段的时间
    mealCount:分段的数量
    '''
    inputTime=[d[0] for d in mealTimeList]
    outputTime=[d[1] for d in mealTimeList]
    inputTime.sort()
    outputTime.sort()
    # 排序之后开始counting
    mealIntervals=[0]
    mealCount=[0]
    while inputTime and outputTime:
        if min(inputTime[0],outputTime[0]) ==  inputTime[0]:
            # 如果现在是增加
            mealIntervals.append(inputTime.pop(0))
            mealCount.append(mealCount[-1]+1)
        else:
            # 限制是离开
            mealIntervals.append(outputTime.pop(0))
            mealCount.append(mealCount[-1]-1)
    while(outputTime):
        mealIntervals.append(outputTime.pop(0))
        mealCount.append(mealCount[-1]-1)
    return mealIntervals,mealCount

def datetime2int(time):
    return time.hour*60+time.minute
