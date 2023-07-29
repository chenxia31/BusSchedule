from timetableDefine import Trip,TripPair,TripPairGroup,stepFormatTime,Timetable
import sys
sys.path.append('PaperTimetable/src/model_rulebased/src')
from util.timetableview import timetableVisualize,timetableEvaluation

class Headway(stepFormatTime):
    def __init__(self,time,point):
        super().__init__()
        self.time=time
        self.point=point
    
    def adjust(self,moment,direction,adjustment):
        """ 它在给定的时刻及时调整车头时距

        Args:
        moment: 以分钟为单位的时间
        direction: 0为下行,1为上行
        adjustment: 车头时距增加或减少的时间量
        """
        try:
            for i in range(len(self.point[direction])):
                if moment<=self.point[direction][i]:
                    if self.time[direction][i]+adjustment>=15 and self.time[direction][i]+adjustment<=35:
                        self.time[direction][i]+=adjustment
                        return self.time[direction][i-1]
        except:
            raise ("Error: headway not found")

class Running_time(stepFormatTime):
    def __init__(self,time,point):
        super().__init__()
        self.time=time
        self.point=point

class timetableBacktraking(Timetable):
    def __init__(self,n_main,n_aid,first_trip,end_trip,headway,running_time) -> None:
        super().__init__()
        self.n_main=n_main
        self.n_aid=n_aid
        self.block_num=self.n_main+self.n_aid
        self.first_trip_time=first_trip
        self.end_trip_time=end_trip
        self.headway=headway
        self.running_time=running_time
        # 路牌吃饭的标记位
        self.meal_flag=[1 for _ in range(self.block_num)]
        # 路牌的班式标志
        self.block_mode=[0 for _ in range(self.block_num)]
        self.block_mode_status=[0 for _ in range(self.block_num)]
    
    def Search_trip_pair_group(self,lasted_trip_pair_group):
        """ 寻找下一个可行的班次对
        """
        # 根据headway生成下一个班次对组
        # temp_trip_pair_group 就是下一个班次对组
        temp_start_time=lasted_trip_pair_group.get_lasted_time()
        temp_start_time_list=[]
        for i in range(self.block_num):
            temp_start_time+=self.headway.get_moment_direction(temp_start_time,0)
            temp_start_time_list.append(temp_start_time)
        temp_trip_pair_group=TripPairGroup(start_time=temp_start_time_list,running_time=self.running_time)

        mark=True
        
        # 基于规则找到当前的最优的分支
        if lasted_trip_pair_group.get_lasted_time()>=660 and lasted_trip_pair_group.get_lasted_time()<=900:
            # 平峰时间不会改变headway
            group=temp_trip_pair_group
        else:
            # 非平峰时间会改变headway
            mark,group=self.Gen_feasible_trip_pair_group(temp_trip_pair_group)
        res=[group]

        # 增加分支的可能性
        import copy
        for i in range(self.block_num):
            temp=copy.deepcopy(group)
            temp.insert_virtual_trip_pair(index=i)
            res.append(temp)
        if mark:
            return res
        else:
            return []

    def Gen_feasible_trip_pair_group(self,trip_pair_group):
        """  生成可行的班次对
        """
        # 根据休息时间调整
        list=[]
        mark,index,new_meal_flag=self.mark_layover_time(trip_pair_group,self.meal_flag)
        if mark==0:
            self.meal_flag=new_meal_flag
            return True,trip_pair_group
        elif mark==1:
            # 减小headway
            for iter_trip_pair_group in TripPairGroup().headway_search(trip_pair_group=trip_pair_group,running_time=self.running_time,flag='negative'):
                mark,index,new_meal_flag=self.mark_layover_time(iter_trip_pair_group,self.meal_flag)
                if mark:
                    self.meal_flag=new_meal_flag
                    return True,iter_trip_pair_group
        elif mark==-1:
            # 增大headway
            for iter_trip_pair_group in TripPairGroup().headway_search(trip_pair_group=trip_pair_group,running_time=self.running_time,flag='positive'):
                mark,index,new_meal_flag=self.mark_layover_time(iter_trip_pair_group,self.meal_flag)
                if mark:
                    self.meal_flag=new_meal_flag
                    return True,iter_trip_pair_group
        elif mark==2:
            # 插入新的班次
            # 每次插入新的班次需要进行新的headway的搜索
            priority=self.find_priority()
            bid=self.find_bid()
            for iter_trip_pair_group in TripPairGroup().insert_search(trip_pair_group=trip_pair_group,priority=priority,bid=bid):
                mark,index,new_meal_flag=self.mark_layover_time(iter_trip_pair_group,self.meal_flag)
                if mark==0:
                    self.meal_flag=new_meal_flag
                    return True,iter_trip_pair_group
                if mark==1:
                    # 减小headway
                    for iter_trip_pair_group2 in TripPairGroup().headway_search(trip_pair_group=iter_trip_pair_group,running_time=self.running_time,flag='negative'):
                        mark,index,new_meal_flag=self.mark_layover_time(iter_trip_pair_group2,self.meal_flag)
                        if mark:
                            self.meal_flag=new_meal_flag
                            return True,iter_trip_pair_group2
                elif mark==-1:
                    # 增大headway
                    for iter_trip_pair_group2 in TripPairGroup().headway_search(trip_pair_group=iter_trip_pair_group,running_time=self.running_time,flag='positive'):
                        mark,index,new_meal_flag=self.mark_layover_time(iter_trip_pair_group2,self.meal_flag)
                        if mark:
                            self.meal_flag=new_meal_flag
                            return True,iter_trip_pair_group2
                return True,iter_trip_pair_group
                
        
        mark=self.rule_basic(trip_pair_group,self.meal_flag)
        if mark==0:
            pass
        else:
            pass
        return False,trip_pair_group

    def insert_rule(self,trips,priority=[],bid=[]):
        """  根据优先级和禁止集合确定插入 tripPairGrpup的情况
        # TODO 可改变
        返回不同情况下的分班集合
        """
        import copy
        result=[]
        chociest=[p for p in priority]
        for i in range(len(trips.trips)):
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
            res=copy.deepcopy(trips)
            res.insert_virtual_trip_pair(i)
            result.append(res)
        return result
    
    def headway_rule(self,trips,flag='positive'):
        """
        返回调整trip pair group的headway
        返回迭代器生成的结果
        """
        res=[]
        for j in range(1,len(trips.trips)-1):
            if flag=='positive':
                for i in range(j,len(trips.trips)):
                    if trips.trips[i].is_virtual==True:
                        continue
                    else:
                        trips.trips[i]=TripPair(trips.trips[i].inbound_trip.start_time+5,
                                                        trips.trips[i].inbound_trip.block_id,
                                                        is_virtual=False,running_time=self.running_time)
                    yield trips
            elif flag=='negative':
                for i in range(j,len(trips.trips)):
                    if trips.trips[i].is_virtual==True:
                        continue
                    else:
                        trips.trips[i]=TripPair(trips.trips[i].inbound_trip.start_time-5,
                                                        trips.trips[i].inbound_trip.block_id,
                                                        is_virtual=False,running_time=self.running_time)
                    yield trips
            else:
                print("Error: flag must be positive or negative")

    def check(self,trip_pair_group):
        self.groups.append(trip_pair_group)

        # 行程时间的判断
        timetable_array=self.to_timetable_array()
        for block_id in range(len(timetable_array)):
            for i in range(len(timetable_array[block_id])-1):
                if timetable_array[block_id][i+1][0]-timetable_array[block_id][i][0]<self.running_time.get_moment_direction(timetable_array[block_id][i][0],timetable_array[block_id][i][1])+2:
                    self.groups.pop()
                    return False
        
        # 两头班的计算
        new_block_status=[0 for _ in range(self.block_num)]
        for group in self.groups:
            begin_status=0
            for tripPair in group.trips:
                if tripPair.is_virtual==False:
                    begin_status=1
                if tripPair.is_virtual==True and begin_status!=0:
                    new_block_status[tripPair.inbound_trip.block_id]+=1
        if max(new_block_status)>24:
            self.groups.pop()
            return False
        
        # 工作时间的判断
        work_time=timetableEvaluation.evaluate(self,flag=1)
        if max(work_time)>840:
            self.groups.pop()
            return False
        self.groups.pop()
        return True

    def finally_check(self):
        # 检查是否满足最终的约束条件

        # 条件1:工作时间的取值范围
        work_time=timetableEvaluation.evaluate(self,flag=1)
        if min(work_time)<360:
            # print('Error: min work time is less than 6 hours')
            return False
        if max(work_time)>840:
            # print('Error: max work time is more than 14 hours')
            return False
        
        # 条件2:工作时间均衡
        test_balance=[]
        for i in range(len(work_time)):
            if work_time[i]<540:
                test_balance.append(work_time[i]*20.83/60)
            else:
                test_balance.append(work_time[i]*15/60)  
        if max(test_balance)-min(test_balance)>30:
            # print('Error: work time is not balanced')
            return False

        if sum(test_balance)/len(work_time)>200:
            # print('Error: work time is over-load')
            return False
        
        # 条件3:连续的两头班的数目
        num_mode=[]

        for i in range(self.block_num):
            begin=0
            end=len(self.groups)-1
            # 记录两头班的数量
            temp_count=0
            # 先删除上班和下班班次
            while self.groups[begin].trips[i].is_virtual==True:
                begin+=1
            while self.groups[end].trips[i].is_virtual==True:
                end-=1
            for j in range(begin,end+1):
                if self.groups[j].trips[i].is_virtual==True:
                    temp_count+=1
                    if temp_count==1:
                        pass
                    else:
                        try:
                            if self.groups[j-1].trips[i].is_virtual==False:
                                return False
                        except:
                            raise Exception('出现了两头班连续的情况')
            num_mode.append(temp_count)
        if max(num_mode)>3:
            # print('Error: two head trips are too many')
            return False
        
        if self.get_end_time()>self.end_trip_time+5 or self.get_end_time()<self.end_trip_time-5:
            # print('Error: end time is not correct')
            return False
        
        rr=timetableEvaluation.evaluate(self,flag=2)
        if max(rr)>0.35:
            # print('Error: max rest-ratio is too large')
            return False
        return True

    