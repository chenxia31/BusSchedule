# Create your views here.
from django.http import HttpResponse
import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import json
from .models import RecordRequest
from .models import Estimate
from .models import Timetable
from .models import AdjustOption
from django.forms.models import model_to_dict

# 只有Linux上的python才包含这个包，非特殊不能使用
import os
from math import *
import matplotlib.pylab as plt
import pandas as pd
from pyomo.environ import *
import random
import numpy as np
from scipy.interpolate import BSpline
from scipy import interpolate
from IPython.core.pylabtools import figsize
from IPython.core.interactiveshell import InteractiveShell
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
import dill
import sys
import time
import pickle
from copy import deepcopy
import pprint

line_name = ['886_timetable.xlsx',
             'anhong_weekday.xlsx',
             'jiaTaiLine.xlsx',
             'jiaDing106.xlsx',
             'JDBUS_104_2018.xlsx',
             'JDBUS_104.xlsx',
             'JDBUS_104_0525_f.xlsx',
             'JDBUS117.xlsx',
             '117生成.xlsx']

# 规定坐标轴
# 规定行程时间
# 规定行程时间转折点
# 线路名称
time_axes = [5, 20]
index_axes = 12
filename = ''
period = 3
history_rest_ratio = []


def index(request):
    return render(request, 'index.html')


def TIMETABLE_INPUT(request):
    '''
    input：前端时刻表输入界面的数据
    out：返回时刻表界面，或者重新输入
    '''
    estimate_first = {'Num_RoadSigns': '0,1,2...', 'Capacity_Start': '0,1,2..', 'Capacity_Terminal': '0,1,2..',
                      'check_alert': ''}
    # with open("Record_Estimate_Pre.json", "w") as f:
    #     json.dump(estimate_pre, f, ensure_ascii=False)
    if request.method == 'POST':
        # 无论是初始界面，还是点击button都会出发get的请求，在这个请求下面进行一系列的操作
        Num_RoadSigns = request.POST.get('Num_RoadSigns')
        # 选取第一参数作为标志，如果路牌数量参数有的话，就说明输入参数没有缺失
        # 然后将前端输入参数记录下来
        if Num_RoadSigns != 0:
            request_record1 = RecordRequest(lineName=line_name[int(request.POST.get('line')) - 1],
                                            change_time=request.POST.get('Num_RoadSigns'),
                                            csrfmiddlewaretoken=request.POST.get('csrfmiddlewaretoken'),
                                            Num_RoadSigns=request.POST.get('Num_RoadSigns'),
                                            Pattern=request.POST.get('Pattern'),
                                            Capacity_Start=request.POST.get('Capacity_Start'),

                                            Headway=request.POST.get('Headway'),
                                            Running_time=request.POST.get('Running_time'),

                                            Capacity_Terminal=request.POST.get('Capacity_Terminal'),
                                            StartTime_Origin=request.POST.get('StartTime_Origin'),
                                            EndTime_Origin=request.POST.get('EndTime_Origin'),
                                            StartTime_Termnial=request.POST.get('StartTime_Termnial'),
                                            EndTime_Terminal=request.POST.get('EndTime_Terminal'),
                                            StartTime_Origin_Passenger=request.POST.get('StartTime_Origin_Passenger'),
                                            EndTime_Origin_Passenger=request.POST.get('EndTime_Origin_Passenger'),

                                            # StartTime_Origin_GPS=request.POST.get('StartTime_Origin_GPS'),
                                            # EndTime_Origin_GPS=request.POST.get('EndTime_Origin_GPS'),

                                            line=request.POST.get('line'), )

            request_record1.save()
            # 之前用来记录的json文件，现在可以不用了
            # with open("Record_Request.json", "w") as f:
            #     json.dump(request.POST, f, ensure_ascii=False)
            # 表示输入参数完整，没有缺失值
            if len(input_data_check()) < 2:
                # 表示输入参数是否逻辑正确，可以生成时刻表
                # with open("Record_Request.json", 'r') as load_f:
                #     record_request = json.load(load_f)
                # estimate = {**estimate_pre, **record_request} # 返回timetable的网页
                return redirect('timetable_gen')
        estimate_first['check_alert'] = input_data_check()

        return render(request, 'timetable_input.html', estimate_first)
    return render(request, 'timetable_input.html')


def TIMETABLE_FILE(request):
    if request.method == 'POST':
        file_obj = request.FILES.get("filename")
        global filename
        global period

        period = int(request.POST['Period'])
        filename = file_obj.name
        request_record1 = RecordRequest(lineName=filename)
        request_record1.save()
        with open(file_obj.name, "wb") as f:
            for chunk in file_obj.chunks():
                f.write(chunk)
        return render(request, 'timetable_file.html', {'information': '上传成功'})
    return render(request, 'timetable_file.html')


def TIMETABLE_GEN(request):
    '''
    这里是展示时刻表生成的界面，但是没有时刻表生成的东西
    '''
    temp = {'1': '起点有车，终点没有车', '2': '起点没有车，终点有车', '3': '起点和终点都有车'}
    estimate_pre = {'limitation': '时刻表暂未生成',
                    'rest_ratio': '司机的行休比例数据展示',
                    'work_time': '司机的工作时长数据展示',
                    'runway': '各路牌的运行里程数据展示',
                    'warning': '时刻表暂未生成',
                    }
    target = RecordRequest.objects.order_by('-change_time')[0]
    record_request = model_to_dict(target)

    estimate = {**estimate_pre, **record_request}
    # 返回timetable的网页
    return render(request, 'timetable_gen.html', estimate)


def TIMETABLE_ADJUST(request):
    return render(request, 'base.html')


def TIMETABLE_ESTIMATE(request):
    with open("Record_Estimate.json", 'r') as load_f:
        record_estimate = json.load(load_f)
        if record_estimate:
            return render(request, 'timetable_estimate.html', record_estimate)
        else:
            return render(request, '404.html')


def create_timetable_ajax(data):
    # 传递的时刻表数据中需要包括：
    # timetable：按照路牌和班次行程的包括【start——time。pattern，index，class】的数据
    # estimate：约束问题和五个指标的计算（后续可以考虑转移到前端来进行计算）
    # index_axes：用来表征计算路牌数量
    # time_axes：用来表征时间轴的长短
    # turning_time和turning_point：行程时间和行程时间的转折点
    # 这个仅仅作为ajax完成的例子，来实现相关数据的变换
    # 通过timetable_gen函数生成时刻表的数组数据
    # 通过timetable_estimate函数生成时刻表的相关评价，包括limitation和estimate的数据
    global time_axes
    global index_axes
    global period
    global history_rest_ratio
    history_rest_ratio = []
    # 新建的时候，历史的行休比例都是

    # 时刻表生成函数
    timetable_array, turning_point, turning_time, index_axes, time_axes = timetable_gen(int(data.POST['tape']))

    # 时刻表评价指标函数
    estimate = timetable_estimate(timetable_array, turning_time, turning_point)

    # 保存时刻表的数据和时刻表的评价指标，保存在timetable-timetable
    new_timetable = Timetable()
    timetable_return = new_timetable.newTimetable(timetable_array, estimate, index_axes, time_axes, turning_point,
                                                  turning_time, 1, period)

    return HttpResponse(timetable_return)


def Optimate_min_fleetsize_timetable(data):
    """针对原始的时刻表，来根据优化目标，生成新的时刻表

    需要读取的数据
    timetable_array：列表中为每个路牌，每个路牌包括运行的[时间，模式，路牌序号]，eg[1015,1,1]
    turnning_point:换乘时间节点
    turnning_time:各时间段的行程时间
    """

    def read_data():
        '''
        读取原始时刻表的参数，来源于104路时刻表.xlsx的文件，并输出对应的参数提供给createParameter()文件夹
        网站中：从timetable-array中得到相关发车时间

        output:
        time_u ：上行站点的时间，包含所有的上行班次的【出发时间，到达时间】
        time_d: 下行站点的时间，包含所有的下行班次的{出发时间，到达时间}
        // 这里的到达时间是根据行程时间和理论休息时间来重新计算的
        T_u：上行班次的到达时间晚于下行班次的发车时间，那么就为0
        T_d: 下行班次的到达时间晚于上行班次的发车时间，那么就为0
        // 这两个是用来缩小定义可行域
        '''
        upstreamStartTime = []
        downstreamStartTime = []
        time_u = [[0, 0]]
        time_d = [[0, 0]]

        for bus_index in timetable_array:
            for banci in bus_index:
                if banci[1] == 0:
                    # banci的第二个代表上下行模式
                    upstreamStartTime.append(banci[0])
                else:
                    downstreamStartTime.append(banci[0])
        upstreamStartTime.sort()
        downstreamStartTime.sort()

        # 由此生成班次的出发时间和到达时间对【出发时间，到达时间】
        for upstreamStartTimeSingle in upstreamStartTime:
            tempUpStream = []
            tempUpStream.append(upstreamStartTimeSingle)
            tempUpStream.append(tempUpStream[0] + work_time_gen(turning_time, turning_point, tempUpStream[0], 0))
            time_u.append(tempUpStream)

        # 由此生成班次的出发时间和到达时间对【出发时间，到达时间】
        for downstreamStartTimeSingle in downstreamStartTime:
            tempDownStream = []
            tempDownStream.append(downstreamStartTimeSingle)
            tempDownStream.append(tempDownStream[0] + work_time_gen(turning_time, turning_point, tempDownStream[0], 1))
            time_d.append(tempDownStream)

        # 这里的约束条件是关于班次对的约束
        T_u = []
        theta_u = []
        for i in range(len(time_u)):
            # T_u.append([0,i])
            T_u.append([i, 999])
            # theta_u.append(0)

        for i, num in enumerate(time_u):
            # 上行发车时间，上行到达时间
            for j, num_j in enumerate(time_d):
                # 下行发车时间，下行到达时间
                if i == 0:
                    T_u.append([i, j])
                    # 设置主站和副站的时间
                elif num_j[0] >= num[1] + 5 and num_j[0] <= num[1] + 120:
                    # 如果下行发车时间 大于 上行到达时间的 +5 ，保证有休息时间
                    if num_j[0] - num[1] >= 120:
                        # 如果 下行发车时间 大于 上行到达时间的 =120，这个theta待定，可能是为了删掉两头班
                        T_u.append([i, j])
                        if i != 0 and j != 999:
                            theta_u.append(1)
                    else:
                        # 其余的正常班次的时间
                        T_u.append([i, j])
                        if i != 0 and j != 999:
                            theta_u.append(0)
        T_d = []
        theta_d = []
        for i in range(len(time_d)):
            # T_d.append([0,i])
            T_d.append([i, 999])
            # theta_d.append(0)
        for i, num in enumerate(time_d):
            for j, num_j in enumerate(time_u):
                if i == 0:
                    T_d.append([i, j])
                elif num_j[0] >= num[1] + 5:
                    if num_j[0] - num[1] >= 120:
                        T_d.append([i, j])
                        if i != 0 and j != 999:
                            theta_d.append(1)
                    else:
                        T_d.append([i, j])
                        if i != 0 and j != 999:
                            theta_d.append(0)

        startTime = [upstreamStartTime, downstreamStartTime]
        return T_u, T_d, time_u, time_d, startTime, theta_u, theta_d

    def createParameters(fleet_size):
        '''
        method：
        创建模型中需要的参数

        input:
        fleet_size:车队规模

        output:
        parameters:列表，其中依次包含
        S:list,0代表上行站点，1代表下行站点
        D:list,表示的是司机编号
        T_u：from read_data()，上行班次，从次站发往主站
        T_d：from read_data()，下行班次，从主站发往次站
        time_u:from read_data()，上行班次的发车时间
        time_d:frome read_data()，下行班次的发车时间
        t_u: 上行班次序号
        t_d: 下行班次序号
        t_d_m: 允许的最小吃饭时间
        '''
        S = [0, 1]
        D = list(range(fleet_size))
        T_u, T_d, time_u, time_d, startTime, theta_u, theta_d = read_data()
        t_u = list(range(1, len(time_u)))
        t_d = list(range(1, len(time_d)))
        t_d_m = [i for i in t_d if time_d[i][1] <= 17.5 * 60]
        parameters = [S, D, T_u, T_d, time_u, time_d, t_u, t_d, t_d_m, theta_u, theta_d]
        return parameters, startTime

    def createModel(parameters, type):
        '''
        根据createParameters()输出的参数，来针对对应的约束条件建模，返回建立好的模型

        input:
        来自createParameters（）的参数
        type：选择的方法
        1 代表优化配车数
        2 代表优化配车数和工作时间

        output：
        pyomo建立但是还没有求解的model
        '''

        S = parameters[0]  # 车站
        D = parameters[1]  # 理论的司机数量
        T_u = parameters[2]  # 上行班次upstream terminal to downstream terminal 包括0-和-（999）指代下班
        time_u = parameters[4]  # 上行班次的[离开时间，和到达时间]depart time and arrival time of tasks from upstream terminal
        T_d = parameters[3]  # 下行班次 downstream terminal to upstream terminal
        time_d = parameters[5]  # 下行班次的离开时间和到达时间 depart time and arrival time of tasks from downstream terminal
        # T_mu=parameters[6]
        # T_md=parameters[7]
        R = [0, 1]  # 0代表上行、1代表下行  0:upstream terminal to downstream terminal;1:downstream terminal to upstream terminal
        t_u = parameters[6]  # 上行班次的序号
        t_d = parameters[7]  # 下行班次的序号
        t_d_m = parameters[8]  # 允许吃饭的班次
        theta_u = parameters[-2]
        theta_d = parameters[-1]
        rest_time_u = [5, 25]
        rest_time_d = [5, 25]
        N_max = 14
        N_min = 8
        mealwindow = [60 * 10, 60 * 14.5]  # 吃饭时间，在10：00到13：30之间
        theta_0 = 25  # 吃饭的松弛时间1
        theta_1 = 5  # 吃饭的松弛时间2
        M = 50000
        T_u_tmp = [i for i in T_u if i[0] != 0 and i[1] != 999]
        T_d_tmp = [i for i in T_d if i[0] != 0 and i[1] != 999]
        model = ConcreteModel()
        flag = 0

        init_type = 1  # 0不初始化、1初始化
        # variable alpha beta 没有初始化
        if init_type == 0:
            print('==========模型建立过程createModel()============')
            print('====模型变量中的alpha、beta和delta初始化为0==========')
            model.a_0 = Var(T_u, D, within=Binary, initialize=0)
            model.a_1 = Var(T_d, D, within=Binary, initialize=0)
        elif init_type == 1:
            print('==========模型建立过程createModel()============')
            print('====模型变量中的alpha、beta和delta初始化为原始时刻表==========')
            model.a_0 = Var(T_u, D, within=Binary, initialize=0)
            # 对alpha进行初始化

            for driver in range(len(D)):
                if driver < len(timetable_array):
                    # 对于单个时刻表，车辆不会出现发车时间相同的情况
                    # 当司机的下标小于
                    temp = timetable_array[driver]
                    temp_startime = []
                    for temp_banci in temp:
                        temp_startime.append(temp_banci[0])
                    # 得到司机的发车时间之后
                    for shift in T_u:
                        if shift[0] == 0 and shift[1] != 999:
                            # 早晨上班的情况
                            if time_d[shift[1]][0] == temp_startime[0]:
                                model.a_0[shift[0], shift[1], driver] = 1

                                flag += 1
                        elif shift[1] == 999 and shift[0] != 0:
                            # 晚上下班的情况
                            if time_u[shift[0]][0] == temp_startime[-1]:
                                model.a_0[shift[0], shift[1], driver] = 1
                                flag += 1
                        elif shift[0] != 0 and shift[1] != 999:
                            # 在路牌中
                            # 因为是所有都遍历，可能存在时间并不在的情况
                            try:
                                index_1 = temp_startime.index(time_u[shift[0]][0])
                                index_2 = temp_startime.index(time_d[shift[1]][0])
                                if index_2 - index_1 == 1:
                                    model.a_0[shift[0], shift[1], driver] = 1
                                    flag += 1
                            except:
                                # 如何时间不存在就删掉罗
                                pass
            model.a_1 = Var(T_d, D, within=Binary, initialize=0)
            for driver in range(len(D)):
                if driver < len(timetable_array):
                    # 对于单个时刻表，车辆不会出现发车时间相同的情况
                    # 当司机的下标小于
                    temp = timetable_array[driver]
                    temp_startime = []
                    for temp_banci in temp:
                        temp_startime.append(temp_banci[0])
                    # 得到司机的发车时间之后
                    for shift in T_d:
                        if shift[0] == 0 and shift[1] != 999:
                            # 早晨上班的情况
                            if time_u[shift[1]][0] == temp_startime[0]:
                                model.a_1[shift[0], shift[1], driver] = 1
                                flag += 1
                        elif shift[1] == 999 and shift[0] != 0:
                            # 晚上下班的情况
                            if time_d[shift[0]][0] == temp_startime[-1]:
                                model.a_1[shift[0], shift[1], driver] = 1
                                flag += 1
                        elif shift[0] != 0 and shift[1] != 999:
                            # 在路牌中
                            # 因为是所有都遍历，可能存在时间并不在的情况
                            try:
                                index_1 = temp_startime.index(time_d[shift[0]][0])
                                index_2 = temp_startime.index(time_u[shift[1]][0])
                                if index_2 - index_1 == 1:
                                    model.a_1[shift[0], shift[1], driver] = 1
                                    flag += 1
                            except:
                                # 如何时间不存在就删掉罗
                                pass

        print('=====模型建立：允许的type====')
        type_name = ['优化配车数', '优化配车数和均衡工作量（备选目标一）', '优化配车数和休息时间（备选目标二）', '固定均衡时间（备选目标一的延伸）', '优化配车数+均衡工作量+副站时间为软约束']
        print(type_name[type - 1])

        if type == 1:
            model.gamma = Var(t_d, D, within=Binary, initialize=0)
            model.delta = Var(D, within=Binary, initialize=0)

            def delta_def(model, d):
                # 上班约束
                M_tmp = [i for i in T_u if i[0] == 0]
                N_tmp = [i for i in T_d if i[0] == 0]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp) + sum(model.a_1[i[0], i[1], d] for i in N_tmp)
                return expr == model.delta[d]

            model.delta_def = Constraint(D, rule=delta_def)

            # flow balance
            def fb_down(model, td, d):
                # 针对下行的站点的发车班次
                M_tmp = [i for i in T_d if i[0] == td]
                N_tmp = [i for i in T_u if i[1] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_down = Constraint(t_d, D, rule=fb_down)

            def fb_up(model, tu, d):
                M_tmp = [i for i in T_d if i[1] == tu]
                N_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_up = Constraint(t_u, D, rule=fb_up)

            def task_down(model, td):
                # 班次对的约束
                M_tmp = [i for i in T_d if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_down = Constraint(t_d, rule=task_down)

            def task_up(model, tu):
                # 上行班次对的约束
                M_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_up = Constraint(t_u, rule=task_up)

            def have_meal(model, d):
                # 吃饭时间的约束
                expr = sum(model.gamma[i, d] for i in t_d_m)
                return expr == model.delta[d]

            model.have_meal = Constraint(D, rule=have_meal)

            def have_meal_(model, d):
                expr = sum(model.gamma[i, d] for i in t_d)
                return expr == model.delta[d]

            model.have_meal_ = Constraint(D, rule=have_meal_)

            def meal_trip(model, td, d):
                M_tmp = [i for i in T_d_tmp if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - model.gamma[td, d]
                return expr >= 0

            model.meal_trip = Constraint(t_d, D, rule=meal_trip)

            def meal_duration(model, td, tu, d):
                expr = (time_u[tu][0] - time_d[td][1] - theta_0) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_duration = Constraint(T_d_tmp, D, rule=meal_duration)

            def meal_not_late(model, td, tu, d):
                expr = (time_u[tu][0] - mealwindow[0] - theta_1) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_not_late = Constraint(T_d_tmp, D, rule=meal_not_late)
            model.cost = Objective(expr=sum(model.delta[d] for d in D))

        elif type == 2:
            '''
            根据createParameters()输出的参数，来针对对应的约束条件建模，返回建立好的模型

            input:
            来自createParameters（）的参数

            output：
            pyomo建立但是还没有求解的model
            '''
            model.gamma = Var(t_d, D, within=Binary, initialize=0)
            # for i in t_d:
            #     for j in D:
            #         model.gamma[i,j].fix(1)
            model.delta = Var(D, within=Binary, initialize=1)
            for i in D:
                model.delta[i] = 1
            model.Wk = Var(D, initialize=0)
            model.HU = Var([0], initialize=0)
            model.HL = Var([0], initialize=0)
            model.epsilon = Var([0], initialize=0)
            model.Hk = Var(D, initialize=0)

            # #select the first and last tasks for each driver
            # def first_task(model,d):
            #     M_tmp=[i for i in T_u if i[0]==0]
            #     N_tmp=[i for i in T_d if i[0]==0]
            #     expr=sum(model.a_0[i[0],i[1],d] for i in M_tmp)+sum(model.a_1[i[0],i[1],d] for i in N_tmp)
            #     return expr<=1

            # def last_task(model,d):
            #     M_tmp=[i for i in T_u if i[1]==999]
            #     N_tmp=[i for i in T_d if i[1]==999]
            #     expr=sum(model.a_0[i[0],i[1],d] for i in M_tmp)+sum(model.a_1[i[0],i[1],d] for i in N_tmp)
            #     return expr<=1
            # model.first_task=Constraint(D,rule=first_task)
            # model.last_task=Constraint(D,rule=last_task)

            def delta_def(model, d):
                M_tmp = [i for i in T_u if i[0] == 0]
                N_tmp = [i for i in T_d if i[0] == 0]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp) + sum(model.a_1[i[0], i[1], d] for i in N_tmp)
                return expr == model.delta[d]

            model.delta_def = Constraint(D, rule=delta_def)

            # flow balance
            def fb_down(model, td, d):  # 针对下行的站点的发车班次
                M_tmp = [i for i in T_d if i[0] == td]
                N_tmp = [i for i in T_u if i[1] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_down = Constraint(t_d, D, rule=fb_down)

            def fb_up(model, tu, d):
                M_tmp = [i for i in T_d if i[1] == tu]
                N_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_up = Constraint(t_u, D, rule=fb_up)

            # #every task is undertaken by a driver
            def task_down(model, td):
                M_tmp = [i for i in T_d if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_down = Constraint(t_d, rule=task_down)

            def task_up(model, tu):
                M_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_up = Constraint(t_u, rule=task_up)

            # Mealtime length constraints
            def have_meal(model, d):
                expr = sum(model.gamma[i, d] for i in t_d_m)
                return expr == model.delta[d]

            model.have_meal = Constraint(D, rule=have_meal)

            def have_meal_(model, d):
                expr = sum(model.gamma[i, d] for i in t_d)
                return expr == model.delta[d]

            model.have_meal_ = Constraint(D, rule=have_meal_)

            def meal_trip(model, td, d):
                M_tmp = [i for i in T_d_tmp if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - model.gamma[td, d]
                return expr >= 0

            model.meal_trip = Constraint(t_d, D, rule=meal_trip)

            def meal_duration(model, td, tu, d):
                expr = (time_u[tu][0] - time_d[td][1] - theta_0) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_duration = Constraint(T_d_tmp, D, rule=meal_duration)

            def meal_not_late(model, td, tu, d):
                expr = (time_u[tu][0] - mealwindow[0] - theta_1) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_not_late = Constraint(T_d_tmp, D, rule=meal_not_late)

            # 最晚班次下班时间-最早班次上班时间
            def wk_def(model, d):
                M_tmp = [i[1] for i in T_u if i[0] == 0 and i[1] != 999]
                N_tmp = [i[1] for i in T_d if i[0] == 0 and i[1] != 999]
                P_tmp = [i[0] for i in T_u if i[1] == 999 and i[0] != 0]
                Q_tmp = [i[0] for i in T_d if i[1] == 999 and i[0] != 0]
                expr = model.Wk[d] + sum(time_d[i][0] * model.a_0[0, i, d] for i in M_tmp) + sum(
                    time_u[i][0] * model.a_1[0, i, d] for i in N_tmp) \
                       - sum(time_u[i][1] * model.a_0[i, 999, d] for i in P_tmp) - sum(
                    time_d[i][1] * model.a_1[i, 999, d] for i in Q_tmp)
                return expr == 0

            model.wk_def = Constraint(D, rule=wk_def)

            # 两头班中间间隔时间
            def hk_def(model, d):
                M_tmp = 0
                N_tmp = 0
                t = 0
                for i in T_u_tmp:
                    M_tmp = M_tmp + (time_d[i[1]][0] - time_u[i[0]][1]) * model.a_0[i[0], i[1], d] * theta_u[t]
                    t = t + 1
                t = 0
                for i in T_d_tmp:
                    N_tmp = N_tmp + (time_u[i[1]][0] - time_d[i[0]][1]) * model.a_1[i[0], i[1], d] * theta_d[t]
                    t = t + 1
                expr = model.Hk[d] - M_tmp - N_tmp
                return expr == 0

            model.hk_def = Constraint(D, rule=hk_def)

            # 工作时间的相差间隔
            def epsilon_def(model, d1, d2):
                expr = (model.Wk[d1] - model.Hk[d1]) - (model.Wk[d2] - model.Hk[d2]) - model.epsilon[0]
                return expr <= 0

            model.epsilon_def = Constraint(D, D, rule=epsilon_def)

            # 工作时间不超过900分钟
            def max_load(model, d):
                expr = model.Wk[d] - model.Hk[d] - 840
                return expr <= 0

            model.max_load = Constraint(D, rule=max_load)

            # model.time_gap=sum((time_d[i[1]][0]-time_u[i[0]][1])*model.a_0[i[0],i[1],d] for i in T_u_tmp for d in D)+sum((time_u[i[1]][0]-time_d[i[0]][1])*model.a_1[i[0],i[1],d] for i in T_d_tmp for d in D)
            # model.cost = Objective(expr=sum(model.delta[d]+model.Lk[d]/150 for d in D))
            model.cost = Objective(expr=sum(model.delta[d] for d in D) + (model.epsilon[0]) / 1000)

        elif type == 3:
            '''
            根据createParameters()输出的参数，来针对对应的约束条件建模，返回建立好的模型

            input:
            来自createParameters（）的参数

            output：
            pyomo建立但是还没有求解的model
            '''

            model.gamma = Var(t_d, D, within=Binary, initialize=0)
            model.delta = Var(D, within=Binary, initialize=0)
            for i in D:
                model.delta[i] = 1
            model.Hk = Var(D, within=Binary, initialize=0)
            model.Lk = Var(D, initialize=0)
            model.Wk = Var(D, initialize=0)

            def delta_def(model, d):
                M_tmp = [i for i in T_u if i[0] == 0]
                N_tmp = [i for i in T_d if i[0] == 0]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp) + sum(model.a_1[i[0], i[1], d] for i in N_tmp)
                return expr == model.delta[d]

            model.delta_def = Constraint(D, rule=delta_def)

            # flow balance
            def fb_down(model, td, d):  # 针对下行的站点的发车班次
                M_tmp = [i for i in T_d if i[0] == td]
                N_tmp = [i for i in T_u if i[1] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_down = Constraint(t_d, D, rule=fb_down)

            def fb_up(model, tu, d):
                M_tmp = [i for i in T_d if i[1] == tu]
                N_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_up = Constraint(t_u, D, rule=fb_up)

            # #every task is undertaken by a driver
            def task_down(model, td):
                M_tmp = [i for i in T_d if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_down = Constraint(t_d, rule=task_down)

            def task_up(model, tu):
                M_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_up = Constraint(t_u, rule=task_up)

            # Mealtime length constraints
            def have_meal(model, d):
                expr = sum(model.gamma[i, d] for i in t_d_m)
                return expr == model.delta[d]

            model.have_meal = Constraint(D, rule=have_meal)

            def have_meal_(model, d):
                expr = sum(model.gamma[i, d] for i in t_d)
                return expr == model.delta[d]

            model.have_meal_ = Constraint(D, rule=have_meal_)

            def meal_trip(model, td, d):
                M_tmp = [i for i in T_d_tmp if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - model.gamma[td, d]
                return expr >= 0

            model.meal_trip = Constraint(t_d, D, rule=meal_trip)

            def meal_duration(model, td, tu, d):
                expr = (time_u[tu][0] - time_d[td][1] - theta_0) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_duration = Constraint(T_d_tmp, D, rule=meal_duration)

            def meal_not_late(model, td, tu, d):
                expr = (time_u[tu][0] - mealwindow[0] - theta_1) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_not_late = Constraint(T_d_tmp, D, rule=meal_not_late)

            def rest_time(model, d):
                M_tmp = 0
                N_tmp = 0
                for i in T_u_tmp:
                    M_tmp = M_tmp + (time_d[i[1]][0] - time_u[i[0]][1]) * model.a_0[i[0], i[1], d]
                for i in T_d_tmp:
                    N_tmp = N_tmp + (time_u[i[1]][0] - time_d[i[0]][1]) * model.a_1[i[0], i[1], d]

                expr = model.Lk[d] - M_tmp - N_tmp
                return expr == 0

            model.rest_time = Constraint(D, rule=rest_time)

            def wk_def(model, d):
                M_tmp = [i[1] for i in T_u if i[0] == 0 and i[1] != 999]
                N_tmp = [i[1] for i in T_d if i[0] == 0 and i[1] != 999]
                P_tmp = [i[0] for i in T_u if i[1] == 999 and i[0] != 0]
                Q_tmp = [i[0] for i in T_d if i[1] == 999 and i[0] != 0]
                expr = model.Wk[d] - sum(time_d[i][0] * model.a_0[0, i, d] for i in M_tmp) - sum(
                    time_u[i][0] * model.a_1[0, i, d] for i in N_tmp) \
                       + sum(time_u[i][1] * model.a_0[i, 999, d] for i in P_tmp) + sum(
                    time_d[i][1] * model.a_1[i, 999, d] for i in Q_tmp)
                # expr=model.Wk[d]-sum(time_d[i][0] for i in M_tmp)
                return expr == 0

            model.wk_def = Constraint(D, rule=wk_def)

            def hk_def(model, d):
                M_tmp = 0
                N_tmp = 0
                t = 0
                for i in T_u_tmp:
                    M_tmp = M_tmp + (time_d[i[1]][0] - time_u[i[0]][1]) * model.a_0[i[0], i[1], d] * theta_u[t]
                    t = t + 1
                t = 0
                for i in T_d_tmp:
                    N_tmp = N_tmp + (time_u[i[1]][0] - time_d[i[0]][1]) * model.a_1[i[0], i[1], d] * theta_d[t]
                    t = t + 1
                expr = model.Hk[d] - M_tmp - N_tmp
                return expr == 0

            model.hk_def = Constraint(D, rule=hk_def)

            def max_load(model, d):
                expr = model.Wk[d] - model.Hk[d]
                return expr <= 840

            model.max_load = Constraint(D, rule=max_load)

            model.cost = Objective(expr=sum(model.delta[d] + model.Lk[d] / 150 for d in D))

        elif type == 4:
            '''
            仅优化配车时间
            '''
            model.gamma = Var(t_d, D, within=Binary, initialize=0)
            # for i in t_d:
            #     for j in D:
            #         model.gamma[i,j].fix(1)
            model.delta = Var(D, within=Binary, initialize=1, bounds=(1, 1))
            for i in D:
                model.delta[i] = 1
            model.Wk = Var(D, initialize=0)
            model.HU = Var([0], initialize=0)
            model.HL = Var([0], initialize=0)
            model.epsilon = Var([0], initialize=0)
            model.Hk = Var(D, initialize=0)

            # #select the first and last tasks for each driver
            # def first_task(model,d):
            #     M_tmp=[i for i in T_u if i[0]==0]
            #     N_tmp=[i for i in T_d if i[0]==0]
            #     expr=sum(model.a_0[i[0],i[1],d] for i in M_tmp)+sum(model.a_1[i[0],i[1],d] for i in N_tmp)
            #     return expr<=1

            # def last_task(model,d):
            #     M_tmp=[i for i in T_u if i[1]==999]
            #     N_tmp=[i for i in T_d if i[1]==999]
            #     expr=sum(model.a_0[i[0],i[1],d] for i in M_tmp)+sum(model.a_1[i[0],i[1],d] for i in N_tmp)
            #     return expr<=1
            # model.first_task=Constraint(D,rule=first_task)
            # model.last_task=Constraint(D,rule=last_task)

            def delta_def(model, d):
                M_tmp = [i for i in T_u if i[0] == 0]
                N_tmp = [i for i in T_d if i[0] == 0]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp) + sum(model.a_1[i[0], i[1], d] for i in N_tmp)
                return expr == model.delta[d]

            model.delta_def = Constraint(D, rule=delta_def)

            # flow balance
            def fb_down(model, td, d):  # 针对下行的站点的发车班次
                M_tmp = [i for i in T_d if i[0] == td]
                N_tmp = [i for i in T_u if i[1] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_down = Constraint(t_d, D, rule=fb_down)

            def fb_up(model, tu, d):
                M_tmp = [i for i in T_d if i[1] == tu]
                N_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_up = Constraint(t_u, D, rule=fb_up)

            # #every task is undertaken by a driver
            def task_down(model, td):
                M_tmp = [i for i in T_d if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_down = Constraint(t_d, rule=task_down)

            def task_up(model, tu):
                M_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_up = Constraint(t_u, rule=task_up)

            # Mealtime length constraints
            def have_meal(model, d):
                expr = sum(model.gamma[i, d] for i in t_d_m)
                return expr == model.delta[d]

            model.have_meal = Constraint(D, rule=have_meal)

            def have_meal_(model, d):
                expr = sum(model.gamma[i, d] for i in t_d)
                return expr == model.delta[d]

            model.have_meal_ = Constraint(D, rule=have_meal_)

            def meal_trip(model, td, d):
                M_tmp = [i for i in T_d_tmp if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - model.gamma[td, d]
                return expr >= 0

            model.meal_trip = Constraint(t_d, D, rule=meal_trip)

            def meal_duration(model, td, tu, d):
                expr = (time_u[tu][0] - time_d[td][1] - theta_0) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_duration = Constraint(T_d_tmp, D, rule=meal_duration)

            def meal_not_late(model, td, tu, d):
                expr = (time_u[tu][0] - mealwindow[0] - theta_1) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_not_late = Constraint(T_d_tmp, D, rule=meal_not_late)

            # 最晚班次下班时间-最早班次上班时间
            def wk_def(model, d):
                M_tmp = [i[1] for i in T_u if i[0] == 0 and i[1] != 999]
                N_tmp = [i[1] for i in T_d if i[0] == 0 and i[1] != 999]
                P_tmp = [i[0] for i in T_u if i[1] == 999 and i[0] != 0]
                Q_tmp = [i[0] for i in T_d if i[1] == 999 and i[0] != 0]
                expr = model.Wk[d] + sum(time_d[i][0] * model.a_0[0, i, d] for i in M_tmp) + sum(
                    time_u[i][0] * model.a_1[0, i, d] for i in N_tmp) \
                       - sum(time_u[i][1] * model.a_0[i, 999, d] for i in P_tmp) - sum(
                    time_d[i][1] * model.a_1[i, 999, d] for i in Q_tmp)
                return expr == 0

            model.wk_def = Constraint(D, rule=wk_def)

            # 两头班中间间隔时间
            def hk_def(model, d):
                M_tmp = 0
                N_tmp = 0
                t = 0
                for i in T_u_tmp:
                    M_tmp = M_tmp + (time_d[i[1]][0] - time_u[i[0]][1]) * model.a_0[i[0], i[1], d] * theta_u[t]
                    t = t + 1
                t = 0
                for i in T_d_tmp:
                    N_tmp = N_tmp + (time_u[i[1]][0] - time_d[i[0]][1]) * model.a_1[i[0], i[1], d] * theta_d[t]
                    t = t + 1
                expr = model.Hk[d] - M_tmp - N_tmp
                return expr == 0

            model.hk_def = Constraint(D, rule=hk_def)

            # 工作时间的相差间隔
            def epsilon_def(model, d1, d2):
                expr = (model.Wk[d1] - model.Hk[d1]) - (model.Wk[d2] - model.Hk[d2]) - model.epsilon[0]
                return expr <= 0

            model.epsilon_def = Constraint(D, D, rule=epsilon_def)

            # 限制只使用13辆车
            def res_vehicle(model):
                expr = sum(model.delta[d] for d in D)
                return expr == len(D)

            model.res_vehicle = Constraint(rule=res_vehicle)

            # 工作时间不超过900分钟
            def max_load(model, d):
                expr = model.Wk[d] - model.Hk[d] - 840
                return expr <= 0

            model.max_load = Constraint(D, rule=max_load)

            # model.time_gap=sum((time_d[i[1]][0]-time_u[i[0]][1])*model.a_0[i[0],i[1],d] for i in T_u_tmp for d in D)+sum((time_u[i[1]][0]-time_d[i[0]][1])*model.a_1[i[0],i[1],d] for i in T_d_tmp for d in D)
            # model.cost = Objective(expr=sum(model.delta[d]+model.Lk[d]/150 for d in D))
            model.cost = Objective(expr=sum(model.delta[d] for d in D) + (model.epsilon[0]) / 1000)
            # model.cost = Objective(expr=model.epsilon[0])

        elif type == 5:
            model.gamma = Var(t_d, D, within=Binary, initialize=0)
            # for i in t_d:
            #     for j in D:
            #         model.gamma[i,j].fix(1)
            model.delta = Var(D, within=Binary, initialize=0)
            for i in D:
                model.delta[i] = 1
            model.Wk = Var(D, initialize=0)
            model.HU = Var([0], initialize=0)
            model.HL = Var([0], initialize=0)
            model.epsilon = Var([0], initialize=0)
            model.Hk = Var(D, initialize=0)
            model.Ru = Var(D, initialize=0)
            model.Rd = Var(D, initialize=0)

            # #select the first and last tasks for each driver
            # def first_task(model,d):
            #     M_tmp=[i for i in T_u if i[0]==0]
            #     N_tmp=[i for i in T_d if i[0]==0]
            #     expr=sum(model.a_0[i[0],i[1],d] for i in M_tmp)+sum(model.a_1[i[0],i[1],d] for i in N_tmp)
            #     return expr<=1

            # def last_task(model,d):
            #     M_tmp=[i for i in T_u if i[1]==999]
            #     N_tmp=[i for i in T_d if i[1]==999]
            #     expr=sum(model.a_0[i[0],i[1],d] for i in M_tmp)+sum(model.a_1[i[0],i[1],d] for i in N_tmp)
            #     return expr<=1
            # model.first_task=Constraint(D,rule=first_task)
            # model.last_task=Constraint(D,rule=last_task)

            def delta_def(model, d):
                M_tmp = [i for i in T_u if i[0] == 0]
                N_tmp = [i for i in T_d if i[0] == 0]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp) + sum(model.a_1[i[0], i[1], d] for i in N_tmp)
                return expr == model.delta[d]

            model.delta_def = Constraint(D, rule=delta_def)

            # flow balance
            def fb_down(model, td, d):  # 针对下行的站点的发车班次
                M_tmp = [i for i in T_d if i[0] == td]
                N_tmp = [i for i in T_u if i[1] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_down = Constraint(t_d, D, rule=fb_down)

            def fb_up(model, tu, d):
                M_tmp = [i for i in T_d if i[1] == tu]
                N_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - sum(model.a_0[i[0], i[1], d] for i in N_tmp)
                return expr == 0

            model.fb_up = Constraint(t_u, D, rule=fb_up)

            # #every task is undertaken by a driver
            def task_down(model, td):
                M_tmp = [i for i in T_d if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_down = Constraint(t_d, rule=task_down)

            def task_up(model, tu):
                M_tmp = [i for i in T_u if i[0] == tu]
                expr = sum(model.a_0[i[0], i[1], d] for i in M_tmp for d in D)
                return expr == 1

            model.task_up = Constraint(t_u, rule=task_up)

            # Mealtime length constraints
            def have_meal(model, d):
                expr = sum(model.gamma[i, d] for i in t_d_m)
                return expr == model.delta[d]

            model.have_meal = Constraint(D, rule=have_meal)

            def have_meal_(model, d):
                expr = sum(model.gamma[i, d] for i in t_d)
                return expr == model.delta[d]

            model.have_meal_ = Constraint(D, rule=have_meal_)

            def meal_trip(model, td, d):
                M_tmp = [i for i in T_d_tmp if i[0] == td]
                expr = sum(model.a_1[i[0], i[1], d] for i in M_tmp) - model.gamma[td, d]
                return expr >= 0

            model.meal_trip = Constraint(t_d, D, rule=meal_trip)

            def meal_duration(model, td, tu, d):
                expr = (time_u[tu][0] - time_d[td][1] - theta_0) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_duration = Constraint(T_d_tmp, D, rule=meal_duration)

            def meal_not_late(model, td, tu, d):
                expr = (time_u[tu][0] - mealwindow[0] - theta_1) * model.a_1[td, tu, d] - (model.gamma[td, d] - 1) * M
                return expr >= 0

            model.meal_not_late = Constraint(T_d_tmp, D, rule=meal_not_late)

            # 最晚班次下班时间-最早班次上班时间
            def wk_def(model, d):
                M_tmp = [i[1] for i in T_u if i[0] == 0 and i[1] != 999]
                N_tmp = [i[1] for i in T_d if i[0] == 0 and i[1] != 999]
                P_tmp = [i[0] for i in T_u if i[1] == 999 and i[0] != 0]
                Q_tmp = [i[0] for i in T_d if i[1] == 999 and i[0] != 0]
                expr = model.Wk[d] + sum(time_d[i][0] * model.a_0[0, i, d] for i in M_tmp) + sum(
                    time_u[i][0] * model.a_1[0, i, d] for i in N_tmp) \
                       - sum(time_u[i][1] * model.a_0[i, 999, d] for i in P_tmp) - sum(
                    time_d[i][1] * model.a_1[i, 999, d] for i in Q_tmp)
                return expr == 0

            model.wk_def = Constraint(D, rule=wk_def)

            # 两头班中间间隔时间
            def hk_def(model, d):
                M_tmp = 0
                N_tmp = 0
                t = 0
                for i in T_u_tmp:
                    M_tmp = M_tmp + (time_d[i[1]][0] - time_u[i[0]][1]) * model.a_0[i[0], i[1], d] * theta_u[t]
                    t = t + 1
                t = 0
                for i in T_d_tmp:
                    N_tmp = N_tmp + (time_u[i[1]][0] - time_d[i[0]][1]) * model.a_1[i[0], i[1], d] * theta_d[t]
                    t = t + 1
                expr = model.Hk[d] - M_tmp - N_tmp
                return expr == 0

            model.hk_def = Constraint(D, rule=hk_def)

            # 工作时间的相差间隔
            def epsilon_def(model, d1, d2):
                expr = (model.Wk[d1] - model.Hk[d1]) - (model.Wk[d2] - model.Hk[d2]) - model.epsilon[0]
                return expr <= 0

            model.epsilon_def = Constraint(D, D, rule=epsilon_def)

            # 限制只使用13辆车
            def res_vehicle(model):
                expr = sum(model.delta[d] for d in D)
                return expr == 13

            model.res_vehicle = Constraint(rule=res_vehicle)

            # 工作时间不超过900分钟
            def max_load(model, d):
                expr = model.Wk[d] - model.Hk[d] - 840
                return expr <= 0

            model.max_load = Constraint(D, rule=max_load)

            def Rd_def(model, d):
                # 下行班次的发车时间，减去上行班次的到达时间
                # 这里应该是主站的休息时间
                M_tmp = 0
                # N_tmp=0
                for i in T_u_tmp:
                    M_tmp = M_tmp + (time_d[i[1]][0] - time_u[i[0]][1]) * model.a_0[i[0], i[1], d]
                # for i in T_d_tmp:
                #     N_tmp=N_tmp+(time_u[i[1]][0]-time_d[i[0]][1])*model.a_1[i[0],i[1],d]

                expr = model.Rd[d] - M_tmp
                return expr == 0

            model.Rd_def = Constraint(D, rule=Rd_def)

            def Ru_def(model, d):
                # 上行班次的发车时间-下行班次的到达时间
                # 这里应该是副站的休息时间
                # M_tmp=0
                N_tmp = 0
                # for i in T_u_tmp:
                #     M_tmp=M_tmp+(time_d[i[1]][0]-time_u[i[0]][1])*model.a_0[i[0],i[1],d]
                for i in T_d_tmp:
                    N_tmp = N_tmp + (time_u[i[1]][0] - time_d[i[0]][1]) * model.a_1[i[0], i[1], d]

                expr = model.Ru[d] - N_tmp
                return expr == 0

            model.Ru_def = Constraint(D, rule=Ru_def)

            # model.time_gap=sum((time_d[i[1]][0]-time_u[i[0]][1])*model.a_0[i[0],i[1],d] for i in T_u_tmp for d in D)+sum((time_u[i[1]][0]-time_d[i[0]][1])*model.a_1[i[0],i[1],d] for i in T_d_tmp for d in D)
            # model.cost = Objective(expr=sum(model.delta[d]+model.Lk[d]/150 for d in D))
            model.cost = Objective(expr=sum(model.delta[d] for d in D) + (model.epsilon[0]) / 1000 + sum(
                model.Ru[d] for d in D) / 300 + sum(model.Ru[d] for d in D) / 400)
        return model

    def analyze(model, parameters, startTime):
        '''
        根根据对应的模型和参数来进行求解，并输出对应的参数

        input:
        model是求解好的model

        output:
        输出对应alpha、beta、gamma
        在out_put_[parametersName].csv文件夹中
        '''

        a_0 = model.a_0
        a_1 = model.a_1
        # gamma = model.gamma
        T_u = parameters[2]
        T_d = parameters[3]
        # T_u_tmp = [i for i in T_u if i[0] != 0 and i[1] != 999]
        # T_d_tmp = [i for i in T_d if i[0] != 0 and i[1] != 999]
        t_d = parameters[7]
        D = parameters[1]
        # output_a_0 = pd.DataFrame(columns=['task', 'driver', 'value'])
        # output_a_1 = pd.DataFrame(columns=['task', 'driver', 'value'])
        # output_gamma = pd.DataFrame(columns=['task', 'driver', 'value'])
        # 从model数据中提取出来对应的班次数据
        all = []
        for i in T_u:
            # 这里的T_u已经将不可能的班次给去掉了
            # 针对每一个上行班次，也就是执行完一个下行班次之后执行上行班次
            for j in D:
                if round(value(a_0[i[0], i[1], j])) == 1:
                    banci = []
                    # 时间
                    if i[0] == 0:
                        pass
                    elif i[1] == 999:
                        banci.append((startTime[0][i[0] - 1]))
                        # 模式
                        banci.append(0)
                        # 路牌班次
                        banci.append(j)
                        all.append(banci)
                    else:
                        banci.append((startTime[0][i[0] - 1]))
                        # 模式
                        banci.append(0)
                        # 路牌班次
                        banci.append(j)
                        all.append(banci)

        for i in T_d:
            # 这里的T_d已经将不可能的班次给去掉了
            # 针对每一个下行班次，也就是执行完一个上行班次之后执行下行班次
            for j in D:
                if round(value(a_1[i[0], i[1], j])) == 1:
                    banci = []
                    # 时间
                    if i[0] == 0:
                        pass
                    elif i[1] == 999:
                        banci.append(startTime[1][i[0] - 1])
                        # 模式
                        banci.append(1)
                        # 路牌班次
                        banci.append(j)
                        all.append(banci)
                    else:
                        banci.append(startTime[1][i[0] - 1])
                        # 模式
                        banci.append(1)
                        # 路牌班次
                        banci.append(j)
                        all.append(banci)
        # 如何从中得到正确的时刻表数据
        allbanci = np.array(all)
        allbanci = np.unique(allbanci, axis=0)

        realdirvers = np.unique(allbanci[:, 2])

        timetable_array = []
        firstStartTime = []
        for i in range(len(realdirvers)):
            temp_one_driver = allbanci[allbanci[:, 2] == realdirvers[i]]
            # 按照时间进行排序
            temp_one_driver = temp_one_driver[temp_one_driver[:, 0].argsort()]
            firstStartTime.append(temp_one_driver[0][0])
            bus = []
            for banci in temp_one_driver:
                banci[2] = i + 1
                bus.append(banci.tolist())
            timetable_array.append(bus)

        # 按照第一次时间进行排序

        index = np.array(firstStartTime).argsort()
        new_timetable_array = []
        bus_index = 1
        for i in index:
            temp_timetable_array = []
            for banci in timetable_array[i]:
                banci[2] = bus_index
                temp_timetable_array.append(banci)
            bus_index += 1
            new_timetable_array.append(temp_timetable_array)

        return new_timetable_array

    # 先得到timetable_array、turning_time和turning_point
    import ast
    # 选择最原始的时刻表作为输出
    timetable_array = ast.literal_eval(
        Timetable.objects.filter(is_origin=1).order_by('-change_time')[0].timetable_array)
    e2 = ast.literal_eval(Estimate.objects.order_by('-change_time')[0].all_estimate)
    turning_time = e2['turning_time']  # get the turning time and the turning point for the per-estimate
    turning_point = e2['turning_point']

    import re

    fleet_size = re.findall(r'\d+', Busnumber(timetable_array, turning_time, turning_point))
    if int(data.POST['tape']) == 4:
        fleet_size_flag = 0
    else:
        fleet_size_flag = 1

    if fleet_size_flag == 0:
        fleet_size = len(timetable_array)
    else:
        fleet_size = int(fleet_size[0]) + 8
    # 调用createParameters（）来通过读取数据，得到模型建立的参数，【额外的发车时间】
    # 根据参数createModel（），并按照不同的形式来构建不同的模型，不同的type
    parameters, startTime = createParameters(fleet_size)

    model = createModel(parameters, int(data.POST['tape']))

    # 用来检验模型中的参数是否被初始化
    print('=====1011 是否初始化的调整=====')
    print(fleet_size)
    # print(value(model.a_0[4,7,12]))

    solver = SolverFactory('cplex')
    solver.options['mip tolerances mipgap'] = 0.2
    result = solver.solve(model, tee=True)
    # 从模型的结果中analyze()相对应的参数
    new_timetable_array = analyze(model, parameters, startTime)

    # 时刻表评价指标函数
    index_axes, time_axes = formatAxis(new_timetable_array)
    estimate = timetable_estimate(new_timetable_array, turning_time, turning_point)
    new_timetable = Timetable()

    timetable_return = new_timetable.newTimetable(new_timetable_array, estimate, index_axes, time_axes, turning_point,
                                                  turning_time, 0, period)

    return HttpResponse(timetable_return)


def create_timetable_one_step(data):
    temp = Timetable.objects.order_by('-change_time')[0].all_timetable
    Timetable.objects.order_by('-change_time')[0].delete()
    try:
        timetable_return = Timetable.objects.order_by('-change_time')[0].all_timetable
    except:
        timetable_return = temp
    return HttpResponse(timetable_return)


def create_timetable_origin(data):
    timetable_return = Timetable.objects.filter(is_origin=1).order_by('-change_time')[0].all_timetable
    return HttpResponse(timetable_return)


def adjust_timetable_ajax(data):
    # 这个是用来处理前端的鼠标操作调整数据，=> 选择的目标+时间和班次移动 => 修改对应的timetable文件 => 检验和重新修改
    # 前后端时间的调整，行程时间的计算
    # 调整过程：从前端传递的数据来对对应的timetable矩阵进行重新计算，所以这里的timetable数据是从json中取的，同时修改之后需要传递到json中去和返回去前端
    # 检验条件1 ：前后路牌的时间间隔必须是 休息时间间隔，或者是行程时间间隔（但是这一段的计算可能会比较复杂），一种是前后相同必须满足最好休息时间，一种是必须满足休息时间+时间间隔时间
    # 检验条件2：两头班的休息时间的计算

    # from adjust inforamtion to get the co-ordinate about the select(now) and the change(to change)
    select_left = int(data.POST['before_left'])
    select_top = int(data.POST['before_top'])
    change_left = int(data.POST['new_left'])
    change_top = int(data.POST['new_top'])

    if change_left == 0:
        change_left = select_left
    if change_top == 5:
        change_top = select_top

    # using the co-ordinate of the select div to get the to [index , start_time]
    select_index = int((select_top - 125) / 30)
    select_starttime = int(select_left + 200)
    change_index = int((change_top - 125) / 30)
    change_starttime = int(change_left + 200)

    # from record timetable json to load the timetable_array which contains the timetable data with the format
    # [start_time,pattern,index]

    # 得到timetable_array来辅助计算，在timetable的timetable-array里面
    import ast
    timetable_array = ast.literal_eval(Timetable.objects.order_by('-change_time')[0].timetable_array)

    # 遍历选中路牌中的每个班次
    # 应该选中的时刻表是之前的，所以一定会存在这个时刻表
    for i in range(len(timetable_array[select_index - 1])):

        if timetable_array[select_index - 1][i][0] == select_starttime:
            # 根据选择班次的发车时间select-starttime来选择对应的路牌

            # 如果相等的就选择对应的班次，记录在temp-class中
            temp_class = timetable_array[select_index - 1][i]

            # 然后删除改变的班次
            timetable_array[select_index - 1].remove(timetable_array[select_index - 1][i])
            break

    # 然后将之前暂存的班次，更改发车时间和下标
    temp_class[0] = change_starttime
    temp_class[2] = change_index

    # 将该暂存班次插入时刻表
    if change_index <= len(timetable_array):
        # 如果这个路牌在时刻表中
        if len(timetable_array[change_index - 1]) > 0:
            # 保证该路牌的班次数量大于1
            for i in range(len(timetable_array[change_index - 1])):  # loop the every index in the timetable-array
                # 遍历改变路牌的每一个班次
                if i < len(timetable_array[change_index - 1]) - 1:
                    # 当不是最后一个班次的时候
                    if change_starttime < timetable_array[change_index - 1][i][0]:
                        timetable_array[change_index - 1].insert(i, temp_class)
                        break
                else:
                    # 如果均不小于，说明是最后一个
                    timetable_array[change_index - 1].append(temp_class)
        else:
            timetable_array[-1].append(temp_class)
    else:
        # 如果路牌不在时刻表之中

        timetable_array.append([])
        timetable_array[-1].append(temp_class)

    flag = 0

    # 如果调整之后，某一个路牌没有班次，就删除该路牌

    for index_bus in timetable_array:
        if index_bus == []:
            timetable_array.remove([])

    # 重命名班次的对应的路牌

    for i in range(len(timetable_array)):
        for class_bus in timetable_array[i]:
            class_bus[2] = i + 1

    import ast
    e2 = ast.literal_eval(Estimate.objects.order_by('-change_time')[0].all_estimate)
    turning_time = e2['turning_time']  # get the turning time and the turning point for the per-estimate
    turning_point = e2['turning_point']

    # 时刻表评价指标函数
    index_axes, time_axes = formatAxis(timetable_array)
    estimate = timetable_estimate(timetable_array, turning_time, turning_point)
    new_timetable = Timetable()

    timetable_return = new_timetable.newTimetable(timetable_array, estimate, index_axes, time_axes, turning_point,
                                                  turning_time, 0, period)

    ao = AdjustOption(lineName=RecordRequest.objects.order_by('-change_time')[0].lineName,
                      meta_select_left=select_left,
                      meta_select_top=select_top,
                      meta_change_left=change_left,
                      meta_change_top=change_top,
                      # 由像素值解析得到的，选择的班次和选择的时间和改变后的班次和时间
                      select_index=select_index,
                      select_starttime=select_starttime,
                      change_index=change_index,
                      change_starttime=change_starttime,
                      all_estimate=estimate,
                      )
    ao.save()
    return HttpResponse(timetable_return)


def timetable_gen(whatever):
    '''
    whatever==1：根据后台数据生成可视化界面
    wahtever==其他：根据上传的文件生成可视化界面
    '''

    global time_axes
    global index_axes
    request = model_to_dict(RecordRequest.objects.order_by('-change_time')[0])
    import time

    if whatever == 1:
        # 第一种通过后台数据的方式生成时刻表
        # whatever等于2是通过上传文件生成时刻表

        # 根据后台数据生成可视化界面
        # 需要定义：行程时间、行程时间断点、线路名称、坐标轴、坐标时间
        turnning_point = [[[0, 390, 1080, 1440], [0, 390, 1080, 1440]],
                          [[0, 330, 360, 385, 480, 510, 540, 900, 1080, 1200, 1440],
                           [0, 390, 435, 540, 960, 1050, 1140, 1200, 1290, 1440]],
                          [[0, 390, 450, 1160, 1440], [0, 370, 480, 1140, 1200, 1440]],
                          [[0, 480, 1140, 1440], [0, 480, 1140, 1440]],
                          [[0, 415, 445, 475, 500, 960, 990, 1050, 1080, 1440],
                           [0, 410, 440, 470, 540, 970, 990, 1080, 1440]],
                          [[0, 415, 445, 475, 500, 960, 990, 1050, 1080, 1440],
                           [0, 410, 440, 470, 540, 970, 990, 1080, 1440]],
                          [[0, 415, 445, 475, 500, 960, 990, 1050, 1080, 1440],
                           [0, 410, 440, 470, 540, 970, 990, 1080, 1440]],
                          [[0, 1440], [0, 1440]],
                          [[0, 421, 1150, 1440], [0, 421, 1150, 1440]]]

        turnning_time = [[[45, 50, 45], [45, 50, 45]],
                         [[65, 70, 75, 90, 85, 80, 75, 80, 75, 65], [65, 70, 80, 75, 80, 85, 80, 75, 65]],
                         [[65, 70, 75, 65], [65, 70, 75, 70, 65]],
                         [[40, 45, 40], [40, 45, 40]],
                         [[50, 55, 60, 55, 50, 55, 60, 55, 50], [50, 55, 60, 55, 50, 55, 60, 50]],
                         [[50, 55, 60, 55, 50, 55, 60, 55, 50], [50, 55, 60, 55, 50, 55, 60, 50]],
                         [[50, 55, 60, 55, 50, 55, 60, 55, 50], [50, 55, 60, 55, 50, 55, 60, 50]],
                         [[45], [45]],
                         [[40, 45, 40], [40, 45, 40]]]

        import datetime
        import pandas as pd
        import numpy as np

        # 自动调整的设置为line
        def time2int(input):
            return input.hour * 60 + input.minute

        if int(request['line']) == -1:
            # 路牌数量
            index = int(request['Num_RoadSigns'])
            # 22-06-03 这里前端输入headway的方式不要
            # headway=int(request['Headway'])
            # running_time = int(request['Running_time'])
            headway = readHRExcel('self_headway.xlsx')
            [turning_point, turning_time] = readHRExcel('self_running.xlsx')

            index_axes, time_axes = 2, [5, 22]
            # 主站开始工作的时间
            s_o = time2int(request['StartTime_Origin'])
            e_o = time2int(request['EndTime_Origin'])

            # 副站开始工作的时间
            s_t = time2int(request['StartTime_Termnial'])
            e_t = time2int(request['EndTime_Terminal'])

            # 上行的数据
            start_up = headway2starttime(s_t, e_t, headway, 0)

            # 下行的数据 - 主站
            start_down = headway2starttime(s_o, e_o, headway, 1)

            # 生成时刻表
            timetable_array = start2timetable(start_up, start_down)
        else:
            timetable_xlsx = pd.read_excel(line_name[int(request['line']) - 1], header=0,
                                           dtype={'start_time': datetime.time})
            start_times = [start_time.hour * 60 + start_time.minute for start_time in timetable_xlsx['start_time']]
            timetable_xlsx['start_time'] = start_times
            index_init = max(timetable_xlsx['index'])
            timetable = []
            for i in range(index_init):
                timetable.append([])
            # 这里读取的Excel是已经经过start-time排序+index排序之后，所以直接输出的班次可以如此直接
            for row in timetable_xlsx.iterrows():
                if row[1]['pattern'] != -1:
                    bus = []
                    bus.append(int(row[1]['start_time']))
                    bus.append(int(row[1]['pattern']))
                    bus.append(int(row[1]['index']))
                    timetable[row[1]['index'] - 1].append(bus)
            timetable_array = timetable
            print(timetable_array)
            turning_time = turnning_time[int(request['line']) - 1]
            turning_point = turnning_point[int(request['line']) - 1]
            index_axes, time_axes = formatAxis(timetable_array)

    else:
        # 根据上传的时刻表文件生成可视化界面
        import pandas as pd
        global filename
        sheetDf = pd.read_excel(filename, sheet_name=None)
        sheet_index = sheetChoose(sheetDf)
        df2 = pd.read_excel(filename, sheet_name=sheet_index)
        # 1 call for the buffer_bias of index

        # for target timetbale(eg,df2), by using the re to match the numbers and the string in
        # index for choose Origin timetable and then split it with re into timetable of weekend and
        # timetable of weekday(it need a choose which we using assumption to take place)
        df_day, df_end = splitTimetable(chooseIndexFromOrigin(df2))
        if period == 1:
            df_choose = df_day
        if period == 2:
            df_choose = df_end
        # after choosing the timetable named df_choose we want to visualisze
        # first,col-re to get the dataframe for only bus_time and the dataframe for only bus_travel_time
        # second,using time and travel_time to get the timetable array and temp_thing(travel time and start_time)
        df_bus, df_time = reshapeTimeTable(df_choose)
        timetable_array, tt_ts, start_time = formatTimetaleArray(df_bus, df_time)
        turning_point, turning_time = formatTurnningTime(tt_ts)
        index_axes, time_axes = formatAxis(timetable_array)
    return timetable_array, turning_point, turning_time, index_axes, time_axes


def timetable_estimate(timetable, time, points):
    # 功能对输入的时刻表进行指标的计算和约束的生成

    # 生成的评价包括
    # 1。 行休比例、工作时间、运营里程
    # 2。 上行间隔时间、下行间隔时间
    # 3。 半周期时间、周期时间、休息时间（layovertime）

    # timetable    时刻表
    # time 对应班次的行程时间
    # points 对应班次的行程时间转折
    global history_rest_ratio

    # 参数初始定义
    DISTANCE_BUS = 20  # 车辆的运行距离

    TWO_CLASS_DIFF = 109  # 车辆的最大间隔距离

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
    busNumber = Busnumber(timetable, time, points)

    # 00-基础-计算并删除中间的休息时间
    start_time_up = []
    start_time_down = []

    for index_bus in timetable:
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
                if ((index_start_time[i + 1] - index_start_time[i]) - work_time_gen(time, points, index_start_time[i],
                                                                                    1)) > TWO_CLASS_DIFF:
                    delet_time = delet_time + ((index_start_time[i + 1] - index_start_time[i]) - work_time_gen(
                        time, points,
                        index_start_time[i], 0))
        class_pattern.append(delet_time)

    start_time_up = sorted(start_time_up)
    start_time_down = sorted(start_time_down)

    # 01--计算三个对应的指标，包括行休比例、工作时间、车行公里数
    for index_bus in timetable:
        start_work = 1440
        end_work = 0
        runwaytime = 0  # 在车上的时间
        for class_bus in index_bus:
            runwaytime = runwaytime + work_time_gen(time, points, class_bus[0],
                                                    class_bus[1])  # 计算工作时间。行程时间累加
            start_work = min(start_work, class_bus[0])
            end_work = max(end_work, class_bus[0] + work_time_gen(time, points,
                                                                  class_bus[0], class_bus[1]))
        runway_time.append(runwaytime)  # 仅仅包括行程时间，在车上面的时间
        inwork_time.append(end_work - start_work)  # 车辆在站内的时间，还没去掉两头班的两个小时
        runway.append(len(index_bus) * DISTANCE_BUS)

    work_time = [inwork_time[i] - class_pattern[i] for i in range(len(class_pattern))]  # 站内时间 减去 两头班的时间存在的时间
    print('====work time(工作时间）=====')
    print('work_time=' + str(work_time))

    rest_ratio = [(work_time[i] - runway_time[i]) / runway_time[i] for i in range(len(work_time))]
    # 02--计算对应的上行间隔和下行间隔
    for index_bus in timetable:
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
    for bus_index in timetable:
        # 时刻表中的每个路牌，计算circle time，目前是保证没有deadhead的情况，但是调整的时候会出现问题
        for i in range(len(bus_index) - 1):
            # 针对某个路牌的每个班次
            start_time_01.append(bus_index[i][0])
            half_circle_time.append(bus_index[i + 1][0] - bus_index[i][0])
            layover_time.append(
                bus_index[i + 1][0] - bus_index[i][0] - work_time_gen(time, points, bus_index[i][0], bus_index[i][1]))
        for i in range(len(bus_index) - 2):
            # 针对每个路牌的每个班次
            start_time_02.append(bus_index[i][0])
            circle_time.append((bus_index[i + 2][0] - bus_index[i][0]))

    # 按照时间进行排序
    half_circle_time = np.array(half_circle_time)[np.array(start_time_01).argsort()].tolist()
    layover_time = np.array(layover_time)[np.array(start_time_01).argsort()].tolist()
    circle_time = np.array(circle_time)[np.array(start_time_02).argsort()].tolist()
    print('==== 路牌数据=====')
    print('banci=' + str([circle_time, half_circle_time, layover_time]))

    # 03-limitation的检验

    # limitation的检验
    # 观察数据中可能存在的错误
    # task1：路牌中相邻班次的间隔时间，上下行之间休息时间、上行之间或者下行之间周转时间（包括deadheading）
    # task2：路牌工作时间的检验
    # task3：上下行间隔时间的检验，对班次间隔较大给出提示
    REST_LEAST = 5
    REST_LEAST_SAME = 60
    WORK_TIME_LEAST = 600
    WORK_TIME_MOST = 840
    limitation = ''

    for index_bus in timetable:
        if len(index_bus) > 1:
            for i in range(len(index_bus) - 1):
                if index_bus[i][1] == index_bus[i + 1][1]:  # 说明是相同班次的情况
                    if (index_bus[i + 1][0] - index_bus[i][0] - work_time_gen(time, points,
                                                                              index_bus[i][0],
                                                                              index_bus[i][1])) < REST_LEAST_SAME:
                        limitation = limitation + str(index_bus[i][2]) + '路牌存在相同班次之间周转时间冲突\n'
                else:
                    if (index_bus[i + 1][0] - index_bus[i][0] - work_time_gen(time, points,
                                                                              index_bus[i][0],
                                                                              index_bus[i][1])) < REST_LEAST:
                        limitation = limitation + str(index_bus[i][2]) + '路牌存在休息时间的冲突\n'
    for i in range(len(work_time)):
        if work_time[i] < WORK_TIME_LEAST:
            limitation = limitation + str(i + 1) + '小于10小时\n'
        if work_time[i] > WORK_TIME_MOST:
            limitation = limitation + str(i + 1) + '超过14小时\n'

    if max(diff_time_down) > 40:
        limitation = limitation + '班次的下行间隔时间不均匀'
    if max(diff_time_up) > 40:
        limitation = limitation + '班次的上行间隔时间不均匀'

    history_rest_ratio.append(np.mean(rest_ratio))
    if len(history_rest_ratio) < 10:
        pass
    else:
        history_rest_ratio = history_rest_ratio[-9:]

    # 得到最近一次生成原始时刻表的时间Timetable（model）中得到
    # 再检索得到本次运行中得到的
    # 根据之前将一些评价文件存储到评价之中
    estimate1 = {'limitation': limitation,
                 'rest_ratio': rest_ratio,
                 'work_time': work_time,
                 'runway': runway,
                 'diff_time_up': diff_time_up,
                 'diff_time_down': diff_time_down,
                 'history_rest_ratio': history_rest_ratio,

                 'half_circle_time': half_circle_time,
                 'circle_time': circle_time,
                 'layover_time': layover_time,

                 'warning': '暂无问题',
                 'turning_time': time,
                 'turning_point': points}
    estimate_json = json.dumps(estimate1, cls=NpEncoder)

    print('diff=' + str([[start_time_up, diff_time_up], [start_time_down, diff_time_down]]))
    evaluation1 = Estimate(lineName=RecordRequest.objects.order_by('-change_time')[0].lineName,
                           all_estimate=estimate_json,
                           busNumber=12, rest_ratio_average=np.mean(rest_ratio))

    evaluation1.save()
    # import ast
    # estimate2=ast.literal_eval(Estimate.objects.order_by('-change_time')[0].all_estimate)

    # 在基础上增加一些东西
    estimate1['information'] = ''
    estimate1['busNumber'] = busNumber
    estimate1['busName'] = RecordRequest.objects.order_by('-change_time')[0].lineName
    return estimate1


def create_timetable_renew_ajax(number):
    # 这里的输入应该是按照调整：时间调整或者是班次调整输入的相关的参数数据

    with open("Record_adjust_timetable.json", "w") as f:
        json.dump(number.POST, f, ensure_ascii=False)
    timetable_array = timetable_gen(number)
    JSON_timetable = []
    for line in timetable_array:
        bus_class = 1
        for bus in line:
            banci = dict(starttime=bus[0], endtime=bus[1], pattern=bus[2], index=bus[3], bus_class=bus_class)
            bus_class = bus_class + 1
            JSON_timetable.append(banci)
    timetable = {'timetable': JSON_timetable, 'estimate': timetable_estimate(timetable_array)}
    timetable = json.dumps(timetable, separators=(',', ':'), cls=NpEncoder)
    return HttpResponse(timetable)
    # 这里利用一个函数生成时刻表的初始值，时刻表的格式为【【第一个路牌：【starttime，endtime，pattern，index】，，，】，【】】


def input_data_check():
    '''
    input：null
    output：null或者 错误的文本提示
    description：对最近输入的时刻表生成数据，进行生成检验，来判断是否有错误
    '''

    base_alert = '基本错误'
    # 按照时间逆序的方式（从最近到之前的顺序来实现实例的选取）
    target = RecordRequest.objects.order_by('-change_time')[0]
    base_alert_length = len(base_alert)
    if target.Num_RoadSigns != (target.Capacity_Start + target.Capacity_Terminal):
        base_alert = base_alert + '输入的路牌数量和起始点司机的数量不对应，请修改\n'
    if target.Pattern != ((target.Capacity_Start != 0) + (target.Capacity_Terminal != 0) * 2):
        base_alert = base_alert + '输入的停车场模式和起始点停车场数量不对应，请修改\n'

    if target.StartTime_Origin > target.EndTime_Origin:
        base_alert = base_alert + '起点运营时间的冲突\n'

    if target.StartTime_Termnial > target.EndTime_Terminal:
        base_alert = base_alert + '终点运营时间的冲突\n'

    # if (Num_RoadSigns & Pattern & Capacity_Start & Capacity_Terminal & StartTime_Termnial & StartTime_Origin &
    # EndTime_Terminal & EndTime_Terminal): base_alert = base_alert + '有部分所需数据尚未输入\n'

    check_alert = ''
    if len(base_alert) != base_alert_length:
        check_alert = base_alert + check_alert

    if int(target.Num_RoadSigns) < 1:
        # 具体的条件设置后面可以更改
        # 这里仅仅作为展示
        check_alert = check_alert + '所给路牌数量过少'
    return check_alert


def Busnumber(timetable_array, turning_time, turning_point):
    '''
    input:时刻表数据、行程时间、行程时间中断点
    output：最小配车数
    '''
    launch = []  # name has no meaning
    for index in timetable_array:
        for bus in index:
            launch_bus = []
            launch_bus.append(bus[0])  # start_time
            launch_bus.append(bus[1])  # 0 for upstream and 1 for downstream
            launch_bus.append(1)
            launch.append(launch_bus)
            arrive_bus = []
            arrive_bus.append(bus[0] + work_time_gen(turning_time, turning_point, bus[0], bus[1]))
            arrive_bus.append(bus[1])
            arrive_bus.append(-1)
            launch.append(arrive_bus)
    launch = np.array(launch)
    launch = launch[launch[:, 0].argsort()]
    plot_up = launch[launch[:, 1] == 0, :]
    plot_down = launch[launch[:, 1] == 1, :]
    plot_up = plot_up[:, [0, 2]]
    plot_up[:, 1] = plot_up[:, 1].cumsum()
    plot_down = plot_down[:, [0, 2]]
    plot_down[:, 1] = plot_down[:, 1].cumsum()
    plot_all = launch[:, [0, 2]]
    plot_all[:, 1] = plot_all[:, 1].cumsum()
    change_time = np.unique(launch[:, 0])
    num_up = []
    num_down = []
    for time in change_time:
        if time < plot_up[0, 0]:
            # before the beginning
            num_up.append(0)
        if time > plot_up[plot_up.shape[0] - 1, 0]:
            # after the end
            num_up.append(plot_up[plot_up.shape[0] - 1, 1])
        for i in range(plot_up.shape[0] - 1):
            # just in the right time
            if plot_up[i, 0] <= time and plot_up[i + 1, 0] > time:
                num_up.append(plot_up[i, 1])
                break
    for time in change_time:
        if time < plot_down[0, 0]:
            # before the beginning
            num_down.append(0)
        if time > plot_down[plot_down.shape[0] - 1, 0]:
            # after the end
            num_down.append(plot_down[plot_down.shape[0] - 1, 1])
        for i in range(plot_down.shape[0] - 1):
            # just in the right time
            if plot_down[i, 0] <= time and plot_down[i + 1, 0] > time:
                num_down.append(plot_down[i, 1])
                break
    num = num_up + num_down
    busNumber = ''
    busNumber = busNumber + '理论最小配车数：' + str(max(plot_all[:, 1])) + '\n'
    busNumber = busNumber + '实际配车数' + str(len(timetable_array))
    return busNumber


def work_time_gen(times_input, points_input, start_time, pattern):
    '''
    input：输入行程时间、时间的转折点、发车时间和模式
    output: 理论工作时间
    '''
    # 功能是计算已知模式和发车时间班次的实际运行时间
    # times_input 输入的行程时间间断
    # points_input 输入的行程时间的间断点
    # start_time 指的是目标行程时间
    # pattern 目标的上行或者下行间隔

    request = model_to_dict(RecordRequest.objects.order_by('-change_time')[0])
    work_time_return = int(request['Running_time'])
    pattern = int(pattern)

    for i in range(len(points_input[pattern])):
        if start_time < (points_input[pattern][i] + 1):
            work_time_return = times_input[pattern][i - 1]
            break
    return work_time_return  # times——input开始的时间一定是0。所以一定会有值


## pandas 中匹配对应字符串的函数，str.contains
# eg:选择数字所在行df.iloc[:,0].str.contains('\d+',na=False)
import pandas
import pandas as pd
import numpy as np


def chooseIndexFromOrigin(df: pandas.DataFrame) -> pandas.DataFrame:
    '''
    选择对应的路牌
    '''
    df.iloc[:, 0] = df.iloc[:, 0].astype(str)
    return df[df.iloc[:, 0].str.contains('\d+|路牌', na=False)]


def splitTimetable(df_index: pandas.DataFrame):
    '''
    选择对应工作日或者休息日的时刻表
    '''
    logic = df_index.iloc[:, 0].str.contains('实施', na=False)
    logic = logic.astype(int)
    logic = logic.cumsum()
    df_weekday = df_index[logic == 1]
    df_weekday = df_weekday[df_weekday.iloc[:, 0].str.contains('^\d+|^路牌', na=False)]
    if max(logic) == 2:
        df_weekend = df_index[logic == 2]
        df_weekend = df_weekend[df_weekend.iloc[:, 0].str.contains('^\d+|^路牌', na=False)]
    else:
        df_weekend = df_weekday
    return df_weekday, df_weekend


def reshapeTimeTable(df):
    '''
    重新修正时刻表文件
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


def sheetChoose(sheetDf):
    sizes = []
    for sheet in sheetDf:
        sizes.append(sheetDf[sheet].size)
    # return sizes.index(max(sizes))
    return 2


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


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def download(data):
    # 得到timetable_array来辅助计算，在timetable的timetable-array里面
    from django.http import StreamingHttpResponse
    import ast
    timetable_array = ast.literal_eval(Timetable.objects.order_by('-change_time')[0].timetable_array)
    import pandas as pd
    tempTT = []
    # 新建一个列表存储班次
    import datetime
    for lupai in timetable_array:
        for busclass in lupai:
            busclass[0] = datetime.time(int(busclass[0] / 60), busclass[0] - int(busclass[0] / 60) * 60, 0)
            tempTT.append(busclass)
    # 将班次生成dataframe，然后存储下来
    tempTT = pd.DataFrame(data=tempTT, columns=['发车时间', '上下行模式', '路牌序号'])
    tempTT.to_csv('timetable.csv', encoding='gbk')
    # file = open('timetable.csv', 'rb')
    # response =StreamingHttpResponse(file)
    # response['Content-Type']='text/csv'
    # response['Content-Disposition']='attachment;filename="timetable.csv"'
    with open('timetable.csv', encoding='gbk') as f:
        timetable = f.read()
    r = HttpResponse(timetable)
    r['Content-Disposition'] = 'attachment;filename="timetable.csv"'
    return r


import pandas as pd
import datetime


def readHRExcel(dir):
    '''
    专门用于读取headway和running time的时刻表，返回对应的【【【】，【】】，【【】，【】】】
    时间间隔为上行时间间隔和下行时间间隔构成的列表
    后面的为headway和running  time构成的上下行列表

    sheet1是下行--索引为0
    sheet2是上行--索引为1
    '''
    headway = []
    # 上行和下行对应的sheet之间的区分

    # headway的理想:【【【上行发车间隔】，【下行发车间隔】】，【【上行headway】，【下行headway】】】
    df1 = pd.read_excel(dir)
    cn = df1.columns
    df1 = pd.read_excel(dir, sheet_name=1, dtype={cn[0]: datetime.time})

    # 针对上行的
    time1 = [start_time.hour * 60 + start_time.minute for start_time in df1[cn[0]]]
    time1[-1] = 1440
    headway.append([])
    headway[0].append(time1)
    headway.append([])
    temp_h = [h for h in df1[cn[1]] if h]
    headway[1].append(temp_h[1:])

    # 针对下行
    df2 = pd.read_excel(dir, sheet_name=0, dtype={cn[0]: datetime.time})
    time2 = [start_time.hour * 60 + start_time.minute for start_time in df2[cn[0]]]
    time2[-1] = 1440
    headway[0].append(time2)
    temp_h = [h for h in df2[cn[1]] if h != 'nan']
    headway[1].append(temp_h[1:])

    return headway


def headway2starttime(start, end, headway, pattern):
    '''
    根据起点站的时间和终点站的时间、以及对应的发车间隔得到时刻表
    为了简单就是返回对应的发车时间
    pattern的0表示上行、1表示下行
    '''

    def headwayGen(time, headway, pattern):
        '''
        根据对应的时间来得到对应的headway ，pattern取决对应的模式
        '''

        for i in range(len(headway[0][pattern])):
            if time <= (headway[0][pattern][i] + 1):
                headwayRes = headway[1][pattern][i - 1]
                break
        return headwayRes  # times——input开始的时间一定是0。所以一定会有值

    result = [start]
    # 初始化第一辆车为start
    while result[-1] < end:
        result.append(result[-1] + headwayGen(result[-1], headway, pattern))
    return result


def start2timetable(start_time_up, start_time_down):
    timetable = []
    for i in range(2):
        timetable.append([])
    for t in start_time_up:
        bus = []
        bus.append(t)
        bus.append(0)
        bus.append(1)
        timetable[0].append(bus)
    for t in start_time_down:
        bus = []
        bus.append(t)
        bus.append(1)
        bus.append(2)
        timetable[1].append(bus)
    return timetable
