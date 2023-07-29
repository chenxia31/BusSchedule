import sys
sys.path.append('/Users/chenxia/Program/timetable_Create_Web/JDBUS/timetabe_if_then/src/problem')
from problem.timetableDefine import Timetable
import matplotlib.pyplot as plt

class timetableVisualize:
    @staticmethod
    def view(timetable,title='timetable'):
        
        max_index = 0
        for index in timetable.to_timetable_array():
            for bus in index:
                c = ['b', 'r']
                plt.hlines(y=bus[2], xmin=bus[0], xmax=bus[0] + timetable.running_time.get_moment_direction(bus[0], bus[1]), colors=c[bus[1]])
                max_index = max(max_index, bus[2])
        plt.yticks(list(range(1, max_index + 1)))
        plt.title(title)
        plt.show()
    
    @staticmethod
    def timetable2excel(timetable,index=1):
        # 将之前定义的格式转换成为dataframe，然后转换成为Excel    
        def _num_to_time(num):
            hour = int(num / 60)
            minute = int(num % 60)
            return str(hour) + ':' + str(minute)
        import copy
        import pandas as pd
        import numpy as np
        filedir='./result_excel/result'+str(index)+'.xlsx'
        # 01--将之前的时刻表转换成为dataframe，写入sheet01中
        df_list=[]
        cnt=0
        col_template=['主站','时间','副站','时间']
        for TPG in timetable.groups:
            temp_st=[]
            temp_running_time=[]
            temp_st_up=[]
            temp_running_time_up=[]
            for TP in TPG.trip_pair_group:
                if TP.is_virtual==False:
                    temp_st.append(_num_to_time(TP.inbound_trip.start_time))
                    temp_running_time.append(timetable.running_time.get_moment_direction(TP.inbound_trip.start_time,TP.inbound_trip.direction))
                    temp_st_up.append(_num_to_time(TP.outbound_trip.start_time))
                    temp_running_time_up.append(timetable.running_time.get_moment_direction(TP.outbound_trip.start_time,TP.outbound_trip.direction))
                else:
                    temp_st.append(_num_to_time(0))
                    temp_running_time.append(-1)
                    temp_st_up.append(_num_to_time(0))
                    temp_running_time_up.append(-1)
            df_list.append(copy.deepcopy(temp_st))
            df_list.append(copy.deepcopy(temp_running_time))
            df_list.append(copy.deepcopy(temp_st_up))
            df_list.append(copy.deepcopy(temp_running_time_up))
            cnt+=1

        df_list=np.array(df_list)
        df1=pd.DataFrame(df_list)
        df1=df1.T
        df1.columns=col_template*cnt

        # df2分别计算上行的发车时间间隔和下行的发车时间间隔
        df2_list=timetable._headway_cal()
        df2=pd.DataFrame(df2_list)
        df2=df2.T
        df2.columns=['上行发车间隔','下行发车间隔']

        # df3分别计算一些评价指标
        df3_list=timetableEvaluation.evaluate(timetable)
        df3=pd.DataFrame(df3_list)
        df3.columns=['工作时间']
        import os
        try:
            os.remove(filedir)
        except:
            pass
        with pd.ExcelWriter(filedir) as writer:
            df1.to_excel(writer, sheet_name="sheet1", index=False)
            df2.to_excel(writer, sheet_name="sheet2", index=False)
            df3.to_excel(writer, sheet_name="sheet3", index=False)
        return df3_list

class timetableEvaluation:
    @staticmethod
    def evaluate(timetable,flag=1):
        """ 计算时刻表的评价指标

        Argus:
        timetable:时刻表类文件
        
        flag: 
        1: 工作时间
        2: 行休比例
        3. 时刻表类数据
        """
        # 参数初始定义
        timetable_array=timetable.to_timetable_array()
        DISTANCE_BUS = 20  # 车辆的运行距离
        TWO_CLASS_DIFF = 80  # 车辆的最大间隔距离

        rest_ratio = []  # 车辆的行休比例
        runway_time = []  # 车辆的运行时间，在路上的时间
        inwork_time = []  # 路牌在站内时间，还没有删除高峰版的休息时间
        runway = []  # 车辆的运行里程
        diff_time_up = []  # 车辆的上行间隔时间
        diff_time_down = []  # 车辆的下行间隔时间
        class_pattern = []  # 车辆作为两头班应该需要删除的时间

        circle_time = []  # 半周期时间
        half_circle_time = []  # 周期时间
        layover_time = []  # 休息时间

        # 00-基础-计算并删除中间的休息时间
        start_time_up = []
        start_time_down = []

        for index_bus in timetable_array:
            index_start_time = []
            for class_bus in index_bus:
                index_start_time.append(class_bus[0])

                if class_bus[1] == 0:
                    start_time_up.append(class_bus[0])
                else:
                    start_time_down.append(class_bus[0])

            delet_time = 0
            if len(index_start_time) > 1:
                for i in range(len(index_start_time) - 1):
                    if ((index_start_time[i + 1] - index_start_time[i]) - timetable.running_time.get_moment_direction(index_start_time[i],1)) > TWO_CLASS_DIFF:
                        delet_time = delet_time + ((index_start_time[i + 1] - index_start_time[i]) - timetable.running_time.get_moment_direction(index_start_time[i], 0))
            class_pattern.append(delet_time)

        start_time_up = sorted(start_time_up)
        start_time_down = sorted(start_time_down)

        # 01--计算三个对应的指标，包括行休比例、工作时间、车行公里数
        for index_bus in timetable_array:
            start_work = 1440
            end_work = 0
            runwaytime = 0  # 在车上的时间
            for class_bus in index_bus:
                runwaytime = runwaytime + timetable.running_time.get_moment_direction(class_bus[0],
                                                        class_bus[1])  # 计算工作时间。行程时间累加
                start_work = min(start_work, class_bus[0])
                end_work = max(end_work, class_bus[0] + timetable.running_time.get_moment_direction(class_bus[0],
                                                        class_bus[1]))  # 计算工作时间。行程时间累加
            runway_time.append(runwaytime)  # 仅仅包括行程时间，在车上面的时间
            inwork_time.append(end_work - start_work)  # 车辆在站内的时间，还没去掉两头班的两个小时
            # runway.append(len(index_bus) * DISTANCE_BUS)

        work_time = [inwork_time[i] - class_pattern[i] for i in range(len(class_pattern))]  # 站内时间 减去 两头班的时间存在的时间
        if flag==2:
            rest_ratio = [(work_time[i] - runway_time[i]) / runway_time[i] for i in range(len(work_time))]
        # 02--计算对应的上行间隔和下行间隔
        for index_bus in timetable_array:
            for class_bus in index_bus:
                if class_bus[1] == 0:
                    diff_time_up.append(class_bus[0])
                if class_bus[1] == 1:
                    diff_time_down.append(class_bus[0])
        diff_time_up.sort()
        diff_time_down.sort()
        diff_time_down = [diff_time_down[i + 1] - diff_time_down[i] for i in range(len(diff_time_down) - 1)]
        diff_time_up = [diff_time_up[i + 1] - diff_time_up[i] for i in range(len(diff_time_up) - 1)]

        # 03-- 计算对应的circle_time，half circle_time、layover time

        start_time_01 = []  # 针对half_circle_time
        start_time_02 = []  # 针对circle_time
        for bus_index in timetable_array:
            # 时刻表中的每个路牌，计算circle time，目前是保证没有deadhead的情况，但是调整的时候会出现问题
            for i in range(len(bus_index) - 1):
                # 针对某个路牌的每个班次
                start_time_01.append(bus_index[i][0])
                half_circle_time.append(bus_index[i + 1][0] - bus_index[i][0])
                layover_time.append(
                    bus_index[i + 1][0] - bus_index[i][0] - timetable.running_time.get_moment_direction(bus_index[i][0], bus_index[i][1]))
            for i in range(len(bus_index) - 2):
                # 针对每个路牌的每个班次
                start_time_02.append(bus_index[i][0])
                circle_time.append((bus_index[i + 2][0] - bus_index[i][0]))

        # 按照时间进行排序
        import numpy as np
        half_circle_time = np.array(half_circle_time)[np.array(start_time_01).argsort()].tolist()
        layover_time = np.array(layover_time)[np.array(start_time_01).argsort()].tolist()
        circle_time = np.array(circle_time)[np.array(start_time_02).argsort()].tolist()
        banci = [circle_time, half_circle_time, layover_time]
        diff = [[start_time_up, diff_time_up], [start_time_down, diff_time_down]]
        if flag==1:
            return work_time
        if flag==2:
            return rest_ratio
        else:
            return work_time,banci,diff