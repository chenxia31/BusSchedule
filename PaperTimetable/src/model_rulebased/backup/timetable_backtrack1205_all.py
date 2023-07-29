from deprecated.sphinx import deprecated
class Headway:
    def __init__(self) -> None:
        """
        初始化车头时距
        time: 车头时距
        point: 时刻
        """
        self.time=[[30, 30, 25, 25, 25, 20, 20, 20, 25, 25, 25, 25, 30, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 20, 20,
         25, 30, 35, 35, 35, 40],
        [30, 30, 30, 30, 30, 25, 20, 20, 20, 25, 25, 25, 25, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 25, 20,
         25, 25, 35, 35, 35, 35]]
        self.point=[
        [0, 360, 390, 415, 440, 460, 480, 500, 525, 550, 575, 600, 630, 655, 680, 710, 740, 770, 800, 830, 860, 890,
         920, 945, 970, 990, 1010, 1030, 1055, 1085, 1120, 1155, 1190, 1230, 1440],
        [0, 390, 420, 450, 480, 505, 525, 545, 565, 590, 615, 640, 665, 690, 715, 745, 775, 805, 835, 865, 895, 925,
         955, 980, 1005, 1025, 1050, 1070, 1095, 1120, 1155, 1190, 1225, 1260, 1440]]

    
    def get_moment_direction(self,moment,direction):
        """
        它在给定的时刻返回车头时距
        :param moment: 以分钟为单位的时间
        :param direction: 0为下行，1为上行
        :return: 车头时距
        """
        try:
            for i in range(len(self.point[direction])):
                if moment<self.point[direction][i]:
                    return self.time[direction][i-1]
        except:
            raise ("Error: headway not found")

    def adjust(self,moment,direction,adjustment):
        """
        它在给定的时刻及时调整车头时距
        
        :param moment: 以分钟为单位的时间
        :param direction: 0为北向，1为南向
        :param adjustment: 车头时距增加或减少的时间量
        :return: 调整前的车头时距
        """
        try:
            for i in range(len(self.point[direction])):
                if moment<=self.point[direction][i]:
                    if self.time[direction][i]+adjustment>=15 and self.time[direction][i]+adjustment<=35:
                        self.time[direction][i]+=adjustment
                        return self.time[direction][i-1]
        except:
            raise ("Error: headway not found")

class RunningTime:
    def __init__(self) -> None:
        """
        初始化运行时间
        time: 运行时间
        point: 时刻
        """
        self.point=[[0, 390, 415, 440, 480, 500, 990, 1030, 1085, 1440],
                  [0, 390, 420, 480, 980, 1025, 1095, 1440]]
        self.time=[[25, 30, 35, 40, 35, 30, 35, 30, 25], 
                    [35, 30, 35, 30, 35, 30, 25]]

    def get_moment_direction(self,moment,direction):
        """
        它在给定的时刻返回运行时间
        :param moment: 以分钟为单位的时间
        :param direction: 0为下行，1为上行
        :return: 运行时间
        """
        try:
            for i in range(len(self.point[direction])):
                if moment<=self.point[direction][i]:
                    return self.time[direction][i-1]
        except:
            print("Error: running time not found")

class Trip:
    def __init__(self,start_time=0,direction=0,block_id=0) -> None:
        """
        初始化车次
        start_time: 车次发车时间
        direction: 车次行驶方向
        block_id: 车次所在区间
        """
        self.start_time = start_time
        self.direction = direction # dircetion 0: downstream, 1: upstream
        self.block_id = block_id

    def to_array(self):
        """
        将车次转化为数组
        """
        return [self.start_time,self.direction,self.block_id]

class TripPair:
    def __init__(self,start_time=0,block_id=0,is_virtual=False,running_time=RunningTime()) -> None:
        """
        初始化车次对
        start_time: 车次对发车时间
        block_id: 车次对所对应路牌
        is_virtual: BOOL车次对是否为虚拟车次对
        running_time: 运行时间类
        """
        self.inbound_trip = Trip(start_time=start_time,
                                    direction=0,
                                    block_id=block_id)
        self.outbound_trip = Trip(start_time=start_time+5+running_time.get_moment_direction(start_time,0),
                                    direction=1,
                                    block_id=block_id)
        self.is_virtual = is_virtual
    
    def next_feasible_trip_pair(self,running_time=RunningTime()):
        """
        返回下一个可行的车次对
        """
        
        t1=running_time.get_moment_direction(self.inbound_trip.start_time,self.inbound_trip.direction)
        t2=running_time.get_moment_direction(self.outbound_trip.start_time,self.outbound_trip.direction)
        # TODO 这里的10可以调整？
        res=TripPair(start_time=self.inbound_trip.start_time+(t1+t2)+10,block_id=self.inbound_trip.block_id,running_time=running_time)
        return res
    
    def next_optimal_trip_pair(self,running_time=RunningTime()):
        """
        返回下一个最优的车次对
        """
        t1=running_time.get_moment_direction(self.inbound_trip.start_time,self.inbound_trip.direction)
        t2=running_time.get_moment_direction(self.outbound_trip.start_time,self.outbound_trip.direction)
        res=TripPair(start_time=self.inbound_trip.start_time+1.3*(t1+t2),block_id=self.inbound_trip.block_id,running_time=running_time)
        return res

    def to_array(self):
        return [self.inbound_trip.to_array(),self.outbound_trip.to_array(),self.is_virtual,self.next_optimal_trip_pair().inbound_trip.start_time]

class TripPairGroup:
    def __init__(self,start_time=[]) -> None:
        """
        初始化车次对组
        start_time: 车次对组发车时间
        running_time: 运行时间类
        """
        self.trip_pair_group=[]
        for i in range(len(start_time)):
            self.trip_pair_group.append(TripPair(start_time=start_time[i],block_id=i))
    
    def insert_virtual_trip_pair(self,index=-1):
        """
        插入虚拟车次对
        """
        if index==-1:
            index=len(self.trip_pair_group)-1
        virtual_trip_pair = TripPair(self.trip_pair_group[index].inbound_trip.start_time,
                                    self.trip_pair_group[index].inbound_trip.block_id,
                                    is_virtual=True,)
        self.trip_pair_group.insert(index,virtual_trip_pair)
        for i in range(index+1,len(self.trip_pair_group)):
            self.trip_pair_group[i].inbound_trip.block_id+=1
            self.trip_pair_group[i].outbound_trip.block_id+=1
        return self.trip_pair_group.pop()
    
    def insert_search(self,trip_pair_group,priority=[],bid=[]):
        """
        返回调整的trip pair group的headway
        可能会用到的有timetable中不同block的优先级
        """
        import copy
        result=[]
        chociest=[p for p in priority]
        for i in range(len(trip_pair_group.trip_pair_group)):
            if i in priority:
                continue
            else:
                chociest.append(i)
        newchociest=copy.deepcopy(chociest)
        for i in range(len(newchociest)):
            # 删除不匹配的结果
            if newchociest[i] in bid:
                chociest.remove(newchociest[i])
        print('line172----chociest',chociest)
        for i in chociest:
            res=copy.deepcopy(trip_pair_group)
            res.insert_virtual_trip_pair(i)
            result.append(res)
        return result
    
    def headway_search(self,trip_pair_group,flag='positive'):
        """
        返回调整trip pair group的headway
        返回迭代器生成的结果
        """
        res=[]
        for j in range(1,len(trip_pair_group.trip_pair_group)-1):
            if flag=='positive':
                for i in range(j,len(trip_pair_group.trip_pair_group)):
                    if trip_pair_group.trip_pair_group[i].is_virtual==True:
                        continue
                    else:
                        trip_pair_group.trip_pair_group[i]=TripPair(trip_pair_group.trip_pair_group[i].inbound_trip.start_time+5,
                                                        trip_pair_group.trip_pair_group[i].inbound_trip.block_id,
                                                        is_virtual=False)
                    yield trip_pair_group
            elif flag=='negative':
                for i in range(j,len(trip_pair_group.trip_pair_group)):
                    if trip_pair_group.trip_pair_group[i].is_virtual==True:
                        continue
                    else:
                        trip_pair_group.trip_pair_group[i]=TripPair(trip_pair_group.trip_pair_group[i].inbound_trip.start_time-5,
                                                        trip_pair_group.trip_pair_group[i].inbound_trip.block_id,
                                                        is_virtual=False)
                    yield trip_pair_group
            else:
                print("Error: flag must be positive or negative")
    
    def get_end_time(self):
        """
        返回车次对组的结束时间
        """
        for i in range(len(self.trip_pair_group)-1,-1,-1):
            if self.trip_pair_group[i].is_virtual==False:
                return self.trip_pair_group[i].inbound_trip.start_time
        raise Exception("车次对组中没有非虚拟车次对")

    def to_array(self):
        """
        转换为数组
        """
        res=[]
        for i in range(len(self.trip_pair_group)):
            res.append(self.trip_pair_group[i].to_array())
        return res
    def get_virtual_index(self):
        """
        返回虚拟车次对的索引
        """
        for i in range(len(self.trip_pair_group)):
            if self.trip_pair_group[i].is_virtual==True:
                return self.trip_pair_group[i].inbound_trip.block_id

class Timetable:
    def __init__(self,n_main=0,n_aid=0,first_trip_time=360,end_trip_time=1440,headway=Headway()) -> None:
        """
        初始化时刻表
        n_main: 主线车次对数量
        n_aid: 辅线车次对数量
        first_trip_time: 首班车发车时间
        end_trip_time: 末班车发车时间
        headway: 车头间隔类
        """
        self.group_list=[
            # TripPairList1,...
        ]
        # 总体的路牌数量
        self.block_num=n_main+n_aid
        # 首班车发车时间
        self.first_trip_time=first_trip_time
        # 末班车发车时间
        self.end_trip_time=end_trip_time
        # 允许的吃饭时间
        self.meal_time=20
        # 路牌吃饭的标记位
        self.meal_flag=[1 for _ in range(self.block_num)]
        # 路牌的班式标志
        self.block_mode=[0 for _ in range(self.block_num)]
        self.block_mode_status=[0 for _ in range(self.block_num)]
        # 两头班的优先级
        self.block_mode_buffer=[]
        # 时刻表的发车间隔
        self.headway=headway

    def Init_trip_pair_group(self):
        """
        返回可行的首班车初始化的结果
        """
        import copy
        temp_start_time_list=[self.first_trip_time]
        for i in range(self.block_num-1):
            temp_start_time_list.append(temp_start_time_list[-1]+self.headway.get_moment_direction(temp_start_time_list[-1],0))
        init_trip_pair_group=TripPairGroup(start_time=temp_start_time_list)
        res1=[init_trip_pair_group]
        for i in TripPairGroup().insert_search(init_trip_pair_group):
            res1.append(i)
        res2=[]
        for trip_pair_group in res1:
            res2.append(copy.deepcopy(trip_pair_group))
            temp_trip_pair_group=copy.deepcopy(trip_pair_group)
            for j in TripPairGroup().headway_search(trip_pair_group):
                temp=copy.deepcopy(j)
                res2.append(temp)
            for j in TripPairGroup().headway_search(temp_trip_pair_group,flag='negative'):
                temp=copy.deepcopy(j)
                res2.append(temp)
        return res2
    
    def Search_trip_pair_group(self):
        """
        寻找下一个可行的班次对
        """
        # 根据headway生成下一个班次对组
        # temp_trip_pair_group 就是下一个班次对组
        temp_start_time=self.group_list[-1].get_end_time()
        temp_start_time_list=[]
        for i in range(self.block_num):
            temp_start_time+=self.headway.get_moment_direction(temp_start_time,0)
            temp_start_time_list.append(temp_start_time)
        temp_trip_pair_group=TripPairGroup(start_time=temp_start_time_list)

        # 生成可行的班次对组
        mark,group=self.Gen_feasible_trip_pair_group(temp_trip_pair_group)
        if mark:
            return group
        else:
            return []
    
    def Gen_feasible_trip_pair_group(self,trip_pair_group):
        """
        生成可行的班次对
        """
        # 休息时间的约束
        import copy
        res=[]
        res.append(copy.deepcopy(trip_pair_group))
        # 修改发生时间间隔得到的班次对组
        for iter_trip_pair_group in TripPairGroup().headway_search(trip_pair_group=trip_pair_group,flag='negative'):
            res.append(copy.deepcopy(iter_trip_pair_group))
        for iter_trip_pair_group in TripPairGroup().headway_search(trip_pair_group=trip_pair_group,flag='positive'):
            res.append(copy.deepcopy(iter_trip_pair_group))
        # 插入虚拟班次对得到的班次对组
        for iter_trip_pair_group in TripPairGroup().insert_search(trip_pair_group=trip_pair_group):
            res.append(copy.deepcopy(iter_trip_pair_group))
            for iter_trip_pair_group2 in TripPairGroup().headway_search(trip_pair_group=iter_trip_pair_group,flag='positive'):
                res.append(copy.deepcopy(iter_trip_pair_group2))
            for iter_trip_pair_group2 in TripPairGroup().headway_search(trip_pair_group=iter_trip_pair_group,flag='negative'):
                res.append(copy.deepcopy(iter_trip_pair_group2))
        # 生成可行的班次对组
        res_copy=[]
        for trip in res:
            trip.insert_virtual_trip_pair(index=-1)
            res_copy.append(copy.deepcopy(trip))
        
        return True,res+res_copy
    
    def find_priority(self):
        """
        寻找优先级
        """
        priority=[]
        for i in range(self.block_num):
            if self.block_mode_status[i]==1:
                priority.append(i)
        for i in range(self.block_num):
            if self.block_mode[i]==1 and self.block_mode_status[i]==0 and i not in priority:
                priority.append(i)
        return priority
    
    def find_bid(self):
        """
        寻找bid
        """
        bid=[]
        for i in range(self.block_num):
            if self.block_mode_status[i]==2:
                bid.append(i)
        return bid
    def Operate_last_trip_pair_group(self,flag):
        """
        对上一个班次对组进行操作
        # TODO 调整逻辑
        """
        self.group_list[-1].Operate_trip_pair_group(flag)
    
    def rule_layover_time(self,trip_pair_group,meal_flag):
        """
        结合blocks的meal_flag进行休息时间的计算，根据休息时间来判断是否需要进行搜索
        trip_pair_group: 待匹配的车次对组
        meal_flag: 路牌吃饭的标记位
        """
        mark=0
        index=-1
        layover_time_diff,new_meal_flag=self._cal_layover_time(trip_pair_group=trip_pair_group,meal_flag=meal_flag)
        for i in range(len(layover_time_diff)):
            if trip_pair_group.trip_pair_group[i].is_virtual==False:
                if layover_time_diff[i]>10:
                    if layover_time_diff[i]>5*self.block_num:
                        # 意味着需要insert才能处理
                        mark=2
                        index=i
                        break
                    # 意味着只需要进行headway的调整就行
                    # 需要从头开始减少headway
                    mark=1
                    index=i
                    break
                elif layover_time_diff[i]<-10:
                    if layover_time_diff[i]<-5*self.block_num:
                        # 意味需要返回两头班班次，但是通常这样的情况并不会出现
                        mark=-2
                        index=i
                        break
                    # 意味着只需要进行headway的调整就行
                    # 需要从头开始增大headway
                    mark=-1
                    index=i
                    break
        return mark,index,new_meal_flag

    def _cal_layover_time(self,trip_pair_group,meal_flag):
        """
        计算待匹配班次与实际的休息时间之差
        """
        layover_time=[]
        buffer=0
        print(trip_pair_group.to_array())
        for i in range(len(trip_pair_group.trip_pair_group)):
            if trip_pair_group.trip_pair_group[i].inbound_trip.start_time>=600 and trip_pair_group.trip_pair_group[i].inbound_trip.start_time<=780:
                # eat time
                if meal_flag[trip_pair_group.trip_pair_group[i].inbound_trip.block_id]==1:
                    # eat time and meal_flag=1
                    buffer=-20
                    meal_flag[trip_pair_group.trip_pair_group[i].inbound_trip.block_id]=0
            if self._get_block_lasted_arrive(i)==0:
                layover_time.append(0)
            else:
                layover_time.append(trip_pair_group.trip_pair_group[i].inbound_trip.start_time-self._get_block_lasted_arrive(i)+buffer)
        return layover_time,meal_flag

    def _get_block_lasted_arrive(self,block_id):
        """
        获取路牌上一班车的到达时间
        """
        for i in range(len(self.group_list)-1,-1,-1):
            if self.group_list[i].trip_pair_group[block_id].is_virtual!=1:
                return self.group_list[i].trip_pair_group[block_id].next_optimal_trip_pair().inbound_trip.start_time
        return 0

    def rule_basic(self,trip_pair_group,meal_flag):
        """
        基本规则
        """
        pass

    def view(self,timetable_array,title='timetable'):
        import matplotlib.pyplot as plt
        max_index = 0
        for index in timetable_array:
            for bus in index:
                c = ['b', 'r']
                plt.hlines(y=bus[2], xmin=bus[0], xmax=bus[0] + RunningTime().get_moment_direction(bus[0], bus[1]), colors=c[bus[1]])
                max_index = max(max_index, bus[2])
        plt.yticks(list(range(1, max_index + 1)))
        plt.title(title)
        plt.show()
    
    def to_timetable_array(self):
        # convert the timetable to array
        # return the array
        timetable_array = []
        for i in range(len(self.group_list)):
            for j in range(len(self.group_list[i].trip_pair_group)):
                if len(timetable_array)<=j:
                    timetable_array.append([])
                if self.group_list[i].trip_pair_group[j].is_virtual==True:
                    pass
                else:
                    timetable_array[j].append(self.group_list[i].trip_pair_group[j].inbound_trip.to_array())
                    timetable_array[j].append(self.group_list[i].trip_pair_group[j].outbound_trip.to_array())
        return timetable_array

    def to_array(self):
        for i in range(len(self.group_list)):
            print(self.group_list[i].to_array())
    def check(self,trip_pair_group):
        self.group_list.append(trip_pair_group)

        # 行程时间的判断
        timetable_array=self.to_timetable_array()
        for block_id in range(len(timetable_array)):
            for i in range(len(timetable_array[block_id])-1):
                if timetable_array[block_id][i+1][0]-timetable_array[block_id][i][0]<RunningTime().get_moment_direction(timetable_array[block_id][i][0],timetable_array[block_id][i][1])+2:
                    self.group_list.pop()
                    return False
        
        # 两头班的计算
        new_block_status=[0 for _ in range(timetable.block_num)]
        for group in self.group_list:
            begin_status=0
            for tripPair in group.trip_pair_group:
                if tripPair.is_virtual==False:
                    begin_status=1
                if tripPair.is_virtual==True and begin_status!=0:
                    new_block_status[tripPair.inbound_trip.block_id]+=1
        if max(new_block_status)>3:
            self.group_list.pop()
            return False
        
        # 工作时间的判断
        work_time=self.evaluate(self.to_timetable_array(),flag=1)
        if max(work_time)>840:
            self.group_list.pop()
            return False
        self.group_list.pop()
        return True
    
    def get_end_time(self):
        if self.group_list==[]:
            return 0
        else:
            return self.group_list[-1].get_end_time()

    def evaluate(self,timetable_array,flag=1):
        # calculate the work time of the timetable
        # return the work time
        """
        对timetable_array形式的时刻表计算评价指标，包括

        input:
        timetable:timetable-array类别的矩阵时刻表
        time：运营时间点
        points：运营时间转折点

        output：
        1 work_time
        2 banci 类评价指标
        3 diff 间隔类评价指标
        三者做出特殊规定在之后函数可视化中有用
        """
        global history_rest_ratio

        # 参数初始定义
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
                    if ((index_start_time[i + 1] - index_start_time[i]) - RunningTime().get_moment_direction(index_start_time[i],1)) > TWO_CLASS_DIFF:
                        delet_time = delet_time + ((index_start_time[i + 1] - index_start_time[i]) - RunningTime().get_moment_direction(index_start_time[i], 0))
            class_pattern.append(delet_time)

        start_time_up = sorted(start_time_up)
        start_time_down = sorted(start_time_down)

        # 01--计算三个对应的指标，包括行休比例、工作时间、车行公里数
        for index_bus in timetable_array:
            start_work = 1440
            end_work = 0
            runwaytime = 0  # 在车上的时间
            for class_bus in index_bus:
                runwaytime = runwaytime + RunningTime().get_moment_direction(class_bus[0],
                                                        class_bus[1])  # 计算工作时间。行程时间累加
                start_work = min(start_work, class_bus[0])
                end_work = max(end_work, class_bus[0] + RunningTime().get_moment_direction(class_bus[0],
                                                        class_bus[1]))  # 计算工作时间。行程时间累加
            runway_time.append(runwaytime)  # 仅仅包括行程时间，在车上面的时间
            inwork_time.append(end_work - start_work)  # 车辆在站内的时间，还没去掉两头班的两个小时
            runway.append(len(index_bus) * DISTANCE_BUS)

        work_time = [inwork_time[i] - class_pattern[i] for i in range(len(class_pattern))]  # 站内时间 减去 两头班的时间存在的时间

        # rest_ratio = [(work_time[i] - runway_time[i]) / runway_time[i] for i in range(len(work_time))]
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
                    bus_index[i + 1][0] - bus_index[i][0] - RunningTime().get_moment_direction(bus_index[i][0], bus_index[i][1]))
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
        else:
            return work_time,banci,diff
    
timetable=Timetable(n_main=4,n_aid=0,first_trip_time=360,end_trip_time=1240,headway=Headway())
res=[]
def backtracking(timetable):
    if timetable.get_end_time()>timetable.end_trip_time-240:
        import copy
        res.append(copy.deepcopy(timetable))
        return
    # 生成next_trip_pair_group
    if timetable.group_list==[]:
        next_trip_pair_group_list=timetable.Init_trip_pair_group()
    else:
        next_trip_pair_group_list=timetable.Search_trip_pair_group()

    for next_trip_pair_group in next_trip_pair_group_list:
        # 判断新加入的trip——pair- group是否合法
        # 如果合法就不修改
        if timetable.check(next_trip_pair_group):
            timetable.group_list.append(next_trip_pair_group)  
            # 更新司机的两头班的状态
            if next_trip_pair_group.get_virtual_index():
                if len(timetable.group_list)==1:
                    timetable.block_mode[next_trip_pair_group.get_virtual_index()]=0
                else:
                    if next_trip_pair_group.trip_pair_group[0].inbound_trip.start_time>800:
                        pass
                    else:
                        timetable.block_mode_status[next_trip_pair_group.get_virtual_index()]+=1
            backtracking(timetable)
            temp=timetable.group_list.pop()
            # group list update的同时，司机的mode 和mode status也需要更新
            if temp.get_virtual_index():
                if len(timetable.group_list)==0:
                    timetable.block_mode[next_trip_pair_group.get_virtual_index()]=0
                else:
                    timetable.block_mode_status[next_trip_pair_group.get_virtual_index()]-=1

    if next_trip_pair_group_list==[]:
        return

timetable=Timetable(n_main=4,n_aid=0,first_trip_time=360,end_trip_time=1240,headway=Headway())
backtracking(timetable)
print('---最终结果---')
print(len(res))
for tt in res:
    # tt.view(tt.to_timetable_array())
    print('------------------')
    print('-                  -')
    print('******************')
    tt.to_array()
    tt.view(tt.to_timetable_array())