class step_time:
    def __init__(self, time=[[0],[0]], step=[[0,1440],[0,1440]]):
        self.time = time
        self.step = step
    
    def get_moment_direction(self,moment, direction):
        try:
            for i in range(len(self.step[direction])):
                if moment<self.step[direction][i]:
                    return self.time[direction][i-1]
        except:
            print("Error: step_time not found",moment,direction)
    
    def adjust(self, moment, direction,adjust):
        try:
            for i in range(len(self.step[direction])):
                if moment<self.step[direction][i]:
                    self.time[direction][i]+=adjust
                    return self.time[direction][i]
        except:
            print("Adjust Error: step_timenot found",moment,direction,adjust)

headway_time=[[30, 30, 25, 25, 25, 20, 20, 20, 25, 25, 25, 25, 30, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 20, 20,
         25, 30, 35, 35, 35, 40],
        [30, 30, 30, 30, 30, 25, 20, 20, 20, 25, 25, 25, 25, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 25, 20,
         25, 25, 35, 35, 35, 35]]
headway_step=[
        [0, 360, 390, 415, 440, 460, 480, 500, 525, 550, 575, 600, 630, 655, 680, 710, 740, 770, 800, 830, 860, 890,
         920, 945, 970, 990, 1010, 1030, 1055, 1085, 1120, 1155, 1190, 1230, 1440],
        [0, 390, 420, 450, 480, 505, 525, 545, 565, 590, 615, 640, 665, 690, 715, 745, 775, 805, 835, 865, 895, 925,
         955, 980, 1005, 1025, 1050, 1070, 1095, 1120, 1155, 1190, 1225, 1260, 1440]]

running_time=[[25, 30, 35, 40, 35, 30, 35, 30, 25], 
                    [35, 30, 35, 30, 35, 30, 25]]
running_step=[[0, 390, 415, 440, 480, 500, 990, 1030, 1085, 1440],
                  [0, 390, 420, 480, 980, 1025, 1095, 1440]]

headway=step_time(headway_time,headway_step)
running=step_time(running_time,running_step)

# print('---line 40----- test for step_time')
# print(headway.get_moment_direction(420,0))    
# print(headway.get_moment_direction(420,1))


class Trip:
    def __init__(self,start_time=1,direction=0,block_id=0) -> None:
        '''
        start_time: int, in minutes
        direction: 0 or 1
        block_id: int
        '''
        self.start_time=start_time
        self.direction=direction
        self.block_id=block_id
    
    def to_array(self):
        return [self.start_time,self.direction,self.block_id]

class TripPair:
    def __init__(self,start_time=1,block_id=0,is_virtual=False,running=step_time()) -> None:
        '''
        start_time: int, in minutes
        block_id: int
        is_virtual: bool
        running: step_time
        '''
        self.inbound=Trip(start_time,0,block_id)
        self.outbound=Trip(start_time+5+running.get_moment_direction(start_time,0),1,block_id)
        self.is_virtual=is_virtual
        self.block_id=block_id
        self.next_arrive=self.inbound.start_time+1.3*running.get_moment_direction(self.inbound.start_time,0)\
                        +1.3*running.get_moment_direction(self.outbound.start_time-5,1)
    
    def next_optimal_trip_pair(self,running=step_time()):
        st=self.inbound.start_time+1.3*running.get_moment_direction(self.inbound.start_time,0)+1.3*running.get_moment_direction(self.outbound.start_time,1)
        return TripPair(st,self.inbound.block_id,self.is_virtual,running)
    
    def next_feasible_trip_pair(self,running=step_time()):
        st=self.inbound.start_time+running.get_moment_direction(self.inbound.start_time,0)+running.get_moment_direction(self.outbound.start_time,1)+10
        return TripPair(st,self.inbound.block_id,self.is_virtual,running)
    
    def to_array(self):
        return [self.inbound.to_array(),self.outbound.to_array(),self.next_arrive,self.is_virtual,self.block_id]

class TripPairGroup:
    def __init__(self,start_time=[],running=step_time(),headway=step_time()) -> None:
        '''
        start_time: list of int, in minutes
        '''
        self.trip_pair_group=[]
        for i in range(len(start_time)):
            self.trip_pair_group.append(TripPair(start_time=start_time[i],block_id=i,is_virtual=False,running=running))
    
    def append(self,trip_pair):
        self.trip_pair_group.append(trip_pair)
    
    def pop(self):
        return self.trip_pair_group.pop()
    
    def insert_virtual_trip_pair(self,index=-1):
        virtual_trip_pair=TripPair(start_time=self.trip_pair_group[index].inbound.start_time,
                                    block_id=self.trip_pair_group[index].inbound.block_id,
                                    is_virtual=True)
        self.trip_pair_group.insert(index,virtual_trip_pair)
        for i in range(index+1,len(self.trip_pair_group)):
            self.trip_pair_group[i].inbound.block_id+=1
            self.trip_pair_group[i].outbound.block_id+=1
            self.trip_pair_group[i].block_id+=1
        return self.trip_pair_group.pop().inbound.start_time
    
    def get_last_trip_pair_start_time(self):
        for i in range(len(self.trip_pair_group)-1,-1,-1):
            if self.trip_pair_group[i].is_virtual!=1:
                break
        return self.trip_pair_group[i].inbound.start_time 
    
    def get_main_last_trip(self):
        """
        > 函数返回主线中的最后一趟
        :return: 主线的最后一趟。
        """
        # get the last trip in the main line
        for i in range(len(self.trip_pair_group)-1,-1,-1):
            if self.trip_pair_group[i].is_virtual!=True:
                break
        return self.trip_pair_group[i].inbound

    def next_running_trip_pair_group(self,running=step_time()):
        res=TripPairGroup()
        for i in range(len(self.trip_pair_group)):
            res.append(self.trip_pair_group[i].next_feasible_trip_pair(running))
        return res
    def modified_headway(self,flag='add',direction=-1,running=step_time(),headway=step_time()):
        '''
        flag: add or plus
        '''
        for j in range(len(self.trip_pair_group)-1):
            if flag=='add':
                if direction==1:
                    print('from top to bottom add headway')
                    for i in range(j+1,len(self.trip_pair_group)):
                        if self.trip_pair_group[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_group[i]=TripPair(self.trip_pair_group[i].inbound.start_time+5,
                                                            self.trip_pair_group[i].inbound.block_id,
                                                            is_virtual=False,running=running)
                        yield self.trip_pair_group,headway
                else:
                    print('from bottom to top add headway ')
                    for i in range(len(self.trip_pair_group)-1,j-1,-1):
                        if self.trip_pair_group[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_group[i]=TripPair(self.trip_pair_group[i].inbound.start_time+5,
                                                            self.trip_pair_group[i].inbound.block_id,
                                                            is_virtual=False,running=running)
                            headway.adjust(self.trip_pair_group[i].inbound.start_time,0,5)
                        yield self.trip_pair_group,headway   
            elif flag=='reduce':
                if direction==1:
                    print('from top to bottom reduce headway')
                    for i in range(j,len(self.trip_pair_group)):
                        if self.trip_pair_group[i].is_virtual==1:
                            pass
                        else:
                            self.trip_pair_group[i]=TripPair(self.trip_pair_group[i].inbound.start_time-5,
                                                            self.trip_pair_group[i].inbound.block_id,
                                                            is_virtual=False,running=running)
                            headway.adjust(self.trip_pair_group[i].inbound.start_time,0,-5)
                        yield self.trip_pair_group,headway
                else:
                    print('from bottom to top reduce headway')
                    for i in range(len(self.trip_pair_group)-1,j-1,-1):
                        if self.trip_pair_group[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_group[i]=TripPair(self.trip_pair_group[i].inbound.start_time-5,
                                                            self.trip_pair_group[i].inbound.block_id,
                                                            is_virtual=False,running=running)
                            headway.adjust(self.trip_pair_group[i].inbound.start_time,0,-5)
                        yield self.trip_pair_group,headway
    def to_array(self):
        res=[]
        for i in range(len(self.trip_pair_group)):
            res.append(self.trip_pair_group[i].to_array())
        return res

## trip_pair_group test
# print('---test for Trip Pair Group')
# first_group=TripPairGroup(start_time=[360,390,420,450],running=running,headway=headway)
# print(first_group.to_array())
# print(first_group.insert(2))
# print(first_group.to_array())
# print(first_group.get_last_trip_pair_start_time())
# print(first_group.next_running_trip_pair_group(running=running).to_array())

# print('---- line 188 test for the modified_headway')  
# for a,b in first_group.modified_headway(flag='reduce',direction=-1,running=running,headway=headway):
#     print('---modifed round stop-')
#     for c in a:
#         print(c.to_array())
        
class Timetable:
    def __init__(self,n_main=0,n_aid=0,first_trip_time=360,end_trip_time=1440,running=step_time(),headway=step_time()) -> None:
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
        # 时刻表的运营时间
        self.running=running
        # 时刻表的发车间隔
        self.headway=headway
    
    def Init_trip_pair_group(self):
        """
        初始化第一个 TripPairGroup
        """
        temp_start_time_list=[self.first_trip_time]
        for i in range(self.block_num-1):
            temp_start_time_list.append(temp_start_time_list[-1]+self.headway.get_moment_direction(temp_start_time_list[-1],0))
        init_trip_pair_group=TripPairGroup(start_time=temp_start_time_list,running=self.running,headway=self.headway)
        self.group_list.append(init_trip_pair_group)
        return init_trip_pair_group.to_array()
    
    def next_headway_trip_pair_group(self):
        ht=self.group_list[-1].get_last_trip_pair_start_time()
        headway_time_list=[]
        for i in range(self.block_num):
            ht+=self.headway.get_moment_direction(ht,0)
            headway_time_list.append(ht)
        h_trip_pair_list=TripPairGroup(start_time=headway_time_list,running=self.running,headway=self.headway)
        return h_trip_pair_list
    
    def Gen_trip_pair_group_list(self):
        """
        优先生成headway的解,不行再生成running time feasible的解
        """
        if len(self.group_list)==0:
            raise Exception('please initialize the timetable first')
        h_trip_pair_list=self.next_headway_trip_pair_group()
        r_trip_pair_list=self.group_list[-1].next_running_trip_pair_group(running=self.running)
        return h_trip_pair_list,r_trip_pair_list
    
    def Gen_feasible_trip_pair_group(self,h_trip_pair_group,r_trip_pair_group):
        """
        生成可行的trip_pair_group
        """
        import copy
        # 最好是headway的解，不行的话再考虑running time的解
        modifed_trip_pair_group=copy.deepcopy(h_trip_pair_group)
        mark=self.rule_layover_time(modifed_trip_pair_group)
        max_num=2
        while mark!=0 and max_num>0:
            print('current MAKR',mark)
            # 根据layover time来操作待匹配的trip pair group list
            modifed_trip_pair_group=self.operate_trip_pair_group(modifed_trip_pair_group,mark,headway=self.headway)
            mark=self.rule_layover_time(modifed_trip_pair_group)
            if mark==0:
                print('--LOG: add headway modifed_trip_pair_group')
                return True,modifed_trip_pair_group
            max_num-=1
        # 如果headway的解不行，再考虑running time的解
        if mark==0:
            print('--LOG: add headway perfect_trip_pair_group')
            return True,modifed_trip_pair_group
        print('--LOG: add running time no correct_trip_pair_group,mark',mark)
        print('--Sorry,modifed-trip-pair-is-against-rule:',modifed_trip_pair_group.to_array())
        return True,self.group_list[-1].next_running_trip_pair_group(running=self.running)
    
    def Search_trip_pair_group(self):
        """
        找到目前匹配的最优解
        """
        h_trip_pair_group,r_trip_pair_group=self.Gen_trip_pair_group_list()
        print('LOG-Begin: generating the trip pair group list')
        print(h_trip_pair_group.to_array())
        print(r_trip_pair_group.to_array())
        print('Log-End:  generating the trip pair group list over')
        mark,group=self.Gen_feasible_trip_pair_group(h_trip_pair_group,r_trip_pair_group)
        if mark:
            self.group_list.append(group)

    def operate_trip_pair_group(self,to_match_trip_pair,init_flag=0,headway=step_time()):
        import copy
        to_match_trip_pair_init=copy.deepcopy(to_match_trip_pair)
        group_list_init=copy.deepcopy(self.group_list)
        if init_flag==0:
            # the layover time is ok
            return to_match_trip_pair
        else:
            if init_flag==1:
                # the first trip pair group is to long
                for i in range(len(to_match_trip_pair.trip_pair_group)):
                    if to_match_trip_pair.trip_pair_group[i].is_virtual==1:
                        continue
                    else:
                        to_match_trip_pair.trip_pair_group[i].inbound.start_time-=5
                        if self.rule_layover_time(to_match_trip_pair)!=1 and self.rule_basic():
                            return to_match_trip_pair
                for modfied_trip_pair,modified_headway in self.group_list[-1].modified_headway('reduce'):
                    headway=modified_headway
                    to_match_trip_pair=self.next_headway_trip_pair_group()
                    if self.rule_layover_time(to_match_trip_pair)!=1:
                        return to_match_trip_pair

            if init_flag==2:
                # the layover time is too long
                # insert the virtual trip pair
                # two class is priority
                while self.block_mode_buffer:
                    # 优先插入block mode buffer中的trip pair
                    self.group_list[-1].insert_virtual_trip_pair(self.block_mode_buffer.pop())
                    to_match_trip_pair=self.next_headway_trip_pair_group()
                    if self.rule_layover_time(to_match_trip_pair)!=2 and self.rule_layover_time(to_match_trip_pair)<12 and self.rule_basic():
                        return to_match_trip_pair
                
                for i in range(1,len(to_match_trip_pair.trip_pair_group)):
                    # 先看待匹配班次能否插入虚拟班次
                    if self.block_mode_status[i]>0 and self.block_mode_status[i]//2==0:
                        self.block_mode_status[i]-=1
                        continue

                    to_match_trip_pair.insert_virtual_trip_pair(i)
                    self.block_mode_buffer.append(i)
                    self.block_mode_status[i]=1
                    if self.rule_layover_time(to_match_trip_pair)!=2 and self.rule_layover_time(to_match_trip_pair)<12 and self.rule_basic():
                        self.block_mode_buffer[i]+=1
                        return to_match_trip_pair
                    self.block_mode_status[i]-=1
                    self.block_mode_buffer.pop()
                    self.block_mode[i]=0
                    to_match_trip_pair=to_match_trip_pair_init


                for i in range(len(to_match_trip_pair.trip_pair_group)-1,-1,-1):
                    # 再看最后一个trip pair group能否插入虚拟班次
                    if self.block_mode_status[i]>0 and self.block_mode_status[i]//2==0:
                        self.block_mode_status[i]-=1
                        continue

                    self.group_list[-1].insert_virtual_trip_pair(i)

                    self.block_mode_buffer.append(i)
                    self.block_mode_status[i]+=1
                    self.block_mode[i]=1

                    to_match_trip_pair=self.next_headway_trip_pair_group()
                    if self.rule_layover_time(to_match_trip_pair)!=2 and self.rule_layover_time(to_match_trip_pair)<12 and self.rule_basic():
                        self.block_mode_status[i]+=1
                        return to_match_trip_pair

                    self.block_mode_status[i]-=1
                    self.block_mode_buffer.pop()
                    self.block_mode[i]=0

                    self.group_list=group_list_init
                    # insert the virtual trip pair is over
            
            if init_flag==9:
                for i in range(len(to_match_trip_pair.trip_pair_list)):
                    # 对headway trip pair group insert virtual trip pair
                    if self.block_mode_buffer[i]>0 and self.block_mode_buffer[i]//2==0:
                        self.block_mode_buffer[i]-=1
                        continue
                    to_match_trip_pair.insert_virtual_trip_pair(i)
                    self.block_mode_buffer.append(i)
                    self.block_mode_status[i]=1
                    if self.rule_layover_time(to_match_trip_pair)!=2 and self.rule_layover_time(to_match_trip_pair)<12 and self.rule_basic():
                        self.block_mode_buffer[i]+=1
                        return to_match_trip_pair
                    self.block_mode_status[i]=0
                    self.block_mode_buffer.pop()
                    to_match_trip_pair=to_match_trip_pair_init

            if init_flag==-1:
                # the layover time is short
                # modified the headway
                pass
            if init_flag==10:
                for modfied_trip_pair,modified_headway in to_match_trip_pair.modified_headway('negative'):
                    headway=modified_headway
                    to_match_trip_pair=self.next_headway_trip_pair_group()
                    if self.rule_layover_time(to_match_trip_pair)!=10 and self.rule_basic():
                        return to_match_trip_pair
            
            if init_flag>10 and init_flag%2!=0:
                # the layover time is short
                # modified the headway
                index=init_flag//10-1
                for i in range(len(to_match_trip_pair.trip_pair_group)):
                    if i<index:
                        continue
                    else:
                        to_match_trip_pair.trip_pair_group[i].inbound.start_time+=5
                        if self.rule_layover_time(to_match_trip_pair)!=10 and self.rule_basic():
                            return to_match_trip_pair
                for modfied_trip_pair,modified_headway in to_match_trip_pair.modified_headway('add',-1):
                    headway=modified_headway
                    to_match_trip_pair=self.next_headway_trip_pair_group()
                    if self.rule_layover_time(to_match_trip_pair)!=10 and self.rule_basic():
                        return to_match_trip_pair
                return to_match_trip_pair
                
            
            if init_flag>10 and init_flag%2==0:
                index=init_flag//10-1
                self.block_mode_buffer.append(index)
                to_match_trip_pair[-1].insert_virtual_trip_pair(index)
                self.block_mode_status[i]=1
                if self.rule_layover_time(to_match_trip_pair)!=2 and self.rule_layover_time(to_match_trip_pair)!=-10 and self.rule_basic():
                    return to_match_trip_pair
                self.block_mode_buffer.pop()
                self.block_mode_status[i]=0
                i=len(to_match_trip_pair.trip_pair_list)-1
                for i in range(len(to_match_trip_pair.trip_pair_list)-1,-1,-1):
                    self.block_mode_buffer.append(i)
                    to_match_trip_pair=self.next_headway_trip_pair_group()
                    to_match_trip_pair[-1].insert_virtual_trip_pair(i)
                    self.block_mode_status[i]=1
                    if self.rule_layover_time(to_match_trip_pair)!=2 and self.rule_layover_time(to_match_trip_pair)!=-10 and self.rule_basic():
                        return to_match_trip_pair
                    self.block_mode_status[i]=0
                    self.block_mode_buffer.pop()
                    # insert the virtual trip pair is over
                    i-=1       
        print('most warning case')
        print('no way to find the solution')
        return to_match_trip_pair_init
        

    def rule_layover_time(self,to_match_trip_pair_group):
        # rule: layover time
        layover_time_diff=self._cal_layover_time_diff(to_match_trip_pair_group.trip_pair_group)
        print(layover_time_diff)
        res=0
        if layover_time_diff[0]>10:
            # modify the headway(negative)
            if layover_time_diff[0]>20:
                # insert a virtual trip pair
                return 2
            return 1
        elif layover_time_diff[0]<-10:
            # *|MARKER_CURSOR|*
            # modify the headway(positive)
            return -1
        
        for i in range(1,len(layover_time_diff)):
            if self.block_mode[i]==1:
                continue
            elif layover_time_diff[i]>10:
                # modify the headway(negative) for headway pair
                if max(layover_time_diff)>20:
                    # insert a virtual trip pair
                    res=9
                res=10
            elif layover_time_diff[i]<-10:
                # modify the headway(positive) for headway pair
                res=i*10+11
            elif layover_time_diff[i]<-20:
                res=i*10+12
        return res

    def _cal_layover_time_diff(self,trip_pair_list):
        layover_time=[]
        buffer=0
        for i in range(len(trip_pair_list)):
            if trip_pair_list[i].is_virtual !=True:
                if trip_pair_list[i].inbound.start_time>=600 and trip_pair_list[i].inbound.start_time<=780:
                    # eat time
                    if self.meal_flag[trip_pair_list[i].inbound.block_id]==1:
                        # eat time and meal_flag=1
                        buffer=-self.meal_time
                        self.meal_flag[trip_pair_list[i].inbound.block_id]=0
                layover_time.append(trip_pair_list[i].inbound.start_time-self._get_block_lasted_arrive(i)+buffer)
        return layover_time

    def _get_block_lasted_arrive(self,block_id):
        # get the lasted trip in the block
        # return the lasted trip
        for i in range(len(self.group_list)-1,-1,-1):
            if self.group_list[i].trip_pair_group[block_id].is_virtual!=True:
                return self.group_list[i].trip_pair_group[block_id].next_arrive
        return 0

    def rule_basic(self):
        # rule: basic
        # runnning time rule
        for i in range(len(self.group_list)-1,-1,-1):
            if i==0:
                return True
            # 看前一个group的最后一趟车的运行时间是否超过了最大运行时间
            for j in range(len(self.group_list[i].trip_pair_group)):
                if self.group_list[i].trip_pair_group[j].is_virtual==True or self.group_list[i-1].trip_pair_group[j].is_virtual==True:
                    continue
                if self.group_list[i].trip_pair_group[j].inbound.start_time<self.group_list[i].trip_pair_group[j].next_feasible_trip_pair().inbound.start_time-10:
                    print('BASIC RULE BROKEN!!')
                    print('current timetable is ',timetable.to_array())
                    print(self.group_list[i].trip_pair_group[j].inbound.start_time)
                    print(self.group_list[i].trip_pair_group[j].next_feasible_trip_pair().inbound.start_time)
                    return False
        return True

    def to_timetable_array(self):
        timetable_array = []
        for i in range(len(self.group_list)):
            for j in range(len(self.group_list[i].trip_pair_group)):
                if len(timetable_array)<=j:
                    timetable_array.append([])
                if self.group_list[i].trip_pair_group[j].is_virtual==1:
                    print(self.group_list[i].trip_pair_group[j].to_array())
                else:
                    timetable_array[j].append(self.group_list[i].trip_pair_group[j].inbound.to_array())
                    timetable_array[j].append(self.group_list[i].trip_pair_group[j].outbound.to_array())
        return timetable_array
    
    def to_array(self):
        res=[]
        for i in range(len(self.group_list)):
            t=[]
            for j in range(len(self.group_list[i].trip_pair_group)):
                t.append(self.group_list[i].trip_pair_group[j].to_array())
            res.append(t)
        return res
    def visualize(self,timetable_array,title='timetable'):
        import matplotlib.pyplot as plt
        max_index = 0
        for index in timetable_array:
            for bus in index:
                c = ['b', 'r']
                plt.hlines(y=bus[2], xmin=bus[0], xmax=bus[0] + self.running.get_moment_direction(bus[0], bus[1]), colors=c[bus[1]])
                max_index = max(max_index, bus[2])
        plt.yticks(list(range(1, max_index + 1)))
        plt.title(title)
        plt.show()


## Timetable test
# print('---test for timetable---')
timetable=Timetable(n_main=4,n_aid=0,first_trip_time=360,end_trip_time=1240,running=running,headway=headway)
# print('---test for timetable.init_trip_pair_group()')
# print(timetable.Init_trip_pair_group())
# print('---test for the to_timetable_array() ')
# print(timetable.to_timetable_array())
# print('---test for the gen_feasible_trip_pair_gourp_list')
# for trippairgroup in timetable.Gen_trip_pair_group_list():
#     print(trippairgroup.to_array())
# print('---MAIN test for the search')
# timetable.Search_trip_pair_group()
# print(timetable.to_array())
timetable.Init_trip_pair_group()
while timetable.group_list[-1].get_main_last_trip().start_time<timetable.end_trip_time:
    timetable.Search_trip_pair_group()
    print(timetable.to_array())
    print('---')

# delete the last group
for trip_pair in timetable.group_list[-1].trip_pair_group:
    if trip_pair.outbound.start_time>1240:
        trip_pair.is_valid = True
timetable.visualize(timetable.to_timetable_array())
        

        

        

 