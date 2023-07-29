# some wonderful class defination
import copy
# AI is creating summary for __init__
# > The Headway class is a container for the headway data of a single bus line
# AI 正在为 __init__ 创建摘要
class Headway:
    def __init__(self) -> None:
        self.time=[[30, 30, 25, 25, 25, 20, 20, 20, 25, 25, 25, 25, 30, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 20, 20,
         25, 30, 35, 35, 35, 40],
        [30, 30, 30, 30, 30, 25, 20, 20, 20, 25, 25, 25, 25, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 25, 20,
         25, 25, 35, 35, 35, 35]]
        self.point=[
        [0, 360, 390, 415, 440, 460, 480, 500, 525, 550, 575, 600, 630, 655, 680, 710, 740, 770, 800, 830, 860, 890,
         920, 945, 970, 990, 1010, 1030, 1055, 1085, 1120, 1155, 1190, 1230, 1440],
        [0, 390, 420, 450, 480, 505, 525, 545, 565, 590, 615, 640, 665, 690, 715, 745, 775, 805, 835, 865, 895, 925,
         955, 980, 1005, 1025, 1050, 1070, 1095, 1120, 1155, 1190, 1225, 1260, 1440]]

    
    def get_headway(self,moment,direction):
        """
        该函数接受一个时刻和一个方向，并返回那一刻的车头时距
        
        :param moment: 以分钟为单位的时间
        :param direction: 0为北向，1为南向
        :return: 目前的进展
        """
        # get the headway at the moment
        # moment is the time in minuts
        try:
            for i in range(len(self.point[direction])):
                if moment<self.point[direction][i]:
                    return self.time[direction][i-1]
        except:
            print("Error: headway not found")
    
    def adjust(self,moment,direction,adjustment):
        """
        它在给定的时刻及时调整车头时距
        
        :param moment: 以分钟为单位的时间
        :param direction: 0为北向，1为南向
        :param adjustment: 车头时距增加或减少的时间量
        :return: 调整前的车头时距
        """
        # adjust the headway at the moment
        # moment is the time in minuts
        try:
            for i in range(len(self.point[direction])):
                if moment<=self.point[direction][i]:
                    if self.time[direction][i]+adjustment>=15 and self.time[direction][i]+adjustment<=35:
                        self.time[direction][i]+=adjustment
                        return self.time[direction][i-1]
        except:
            print("Error: headway not found")

# 类 RunningTime 用于获取给定时刻公交车的运行时间
class RunningTime:
    def __init__(self) -> None:
        self.point=[[0, 390, 415, 440, 480, 500, 990, 1030, 1085, 1440],
                  [0, 390, 420, 480, 980, 1025, 1095, 1440]]
        self.time=[[25, 30, 35, 40, 35, 30, 35, 30, 25], 
                    [35, 30, 35, 30, 35, 30, 25]]

    def get_running_time(self,moment,direction):
        """
        它需要一个时间和一个方向（向上或向下）并返回那一刻的运行时间
        
        :param moment: 以分钟为单位的时间
        :param direction: 公共汽车的方向，“入站”或“出站”
        :return: 当前运行时间
        """
        # get the running time at the moment
        # moment is the time in minuts
        try:
            for i in range(len(self.point[direction])):
                if moment<=self.point[direction][i]:
                    return self.time[direction][i-1]
        except:
            print("Error: running time not found")

class twoclass:
    def __init__(self) -> None:
        self.two_class_time=120

class Trip:
    def __init__(self,start_time=0,direction=0,block_id=0) -> None:
        """
        > `__init__` 函数是在创建对象时调用的特殊函数。它用于初始化对象
        
        :param start_time: 火车开始移动的时间, defaults to 0 (optional)
        :param direction: 0 为下游，1 为上游, defaults to 0 (optional)
        :param block_id: 火车所在街区的编号, defaults to 0 (optional)
        """
        self.start_time = start_time
        self.direction = direction # dircetion 0: downstream, 1: upstream
        self.block_id = block_id
    
    def to_array(self):
        # 上面的代码定义了一个名为“Bus”的类，它具有三个属性：start_time、direction 和 block_id。
        return [self.start_time,self.direction,self.block_id]

class TripPair:
    # generate a pair of trips with start_time and block_id
    # block_work_mode=1 means the block is two class
    def __init__(self,start_time=0,block_id=0,is_virtual=0,running_time=RunningTime()) -> None:
        """
        > `__init__` 函数使用入站和出站 `Trip` 对象以及 `next_arrive` 时间初始化一个 `Block` 对象
        
        :param start_time: 公共汽车开始第一次旅行的时间, defaults to 0 (optional)
        :param block_id: 块的id, defaults to 0 (optional)
        :param is_virtual: 0为普通模式，1为二类模式, defaults to 0 (optional)
        :param running_time: 包含每次旅行的运行时间的类。
        """
# 
        self.inbound_trip = Trip(start_time=start_time,
                                    direction=0,
                                    block_id=block_id)
        self.outbound_trip = Trip(start_time=start_time+1.3*running_time.get_running_time(start_time,0),
                                    direction=1,
                                    block_id=block_id)
        self.is_virtual = is_virtual
        if is_virtual==0:
            # common pattern
            self.next_arrive=self.outbound_trip.start_time+1.3*running_time.get_running_time(self.outbound_trip.start_time,1)
        else:
            # two class pattern
            self.next_arrive=self.outbound_trip.start_time+running_time.get_running_time(self.outbound_trip.start_time,1)+twoclass().two_class_time
    def to_array(self):
        """
        它需要一个行程列表，并返回一个行程列表，其中每个行程都是一个停靠点列表，其中每个停靠点都是该停靠点属性的列表
        :return: 出入境行程、行程是否虚拟、下一次到达时间。
        """
        return [self.inbound_trip.to_array(),self.outbound_trip.to_array(),self.is_virtual,self.next_arrive]

class TripPairList:
    def __init__(self,start_time=[360]) -> None:
        """
        该函数接收开始时间列表并生成包含开始时间和区块编号的行程对列表
        
        :param start_time: 块中第一次行程的时间
        """
        # generate a list of trip pairs with start_time and block_num
        self.trip_pair_list = []
        for i in range(len(start_time)):
            try:
                self.trip_pair_list.append(TripPair(start_time=start_time[i],block_id=i))
            except:
                self.trip_pair_list.append(TripPair(start_time=start_time[-1],block_id=i))
    
    def insert_virtual_trip_pair(self,index=-1):
        """
        它在列表的索引处插入一个新的行程对，然后在插入的行程对之后递增所有行程对的block_id
        
        :param index: 要插入的旅行对的索引
        :return: 返回列表中的最后一个旅行对。
        """
        # insert a new trip pair at the index of the list
        virtual_trip_pair = TripPair(self.trip_pair_list[index].inbound_trip.start_time,
                                    self.trip_pair_list[index].inbound_trip.block_id,
                                    is_virtual=1,)
        self.trip_pair_list.insert(index,virtual_trip_pair)
        for i in range(index+1,len(self.trip_pair_list)):
            self.trip_pair_list[i].inbound_trip.block_id+=1
            self.trip_pair_list[i].outbound_trip.block_id+=1
        return self.trip_pair_list.pop()
    
    def get_main_last_trip(self):
        """
        > 函数返回主线中的最后一趟
        :return: 主线的最后一趟。
        """
        # get the last trip in the main line
        for i in range(len(self.trip_pair_list)-1,-1,-1):
            if self.trip_pair_list[i].is_virtual!=1:
                break
        return self.trip_pair_list[i].inbound_trip
    
    def modified_headway(self,flag='positive',direction=1,headway=Headway()):
        """
        该函数接受旅行对列表和车头时距对象。然后它遍历旅行对，对于每个旅行对，它检查旅行对是否是虚拟的。如果不是虚拟的，则将旅行对的开始时间调整 5 分钟，并相应地调整车头时距对象。
        
        该函数返回一个生成器对象，它是一个行程对列表和一个车头时距对象。
        
        该函数按以下方式使用：
        
        :param flag: “正面”或“负面”, defaults to positive (optional)
        :param direction: -1 入站，1 出站, defaults to 1 (optional)
        :param headway: 前进目标
        """
        # modified the headway of the trip pairs
        # direction show the direction of the trip pairs
        for j in range(len(self.trip_pair_list)-1):
            if flag=='positive':
                if direction==-1:
                    for i in range(len(self.trip_pair_list)-1):
                        if self.trip_pair_list[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_list[i]=TripPair(self.trip_pair_list[i].inbound_trip.start_time+5,
                                                            self.trip_pair_list[i].inbound_trip.block_id,
                                                            is_virtual=0)
                            headway.adjust(self.trip_pair_list[i].inbound_trip.start_time,0,5)
                        yield self.trip_pair_list,headway
                    break
                else:
                    for i in range(len(self.trip_pair_list)-1,j-1,-1):
                        if self.trip_pair_list[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_list[i]=TripPair(self.trip_pair_list[i].inbound_trip.start_time+5,
                                                            self.trip_pair_list[i].inbound_trip.block_id,
                                                            is_virtual=0)
                            headway.adjust(self.trip_pair_list[i].inbound_trip.start_time,0,5)
                        yield self.trip_pair_list,headway   
                    break
            elif flag=='negative':
                if direction==-1:
                    for i in range(len(self.trip_pair_list)-1):
                        if self.trip_pair_list[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_list[i]=TripPair(self.trip_pair_list[i].inbound_trip.start_time-5,
                                                            self.trip_pair_list[i].inbound_trip.block_id,
                                                            is_virtual=0)
                            headway.adjust(self.trip_pair_list[i].inbound_trip.start_time,0,-5)
                        yield self.trip_pair_list,headway
                else:
                    for i in range(len(self.trip_pair_list)-1,j-1,-1):
                        if self.trip_pair_list[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_list[i]=TripPair(self.trip_pair_list[i].inbound_trip.start_time-5,
                                                            self.trip_pair_list[i].inbound_trip.block_id,
                                                            is_virtual=0)
                            headway.adjust(self.trip_pair_list[i].inbound_trip.start_time,0,-5)
                        yield self.trip_pair_list,headway
                    break
        
    def to_array(self):
        # return a list of trip pairs
        return [self.trip_pair_list[i].to_array() for i in range(len(self.trip_pair_list))]

class Timetable:
    def __init__(self,n_main,fisrt_trip_time) -> None:
        self.group_list=[
            # TripPairList1, TripPairList2, TripPairList3, ...
        ]
        self.block_num = n_main 
        self.first_trip_time = fisrt_trip_time
        self.meal_time=20
        self.meal_flag=[1 for _ in range(self.block_num)]
        self.block_mode_status=[0 for _ in range(self.block_num)]
        self.block_mode_buffer=[]
        self.block_two_class_status=[0 for _ in range(self.block_num)]
    
    def init_trip_pair_group(self):
        """
        它创建第一个旅行对组。
        """
        """
        它创建第一个旅行对组。
        """
        # init the first trip pair group
        # return the first trip pair group
        print('===          ^^^^^^^^^^^^^^^^^^^^^^^^^^^         ====')
        print('===          step1: init trip pair group         ====')
        print('===          ^^^^^^^^^^^^^^^^^^^^^^^^^^^         ====')
        timelist = [self.first_trip_time]
        for i in range(self.block_num-1):
            timelist.append(timelist[-1]+Headway().get_headway(timelist[-1],0))
        first_trip_pair_list = TripPairList(timelist)
        # todo: modify the first_trip_pair_list with change the headway
        self.group_list.append(first_trip_pair_list)
    
    def generate_trip_pair_group(self,headwaytime=360,headway=Headway()):
        """
        它根据发车间隔时间生成行程对列表。
        
        :param headwaytime: 第一班车和第二班车之间的时间, defaults to 360 (optional)
        :param headway: 两次连续行程之间的间隔时间
        :return: 行程对列表。
        """
        print('===          ^^^^^^^^^^^^^^^^^^^^^^^^^^^         ====')
        print('===          step3: generate trip pair group     ====')
        print('===          ^^^^^^^^^^^^^^^^^^^^^^^^^^^         ====')
        # grouplist cannot be empty
        if len(self.group_list)==0:
            print("Error: group list is empty")
            return
        # generate two new trip pair groups:headway and running time
        headway_time_list=[]
        for i in range(self.block_num):
            headwaytime+=headway.get_headway(headwaytime,0)
            headway_time_list.append(headwaytime)
        headway_trip_pair_list = TripPairList(headway_time_list)
        return headway_trip_pair_list
    
    def search_trip_pair_group(self):
        """
        > 函数`search_trip_pair_group`用于搜索下一个旅行对组
        """
        print('===          ^^^^^^^^^^^^^^^^^^^^^^^^^^^         ====')
        print('===          step2: search trip pair group       ====')
        print('===          ^^^^^^^^^^^^^^^^^^^^^^^^^^^         ====')
        current_trip_pair_group = self.group_list[-1]
        # generate the headway group
        headwaytime=current_trip_pair_group.get_main_last_trip().start_time
        headwayTripPairGroup= self.generate_trip_pair_group(headwaytime)
        # some rule to search the trip pair group
        mark,group=self.generate_feasible_trip_pair_group(headwayTripPairGroup)
        if mark==0:
            self.group_list.append(group)
        else:
            raise Exception("Error: cannot find the feasible trip pair group")
    
    def generate_feasible_trip_pair_group(self,headwayTripPairGroup):
        """
        上述函数用于生成一个可行的行程对组。
        
        :param headwayTripPairGroup: 我们要从中生成可行旅行对组的旅行对组
        :return: 可行的旅行对组。
        """
        # generate a feasible trip pair group
        # return the feasible trip pair group
        print('the initial headway group is:',headwayTripPairGroup.to_array())
        mark=self.rule_layovertime(headwayTripPairGroup)
        max_num=2
        while mark!=0 and max_num>0:
            # max_num is used to avoid the infinite loop
            import copy
            print(mark)
            backup=copy.deepcopy(self.group_list[-1])
            headwayTripPairGroup=self.operate_trip_pair_group(headwayTripPairGroup,mark)
            mark=self.rule_layovertime(headwayTripPairGroup)
            max_num-=1
        print('there is still some problem',mark)
        print('the last trip pair group is',self.group_list[-1].to_array())
        print('the headway trip pair group is',headwayTripPairGroup.to_array())
        print('layover time is',self._cal_layover_time_diff(headwayTripPairGroup.trip_pair_list))
        return 0,headwayTripPairGroup


    def operate_trip_pair_group(self,headwayTripPairGroup,init_flag=0,headway=Headway()):
        print('===          ^^^^^^^^^^^^^^^^^^^^^^^^^^^         ====')
        print('===          step4: operate trip pair group      ====')
        print('===          ^^^^^^^^^^^^^^^^^^^^^^^^^^^         ====')
        import copy
        headwayTripPairGroup_init=copy.deepcopy(headwayTripPairGroup)
        group_list_init=copy.deepcopy(self.group_list)
        if init_flag==0:
            # the layover time is ok
            return headwayTripPairGroup
        else:
            if init_flag==1:
                # the first trip pair group is to long
                for i in range(len(headwayTripPairGroup.trip_pair_list)):
                    if headwayTripPairGroup.trip_pair_list[i].is_virtual==1:
                        continue
                    else:
                        headwayTripPairGroup.trip_pair_list[i].inbound_trip.start_time-=5
                        if self.rule_layovertime(headwayTripPairGroup)!=1 and self.rule_basic():
                            return headwayTripPairGroup
                for modfied_trip_pair,modified_headway in self.group_list[-1].modified_headway('negative'):
                    headway=modified_headway
                    headwayTripPairGroup=self.generate_trip_pair_group(self.group_list[-1].get_main_last_trip().start_time,headway)
                    if self.rule_layovertime(headwayTripPairGroup)!=1:
                        return headwayTripPairGroup

            if init_flag==2:
                # the layover time is too long
                # insert the virtual trip pair
                import copy
                # two class is priority
                while self.block_mode_buffer:
                    self.group_list[-1].insert_virtual_trip_pair(self.block_mode_buffer.pop())
                    headwayTripPairGroup=self.generate_trip_pair_group(self.group_list[-1].get_main_last_trip().start_time,headway)
                    if self.rule_layovertime(headwayTripPairGroup)!=2 and self.rule_layovertime(headwayTripPairGroup)<12 and self.rule_basic():
                        return headwayTripPairGroup
                
                for i in range(len(headwayTripPairGroup.trip_pair_list)):
                    # 对headway trip pair group insert virtual trip pair
                    if self.block_two_class_status[i]>0 and self.block_two_class_status[i]//2==0:
                        self.block_two_class_status[i]-=1
                        continue
                    headwayTripPairGroup.insert_virtual_trip_pair(i)
                    self.block_mode_buffer.append(i)
                    self.block_mode_status[i]=1
                    if self.rule_layovertime(headwayTripPairGroup)!=2 and self.rule_layovertime(headwayTripPairGroup)<12 and self.rule_basic():
                        self.block_two_class_status[i]+=1
                        return headwayTripPairGroup
                    self.block_mode_status[i]=0
                    self.block_mode_buffer.pop()
                    headwayTripPairGroup=headwayTripPairGroup_init


                for i in range(len(headwayTripPairGroup.trip_pair_list)-1,-1,-1):
                    if self.block_two_class_status[i]>0 and self.block_two_class_status[i]//2==0:
                        self.block_two_class_status[i]-=1
                        continue
                    self.group_list[-1].insert_virtual_trip_pair(i)
                    self.block_mode_buffer.append(i)
                    self.block_mode_status[i]=1
                    headwayTripPairGroup=self.generate_trip_pair_group(self.group_list[-1].get_main_last_trip().start_time)
                    if self.rule_layovertime(headwayTripPairGroup)!=2 and self.rule_layovertime(headwayTripPairGroup)<12 and self.rule_basic():
                        self.block_two_class_status[i]+=1
                        return headwayTripPairGroup
                    self.block_mode_status[i]=0
                    self.block_mode_buffer.pop()
                    self.group_list=group_list_init
                    # insert the virtual trip pair is over
            
            if init_flag==9:
                for i in range(len(headwayTripPairGroup.trip_pair_list)):
                    # 对headway trip pair group insert virtual trip pair
                    if self.block_two_class_status[i]>0 and self.block_two_class_status[i]//2==0:
                        self.block_two_class_status[i]-=1
                        continue
                    headwayTripPairGroup.insert_virtual_trip_pair(i)
                    self.block_mode_buffer.append(i)
                    self.block_mode_status[i]=1
                    if self.rule_layovertime(headwayTripPairGroup)!=2 and self.rule_layovertime(headwayTripPairGroup)<12 and self.rule_basic():
                        self.block_two_class_status[i]+=1
                        return headwayTripPairGroup
                    self.block_mode_status[i]=0
                    self.block_mode_buffer.pop()
                    headwayTripPairGroup=headwayTripPairGroup_init

            if init_flag==-1:
                # the layover time is short
                # modified the headway
                pass
            if init_flag==10:
                for modfied_trip_pair,modified_headway in headwayTripPairGroup.modified_headway('negative'):
                    headway=modified_headway
                    headwayTripPairGroup=self.generate_trip_pair_group(self.group_list[-1].get_main_last_trip().start_time,headway)
                    if self.rule_layovertime(headwayTripPairGroup)!=10 and self.rule_basic():
                        return headwayTripPairGroup
            
            if init_flag>10 and init_flag%2!=0:
                # the layover time is short
                # modified the headway
                index=init_flag//10-1
                for i in range(len(headwayTripPairGroup.trip_pair_list)):
                    if i<index:
                        continue
                    else:
                        headwayTripPairGroup.trip_pair_list[i].inbound_trip.start_time+=5
                        if self.rule_layovertime(headwayTripPairGroup)!=10 and self.rule_basic():
                            return headwayTripPairGroup
                for modfied_trip_pair,modified_headway in headwayTripPairGroup.modified_headway('positive',-1):
                    headway=modified_headway
                    headwayTripPairGroup=self.generate_trip_pair_group(self.group_list[-1].get_main_last_trip().start_time,headway)
                    if self.rule_layovertime(headwayTripPairGroup)!=10 and self.rule_basic():
                        return headwayTripPairGroup
                return headwayTripPairGroup
                
            
            if init_flag>10 and init_flag%2==0:
                index=init_flag//10-1
                self.block_mode_buffer.append(index)
                headwayTripPairGroup[-1].insert_virtual_trip_pair(index)
                self.block_mode_status[i]=1
                if self.rule_layovertime(headwayTripPairGroup)!=2 and self.rule_layovertime(headwayTripPairGroup)!=-10 and self.rule_basic():
                    return headwayTripPairGroup
                self.block_mode_buffer.pop()
                self.block_mode_status[i]=0
                i=len(headwayTripPairGroup.trip_pair_list)-1
                for i in range(len(headwayTripPairGroup.trip_pair_list)-1,-1,-1):
                    self.block_mode_buffer.append(i)
                    headwayTripPairGroup=self.generate_trip_pair_group(self.group_list[-1].get_main_last_trip().start_time)
                    headwayTripPairGroup[-1].insert_virtual_trip_pair(i)
                    self.block_mode_status[i]=1
                    if self.rule_layovertime(headwayTripPairGroup)!=2 and self.rule_layovertime(headwayTripPairGroup)!=-10 and self.rule_basic():
                        return headwayTripPairGroup
                    self.block_mode_status[i]=0
                    self.block_mode_buffer.pop()
                    # insert the virtual trip pair is over
                    i-=1       
        print('most warning case')
        print('no way to find the solution')
        return headwayTripPairGroup_init
    
    
    def rule_layovertime(self,headwayTripPairGroup):
        # rule: layover time
        layover_time_diff=self._cal_layover_time_diff(headwayTripPairGroup.trip_pair_list)
        res=0

        if layover_time_diff[0]>10:
            # modify the headway(negative)
            if layover_time_diff[0]>5*self.block_num:
                # insert a virtual trip pair
                return 2
            return 1
        elif layover_time_diff[0]<-10:
            # *|MARKER_CURSOR|*
            # modify the headway(positive)
            return -1
        for i in range(1,len(layover_time_diff)):
            print('layover time is:',layover_time_diff[i])
            if self.block_mode_status[i]==1:
                continue
            elif layover_time_diff[i]>10:
                # modify the headway(negative) for headway pair
                if max(layover_time_diff)>5*self.block_num:
                    # insert a virtual trip pair
                    res=10
                res=10
            elif layover_time_diff[i]<-10:
                # modify the headway(positive) for headway pair
                res=i*10+11
            elif layover_time_diff[i]<-5*self.block_num:
                res=i*10+12
        return res
    
    def rule_basic(self):
        # rule: basic
        # rule: 确保可以生成一个正常的时刻表，不会出现start-time拥挤的情况
        timetable_array=self.to_timetable_array()
        for block_id in range(len(timetable_array)):
            for i in range(len(timetable_array[block_id])-1):
                if timetable_array[block_id][i+1][0]-timetable_array[block_id][i][0]<RunningTime().get_running_time(timetable_array[block_id][i][0],timetable_array[block_id][i][1]):
                    print('basic rule is broken')
                    print(timetable_array[block_id][i+1][0]-timetable_array[block_id][i][0])
                    print(timetable_array)
                    return False
        return True

    
    def _cal_layover_time_diff(self,trip_pair_list):
        # calculate the layover time of the trip pair list
        # attention the trip pair may be two class
        # attention the trip pair may be the first init trip pair
        # attention the layover time may be more than 20min when the lunch meal windows [10,13]
        # attention the two class trip pair can be insert in some way 
        # quesntion: two class is use to affect the next_arrive time in the trip pair list or affect the layover time calculation
        layover_time=[]
        buffer=0
        for i in range(len(trip_pair_list)):
            if trip_pair_list[i].inbound_trip.start_time>=600 and trip_pair_list[i].inbound_trip.start_time<=780:
                # eat time
                if self.meal_flag[trip_pair_list[i].inbound_trip.block_id]==1:
                    # eat time and meal_flag=1
                    buffer=-20
                    self.meal_flag[trip_pair_list[i].inbound_trip.block_id]=0
            layover_time.append(trip_pair_list[i].inbound_trip.start_time-self._get_block_lasted_arrive(i)+buffer)
        return layover_time

    def _get_block_lasted_arrive(self,block_id):
        # get the lasted trip in the block
        # return the lasted trip
        for i in range(len(self.group_list)-1,-1,-1):
            if self.group_list[i].trip_pair_list[block_id].is_virtual!=1:
                return self.group_list[i].trip_pair_list[block_id].next_arrive
        return 0

    def to_timetable_array(self):
        # convert the timetable to array
        # return the array
        timetable_array = []
        for i in range(len(self.group_list)):
            for j in range(len(self.group_list[i].trip_pair_list)):
                if len(timetable_array)<=j:
                    timetable_array.append([])
                if self.group_list[i].trip_pair_list[j].is_virtual==1:
                    print(self.group_list[i].trip_pair_list[j].to_array())
                else:
                    timetable_array[j].append(self.group_list[i].trip_pair_list[j].inbound_trip.to_array())
                    timetable_array[j].append(self.group_list[i].trip_pair_list[j].outbound_trip.to_array())
        return timetable_array
    
    def visualize(self,timetable_array,title='timetable'):
        import matplotlib.pyplot as plt
        max_index = 0
        for index in timetable_array:
            for bus in index:
                c = ['b', 'r']
                plt.hlines(y=bus[2], xmin=bus[0], xmax=bus[0] + RunningTime().get_running_time(bus[0], bus[1]), colors=c[bus[1]])
                max_index = max(max_index, bus[2])
        plt.yticks(list(range(1, max_index + 1)))
        plt.title(title)
        plt.show()
    
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
                    if ((index_start_time[i + 1] - index_start_time[i]) - RunningTime().get_running_time(index_start_time[i],1)) > TWO_CLASS_DIFF:
                        delet_time = delet_time + ((index_start_time[i + 1] - index_start_time[i]) - RunningTime().get_running_time(index_start_time[i], 0))
            class_pattern.append(delet_time)

        start_time_up = sorted(start_time_up)
        start_time_down = sorted(start_time_down)

        # 01--计算三个对应的指标，包括行休比例、工作时间、车行公里数
        for index_bus in timetable_array:
            start_work = 1440
            end_work = 0
            runwaytime = 0  # 在车上的时间
            for class_bus in index_bus:
                runwaytime = runwaytime + RunningTime().get_running_time(class_bus[0],
                                                        class_bus[1])  # 计算工作时间。行程时间累加
                start_work = min(start_work, class_bus[0])
                end_work = max(end_work, class_bus[0] + RunningTime().get_running_time(class_bus[0],
                                                        class_bus[1]))  # 计算工作时间。行程时间累加
            runway_time.append(runwaytime)  # 仅仅包括行程时间，在车上面的时间
            inwork_time.append(end_work - start_work)  # 车辆在站内的时间，还没去掉两头班的两个小时
            runway.append(len(index_bus) * DISTANCE_BUS)

        work_time = [inwork_time[i] - class_pattern[i] for i in range(len(class_pattern))]  # 站内时间 减去 两头班的时间存在的时间

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
                    bus_index[i + 1][0] - bus_index[i][0] - RunningTime().get_running_time(bus_index[i][0], bus_index[i][1]))
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
    
    def get_benchmark_work_time(self,work_time):
        # 计算对应的work_time的均值和标准差
        work_time=self.evaluate(self.to_timetable_array())
        wk=[]
        for wt in work_time:
            if wt>600:
                wk.append(wt)
        import numpy as np
        benckmark_work_time = np.mean(wk)
        return benckmark_work_time
    
# init the timetable
timetable = Timetable(4,360)
timetable.init_trip_pair_group()
timetable_array = timetable.to_timetable_array()
print(timetable.group_list[-1].to_array())
while timetable.group_list[-1].trip_pair_list[-1].outbound_trip.start_time<1240:
    print('\n')
    print('\n')
    timetable.search_trip_pair_group()
    timetable.visualize(timetable.to_timetable_array())

# delete the last group
for trip_pair in timetable.group_list[-1].trip_pair_list:
    if trip_pair.outbound_trip.start_time>1240:
        trip_pair.is_valid = True

# # blance the work time
# benchmark_work_time = timetable.get_benchmark_work_time(timetable.evaluate(timetable.to_timetable_array()))
# while max(timetable.evaluate(timetable.to_timetable_array()))>benchmark_work_time:
#     timetable.group_list.pop()


# while timetable.group_list[-1].trip_pair_list[-1].outbound_trip.start_time<1240:
#     print('\n')
#     print('\n')
#     timetable.search_trip_pair_group()

timetable_array = timetable.to_timetable_array()
print(timetable.evaluate(timetable_array,0))
print(timetable_array)
timetable.visualize(timetable_array)
