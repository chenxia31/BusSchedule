# -*- coding: utf-8 -*-
# @Create Time    : 2022/11/12 19:30
# @Update time: 2022/11/12
# @PROJECT : timetable_Create_Web
# @Author  : xuchenlong796@tongji.edu.cn
# @Software: PyCharm
# % where the utils stay
def step_time_gen(times_input, points_input, start_time, pattern):
    """
    函数功能：headway、work-time、running time 都是阶梯函数,将阶梯函数的值定义为2*n的time；
    将阶梯函数转折点定义为2*（n+1）的point，这样在输入时间点和模式的时候可以生成对应点的时间
    pattern：0代表下行，1代表上行

    input：
    time_input：为函数值，比如headway=[【45】，【45】]
    points_input:为函数值，比如points=[[0,1440],[0,1440]]
    start_time:为查询的时间,比如start_time=300
    pattern:上下行模式

    output:函数值
    """
    try:
        for i in range(len(points_input[pattern])):
            if start_time < (points_input[pattern][i] + 1):
                work_time_return = times_input[pattern][i - 1]
                break
        return work_time_return
    except:
        print('error')


def visual_timetable(timetable_array, title='Really JDBUS timetable'):
    import matplotlib.pyplot as plt
    max_index = 0
    for index in timetable_array:
        for bus in index:
            c = ['b', 'r']
            plt.hlines(y=bus[2], xmin=bus[0], xmax=bus[0] + gen_running_time(bus[0], bus[1]), colors=c[bus[1]])
            max_index = max(max_index, bus[2])
    plt.yticks(list(range(1, max_index + 1)))
    plt.title(title)
    plt.show()


# % where assisted function stays
def gen_headway(time, pattern):
    """
    option1:根据现有的headway生成

    option2:根据一个固定值动态调整
    """
    headway_time = [[30, 30, 30, 25, 25, 20, 20, 20, 25, 25, 25, 25, 30, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 20, 20,
         25, 30, 35, 35, 35, 40],
        [30, 30, 30, 30, 30, 25, 20, 20, 20, 25, 25, 25, 25, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 25, 20,
         25, 25, 35, 35, 35, 35]]
    headway_point = [
        [0, 360, 390, 415, 440, 460, 480, 500, 525, 550, 575, 600, 630, 655, 680, 710, 740, 770, 800, 830, 860, 890,
         920, 945, 970, 990, 1010, 1030, 1055, 1085, 1120, 1155, 1190, 1230, 1440],
        [0, 390, 420, 450, 480, 505, 525, 545, 565, 590, 615, 640, 665, 690, 715, 745, 775, 805, 835, 865, 895, 925,
         955, 980, 1005, 1025, 1050, 1070, 1095, 1120, 1155, 1190, 1225, 1260, 1440]]
    res1 = step_time_gen(headway_time, headway_point, time, pattern)
    return res1


def gen_running_time(time, pattern):
    """
    生成理论到达时间
    """
    turning_point = [[0, 390, 415, 440, 480, 500, 990, 1030, 1085, 1440], [0, 390, 420, 480, 980, 1025, 1095, 1440]]
    turning_time = [[25, 30, 35, 40, 35, 30, 35, 30, 25], [35, 30, 35, 30, 35, 30, 25]]
    return step_time_gen(turning_time, turning_point, time, pattern)


def init_first_run(st_main, st_sub, num_main, num_sub):
    """
    st_mian:主站发车时间
    st_sub:副站发车时间
    num_main:主站车辆数目
    num_sub:副站车辆数目
    """
    init_flights = []
    if num_sub == 0:
        # 没有副站发车车辆的简单情况
        init_flights.append(st_main)
        while len(init_flights) < num_main:
            init_flights.append(init_flights[-1] + gen_headway(init_flights[-1], 0))
    else:
        # 有副站发车车辆的复杂情况
        init_flights.append(st_sub)
        while (len(init_flights)) < num_sub:
            init_flights.append(gen_headway(init_flights[-1], 1))
    return init_flights


def gen_from_last_flights_running_time(last_flights, insert_time=-1, insert_num=-1):
    """
    last_flights:已经排列好的班次

    根据running time生成理论的发车时间
    1. headway在更改last—flight的时候会修改运营时间
    2. 削减班次的时候会修改运营时间
    """
    gen_by_running_time = []
    for flight in last_flights:
        if flight != -1:
            # -1代表空的班次
            r1 = gen_running_time(flight, 0)
            # 1120这里副站的5值得商榷
            r2 = gen_running_time((flight + r1 + 5), 1)
            gen_by_running_time.append(flight + 1.3 * (r1 + r2))
        else:
            gen_by_running_time.append(-1)
    return gen_by_running_time


def gen_from_headway(last_flights):
    """
    last_flights:已经排列好的班次

    根据headway生成理论发车时间
    """
    gen_by_headway = []
    flight_len = len(last_flights)
    while last_flights and last_flights[-1] == -1:
        last_flights.pop()
    gen_by_headway.append(last_flights[-1] + gen_headway(last_flights[-1], 0))
    while len(gen_by_headway) < flight_len:
        gen_by_headway.append(gen_by_headway[-1] + gen_headway(gen_by_headway[-1], 0))
    return gen_by_headway


EAT_FLAG = [1, 1, 1, 1]


def is_flights_time_match(gen_by_running_time, gen_by_headway, two_class_time=0):
    """
    gen_by_running_time:根据运营时间生成
    gen_by_headway:根据发车间隔生成

    option1：根据休息时间及特殊情况判断两个序列相近
    option2：特征情况需要考虑中午吃饭、两头班时间
    option3：如果两个序列并不相近，返回一定相差的时间
    """
    num = 0
    margin = []  # margin的定义为 发车间隔时间生成-运营时间生成
    for i in range(len(gen_by_running_time)):
        print('---149')
        print(gen_by_running_time)
        print(gen_by_headway)
        if gen_by_running_time[i] != -1:
            if gen_by_running_time[i] - gen_by_headway[i] > 20 and gen_by_running_time[i] > 600 and EAT_FLAG[i] == 1:
                margin.append(gen_by_headway[i] - gen_by_running_time[i] - 20)
                EAT_FLAG[i] -= 1
            else:
                margin.append(gen_by_headway[i] - gen_by_running_time[i])
            num += 1
    if margin[0] > 10:
        # 不正常的情况
        if margin[0] > 30:
            # 需要在last flight中插入班次
            return -2
        else:
            return -1

    if margin[0] < -10:
        pass

    if margin[-1] > 10:
        return -11
    if margin[-1] < -10:
        return -12
    # margin 太大
    # -1 减小lastflight的发车间隔时间
    # -2在lastflight中插入空的班次
    # -11减小发车间隔时间
    # -12 插入空的班次
    # margin太小
    # 1 增大lastflight中的发车间隔时间
    # 11 增大发车间隔时间
    # 12 插入新的班次
    # margin 太小，11增大发车间隔时间 12 插入空的班次
    # num 代表需要匹配的数量
    return 0


def change_headway(pre_flights, flights, flag):
    """
    gen_by_headway:之前生成的理论发车间隔

    如果不匹配需要对班次的headway进行调整
    注意相邻调整不能超过5min
    """
    if flag < 0:
        for i in range(len(flights)):
            for j in range(i):
                flights[len(flights) - 1 - j] += 5
                if is_flights_time_match(pre_flights, flights) == 0:
                    return flights
    else:
        for i in range(len(flights)):
            for j in range(i):
                flights[len(flights) - 1 - j] -= 5
                if is_flights_time_match(pre_flights, flights) == 0:
                    return flights


def change_empty_flight(flights):
    """
    gen_by_headway:之前生成的理论发车间隔

    返回重新生成的发车时间
    """
    # 需要一定的搜索技巧
    buffer = [flights[:-1] for _ in range(len(flights))]
    for i in range(len(flights)):
        buffer[i].insert(len(flights) - 1 - i, -1)

    for i in range(len(buffer)):
        f1 = gen_from_last_flights_running_time(buffer[i])
        f2 = gen_from_headway(buffer[i])
        if is_flights_time_match(f1, f2, two_class_time=len(flights) - 1 - i) == 0:
            break
    return buffer[i]

    # for s_flights in buffer_copy:
    #
    #     if is_flights_time_match(f1,f2)==0:
    #         break
    # return s_flights


class flights_stack:
    # 时刻表班次栈
    def __init__(self):
        self.stack = []
        self.upstream = []
        self.downstream = []

    def last_upstream(self):
        """
        返回上行的最后一个班次
        """
        if self.upstream:
            return self.upstream[-1]
        else:
            return -1

    def last_downstream(self):
        """
        返回下行的最新一个班次的发车时间
        """
        if self.downstream:
            return self.downstream[-1] + gen_headway(self.downstream[-1], 0)
        else:
            return -1

    def gen_upstream_downstream(self):
        self.upstream = []
        self.downstream = []
        for flight in self.stack:
            for f in flight:
                if f != -1:
                    self.downstream.append(f)
                    self.upstream.append(f + gen_running_time(f, 0))

    def append(self, flight):
        self.stack.append(flight)
        self.gen_upstream_downstream()

    def pop(self):
        if self.stack:
            f = self.stack.pop()
            self.gen_upstream_downstream()
        return f

    def last_flights(self):
        if self.stack:
            return self.stack[-1]

    def gen_timetable_array(self):
        """
        根据已有的flights stack生成timetable array
        """
        timetable_array = []
        for i in range(len(self.stack)):
            for j in range(len(self.stack[i])):
                if len(timetable_array) <= j:
                    timetable_array.append([])
                if self.stack[i][j] != -1:
                    timetable_array[j].append([self.stack[i][j], 0, j + 1])
                    timetable_array[j].append(
                        [self.stack[i][j] + gen_running_time(self.stack[i][j], 0) + 5, 1, j + 1])  # 这里的五分钟后面可以讨论
        return timetable_array


# % variable definition

FLIGHTS_STACK = flights_stack()  # 用于后面backtracking时候记录flights的历史记录
DOWNSTREAM = []  # 记录上行班次或者下行班次
UPSTREAM = []
WORK_TIME = []  # 记录工作时间

# % constant definition # 0 表示下行，1表示上行

num_main = 4
num_sub = 0
start_time_main = 360
end_time_main = 1230
start_time_sub = 390
end_time_sub = 1260

FLIGHTS_STACK.append(init_first_run(start_time_main, start_time_sub, num_main, num_sub))  # 初始化第一个班次
while FLIGHTS_STACK.last_upstream() < end_time_sub or FLIGHTS_STACK.last_downstream() < end_time_main:
    f1 = gen_from_last_flights_running_time(FLIGHTS_STACK.last_flights())
    f2 = gen_from_headway(FLIGHTS_STACK.last_flights())
    while is_flights_time_match(f1, f2) != 0:
        if is_flights_time_match(f1, f2) == 11:
            # 增大发车间隔
            change_headway()
        if is_flights_time_match(f1, f2) == 12:
            # 插入新的班次
            change_empty_flight()
        if is_flights_time_match(f1, f2) == 1:
            # 在lastflight中修改发车间隔
            change_empty_flight()
        if is_flights_time_match(f1, f2) == -11:
            # 减小发车间隔
            f2 = change_headway(f1, f2)
        if is_flights_time_match(f1, f2) == -12:
            # 删除班次
            pass
        if is_flights_time_match(f1, f2) == -1:
            # 减小lastflights班次的发车时间间隔
            change_empty_flight()
        if is_flights_time_match(f1, f2) == -2:
            # 删除某些班次
            FLIGHTS_STACK.append(change_empty_flight(FLIGHTS_STACK.pop()))
            f1 = gen_from_last_flights_running_time(FLIGHTS_STACK.last_flights())
            f2 = gen_from_headway(FLIGHTS_STACK.last_flights())
    FLIGHTS_STACK.append(f2)  # 优先满足发车间隔的要求
    print(FLIGHTS_STACK.gen_timetable_array())

# 一般情况下最后一个班次会有超载的现象
flights = FLIGHTS_STACK.pop()
for i in range(len(flights)):
    if flights[i] > end_time_main:
        flights[i] = -1
FLIGHTS_STACK.append(flights)

print(FLIGHTS_STACK.gen_timetable_array())
visual_timetable(FLIGHTS_STACK.gen_timetable_array())
