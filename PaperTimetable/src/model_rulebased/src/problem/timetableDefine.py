
import sys
# from deprecated.sphinx import deprecated
sys.path.append('/home/step/data/xcl/JDBUSgroup/modelTimetable/timetabe_if_then/src')

class stepFormatTime:
    def __init__(self):
        self.time=[]
        self.point=[]
    
    def get_moment_direction(self,moment,direction):
        """ 取阶梯形状的时间点
        
        Args:
        moment : 时间点
        direction : 方向，0代表上行、1代表下行

        Return:
        返回对应的时间点
        """
        try:
            for i in range(len(self.point[direction])):
                if moment<=self.point[direction][i]:
                    return self.time[direction][i-1]
        except:

            raise ('Step time error!')


# TODO: 2023-01-12区分哪些是类的操作，哪些是可以移植的操作
class Trip:
    def __init__(self,start_time=0,direction=0,block_id=0) -> None:
        """   初始化车次
        start_time: 车次发车时间
        direction: 车次行驶方向
        block_id: 车次所在区间
        """
        self.start_time = start_time
        self.direction = direction 
        self.block_id = block_id

    def to_array(self):
        """ 将车次转化为数组
        """
        return [self.start_time,self.direction,self.block_id]

class TripPair:
    def __init__(self,start_time=0,block_id=0,is_virtual=False,running_time=stepFormatTime()) -> None:
        """
        初始化车次对
        start_time: 车次对发车时间
        block_id: 车次对所对应路牌
        is_virtual: BOOL车次对是否为虚拟车次对
        running_time: 运行时间类
        """
        self._interval=5         # 理论最短运行时间
        self.running_time=running_time
        self.inbound_trip = Trip(start_time,0,block_id)

        outbound_start_time=start_time+self._interval+running_time.get_moment_direction(start_time,0)
        self.outbound_trip = Trip(outbound_start_time,1,block_id)

        self.is_virtual = is_virtual
    
    def next_feasible_trip_pair(self):
        """ 返回下一个可行的车次对
        """
        t1=self.running_time.get_moment_direction(self.inbound_trip.start_time,self.inbound_trip.direction)
        t2=self.running_time.get_moment_direction(self.outbound_trip.start_time,self.outbound_trip.direction)

        st=self.inbound_trip.start_time+(t1+t2)+2*self._interval
        bi=self.inbound_trip.block_id
        rt=self.running_time
        res=TripPair(start_time=st,block_id=bi,running_time=rt)
        return res
    
    def next_optimal_trip_pair(self):
        """ 返回下一个最优的车次对
        """
        t1=self.running_time.get_moment_direction(self.inbound_trip.start_time,self.inbound_trip.direction)
        t2=self.running_time.get_moment_direction(self.outbound_trip.start_time,self.outbound_trip.direction)

        st=self.inbound_trip.start_time+1.3*(t1+t2)
        bi=self.inbound_trip.block_id
        rt=self.running_time
        res=TripPair(start_time=st,block_id=bi,running_time=rt)
        return res

    def to_array(self):
        return [self.inbound_trip.to_array(),self.outbound_trip.to_array(),self.is_virtual,self.next_optimal_trip_pair().inbound_trip.start_time]

class TripPairGroup:
    def __init__(self,start_time=[],running_time=stepFormatTime()) -> None:
        """ 初始化车次对组
        start_time: 车次对组发车时间
        running_time: 运行时间类
        """
        self.running_time=running_time
        self.trips=[]

        for i in range(len(start_time)):
            # 根据运营时间的新建 trip pair
            self.trips.append(TripPair(start_time=start_time[i],block_id=i,running_time=self.running_time))
    
    def insert_virtual_trip_pair(self,index=-1):
        """ 插入虚拟车次对
        """
        if index==-1:
            index=len(self.trips)-1
        virtual_trip_pair = TripPair(
                                        self.trips[index].inbound_trip.start_time,
                                        self.trips[index].inbound_trip.block_id,
                                        True,
                                        self.running_time
                                    )
        self.trips.insert(index,virtual_trip_pair)

        for i in range(index+1,len(self.trips)):
            # 更新block id
            self.trips[i].inbound_trip.block_id+=1
            self.trips[i].outbound_trip.block_id+=1
        return self.trips.pop()

    def insert_search(self,trip_pair_group,priority=[],bid=[]):
        """
        返回调整的trip pair group的headway
        可能会用到的有timetable中不同block的优先级
        """
        import copy
        result=[]
        chociest=[p for p in priority]
        for i in range(len(trip_pair_group.trips)):
            if i in priority:
                continue
            else:
                chociest.append(i)
        newchociest=copy.deepcopy(chociest)
        for i in range(len(newchociest)):
            # 删除不匹配的结果
            if newchociest[i] in bid:
                chociest.remove(newchociest[i])
        for i in chociest:
            res=copy.deepcopy(trip_pair_group)
            res.insert_virtual_trip_pair(i)
            result.append(res)
        return result

    def headway_search(self,trip_pair_group,running_time=stepFormatTime(),flag='positive'):
        """
        返回调整trip pair group的headway
        返回迭代器生成的结果
        """
        res=[]
        for j in range(1,len(trip_pair_group.trips)-1):
            if flag=='positive':
                for i in range(j,len(trip_pair_group.trips)):
                    if trip_pair_group.trips[i].is_virtual==True:
                        continue
                    else:
                        trip_pair_group.trips[i]=TripPair(trip_pair_group.trips[i].inbound_trip.start_time+5,
                                                        trip_pair_group.trips[i].inbound_trip.block_id,
                                                        is_virtual=False,
                                                        running_time=running_time)
                    yield trip_pair_group
            elif flag=='negative':
                for i in range(j,len(trip_pair_group.trips)):
                    if trip_pair_group.trips[i].is_virtual==True:
                        continue
                    else:
                        trip_pair_group.trips[i]=TripPair(trip_pair_group.trips[i].inbound_trip.start_time-5,
                                                        trip_pair_group.trips[i].inbound_trip.block_id,
                                                        is_virtual=False,
                                                        running_time=running_time)
                    yield trip_pair_group
            else:
                print("Error: flag must be positive or negative")

    def get_lasted_time(self):
        """
        返回车次对组的结束时间
        """
        for i in range(len(self.trips)-1,-1,-1):
            if self.trips[i].is_virtual==False:
                return self.trips[i].inbound_trip.start_time
        raise Exception('该班次对组均为虚拟班次')

    def get_lasted_virtual_index(self):
        """
        返回虚拟车次对的索引
        """
        for i in range(len(self.trips)):
            if self.trips[i].is_virtual==True:
                return self.trips[i].inbound_trip.block_id

    def to_array(self):
        """
        转换为数组
        """
        res=[]
        for i in range(len(self.trips)):
            res.append(self.trips[i].to_array())
        return res


class Timetable:
    def __init__(self) -> None:
        """ 初始化时刻表
        n_main: 主线车次对数量
        n_aid: 辅线车次对数量
        first_trip_time: 首班车发车时间
        end_trip_time: 末班车发车时间
        headway: 车头间隔类
        """
        self.groups=[
            # TripPairList1,...
        ]
        # 总体的路牌数量
        self.n_main=0
        self.n_aid=0
        self.block_num=self.n_main+self.n_aid
        # 首班车发车时间
        self.first_trip_time=360
        # 末班车发车时间
        self.end_trip_time=1440
        # 允许的吃饭时间
        self.meal_time=20
        # 两头班的优先级
        self.block_mode_buffer=[]
        # 时刻表的发车间隔
        self.headway=stepFormatTime()
        self.running_time=stepFormatTime()

    def Init_trip_pair_group(self):
        """ 返回可行的首班车初始化的结果
        """
        # 按照发车间隔生成车次对组
        import copy
        temp_start_time_list=[self.first_trip_time]
        for i in range(self.block_num-1):
            temp_start_time_list.append(temp_start_time_list[-1]+self.headway.get_moment_direction(temp_start_time_list[-1],0))
        init_trip_pair_group=TripPairGroup(start_time=temp_start_time_list,running_time=self.running_time)

        # 插空班次生成车次对组
        res1=[init_trip_pair_group]
        for i in TripPairGroup().insert_search(init_trip_pair_group):
            res1.append(i)

        # 对insert search的结果进行headway search，得到所有可能的车次对组
        res2=[]
        for trip_pair_group in res1:
            res2.append(copy.deepcopy(trip_pair_group))
            temp_trip_pair_group=copy.deepcopy(trip_pair_group)
            for j in TripPairGroup().headway_search(trip_pair_group,running_time=self.running_time,flag='positive'):
                temp=copy.deepcopy(j)
                res2.append(temp)
            for j in TripPairGroup().headway_search(temp_trip_pair_group,running_time=self.running_time,flag='negative'):
                temp=copy.deepcopy(j)
                res2.append(temp)
        return res2

    # def Operate_last_trip_pair_group(self,flag):
    #     """ 对上一个班次对组进行操作
    #     # TODO 调整逻辑
    #     """
    #     self.groups[-1].Operate_trip_pair_group(flag)
    
    def mark_layover_time(self,trip_pair_group,meal_flag):
        """ 计算休息时间来判断是否需要进行搜索

        trip_pair_group: 待匹配的车次对组
        meal_flag: 路牌吃饭的标记位
        """
        mark=0
        index=-1
        layover_time_diff,new_meal_flag=self._cal_layover_time(trip_pair_group=trip_pair_group,meal_flag=meal_flag)
        for i in range(len(layover_time_diff)):
            if trip_pair_group.trips[i].is_virtual==False:
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
        for i in range(len(trip_pair_group.trips)):
            if trip_pair_group.trips[i].inbound_trip.start_time>=600 and trip_pair_group.trips[i].inbound_trip.start_time<=780:
                # eat time
                if meal_flag[trip_pair_group.trips[i].inbound_trip.block_id]==1:
                    # eat time and meal_flag=1
                    buffer=-20
                    meal_flag[trip_pair_group.trips[i].inbound_trip.block_id]=0
            if self._get_block_lasted_arrive(i)==0:
                layover_time.append(0)
            else:
                layover_time.append(trip_pair_group.trips[i].inbound_trip.start_time-self._get_block_lasted_arrive(i)+buffer)
        return layover_time,meal_flag

    def _get_block_lasted_arrive(self,block_id):
        """
        获取路牌上一班车的到达时间
        """
        for i in range(len(self.groups)-1,-1,-1):
            if self.groups[i].trips[block_id].is_virtual!=1:
                # 2023-01-15 这里的trips的running time是有的
                return self.groups[i].trips[block_id].next_optimal_trip_pair().inbound_trip.start_time
        return 0

    def rule_basic(self,trip_pair_group,meal_flag):
        """
        基本规则
        """
        pass
    
    def to_timetable_array(self):
        # convert the timetable to array
        # return the array
        timetable_array = []
        for i in range(len(self.groups)):
            for j in range(len(self.groups[i].trips)):
                if len(timetable_array)<=j:
                    timetable_array.append([])
                if self.groups[i].trips[j].is_virtual==True:
                    pass
                else:
                    timetable_array[j].append(self.groups[i].trips[j].inbound_trip.to_array())
                    timetable_array[j].append(self.groups[i].trips[j].outbound_trip.to_array())
        return timetable_array

    def to_array(self):
        for i in range(len(self.groups)):
            print(self.groups[i].to_array())

    
    def get_end_time(self):
        if self.groups==[]:
            return 0
        else:
            try:
                return self.groups[-1].get_lasted_time()
            except:
                return self.groups[-2].get_lasted_time()

    def _headway_cal(self):
        # 计算上行和下行的发车时间间隔
        upstream_st=[]
        downstream_st=[]
        for i in range(len(self.groups)):
            for j in range(len(self.groups[i].trips)):
                if self.groups[i].trips[j].is_virtual==False:
                    upstream_st.append(self.groups[i].trips[j].inbound_trip.start_time)
                    downstream_st.append(self.groups[i].trips[j].outbound_trip.start_time)
        upstream_st.sort()
        downstream_st.sort()
        upstream_headway=[]
        downstream_headway=[]
        for i in range(len(upstream_st)-1):
            upstream_headway.append(upstream_st[i+1]-upstream_st[i])
        for i in range(len(downstream_st)-1):
            downstream_headway.append(downstream_st[i+1]-downstream_st[i])
        return [upstream_headway,downstream_headway]
        
    def find_priority(self):
        """  路牌分班优先级
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
        """  路牌分班禁止集合
        """
        bid=[]
        if self.get_end_time()<800:
            for i in range(self.block_num):
                if self.block_mode_status[i]==2:
                    bid.append(i)
        return bid

