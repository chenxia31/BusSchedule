from deprecated.sphinx import deprecated
import numpy as np
class Headway:
    def __init__(self) -> None:
        """
        初始化车头时距
        time: 车头时距
        point: 时刻
        """
        # 70路
        self.time=[[30, 30, 25, 25, 25, 20, 20, 20, 25, 25, 25, 25, 30, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 20, 20,
         25, 30, 35, 35, 35, 40],
        [30, 30, 30, 30, 30, 25, 20, 20, 20, 25, 25, 25, 25, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 25, 20,
         25, 25, 35, 35, 35, 35]]

        # # 56路
        # self.time=[
        #             [15,15, 15, 10, 10, 10, 10, 10, 10, 8, 8, 8, 8, 8, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 30, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 15, 15, 15, 15, 15, 15,15],
        #             [15,15, 15, 12, 11, 11, 11, 10, 10, 12, 12, 12, 12, 12, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 15, 15, 15, 10,10]

        #  ]

        # self.time=[[30, 30, 25, 20, 20, 15, 15, 15, 20, 25, 25, 25, 30, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 20, 20,
        #  25, 30, 35, 35, 35, 40],
        # [30, 30, 30, 30, 25, 20, 15, 15, 15, 20, 20, 20, 20, 20, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 25, 20,
        #  25, 25, 35, 35, 35, 35]]

        self.point=[
        [0, 360, 390, 415, 440, 460, 480, 500, 525, 550, 575, 600, 630, 655, 680, 710, 740, 770, 800, 830, 860, 890,
         920, 945, 970, 990, 1010, 1030, 1055, 1085, 1120, 1155, 1190, 1230, 2000],
        [0, 390, 420, 450, 480, 505, 525, 545, 565, 590, 615, 640, 665, 690, 715, 745, 775, 805, 835, 865, 895, 925,
         955, 980, 1005, 1025, 1050, 1070, 1095, 1120, 1155, 1190, 1225, 1260, 2000]]
        
        # # 56路
        # self.point=[
        #     [0,300, 315, 330, 340, 350, 360, 370, 380, 390, 398, 406, 414, 422, 430, 440, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 942, 954, 966, 978, 990, 1002, 1014, 1026, 1038, 1050, 1062, 1074, 1086, 1098, 1110, 1125, 1140, 1155, 1170, 1185, 1200,1440],
        #     [0,335, 350, 365, 377, 388, 399, 410, 420, 430, 442, 454, 466, 478, 490, 500, 510, 520, 530, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 945, 960, 975, 987, 999, 1011, 1023, 1035, 1047, 1059, 1071, 1083, 1095, 1107, 1119, 1131, 1143, 1155, 1167, 1180, 1195, 1210, 1225, 1235,1440] 
        # ]

        # # 134路
        # self.point=[[0,290, 310, 330, 350, 370, 385, 400, 415, 430, 445, 460, 475, 495, 515, 535, 555, 580, 605, 630, 655, 680, 705, 730, 755, 780, 805, 830, 855, 880, 905, 930, 945, 960, 975, 990, 1005, 1020, 1040, 1060, 1080, 1100, 1120, 1140, 1165, 1190, 1215, 1240, 1265,2000],
        #     [0,360, 385, 410, 435, 460, 480, 500, 520, 540, 555, 570, 585, 600, 615, 630, 645, 670, 695, 720, 745, 770, 795, 820, 845, 870, 895, 920, 945, 970, 995, 1020, 1040, 1055, 1070, 1085, 1100, 1115, 1130, 1150, 1170, 1190, 1210, 1230, 1250, 1275, 1300, 1320, 1335,2000]]

        # self.time=[
        #     [20,20,20, 20, 20, 20, 15, 15, 15, 15, 15, 15, 15, 20, 20, 20, 20, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 15, 15, 15, 15, 15, 15, 20, 20, 20, 20, 20, 20, 25, 25, 25, 25, 25,25], 
        #     [25,25,25, 25, 25, 25, 20, 20, 20, 20, 15, 15, 15, 15, 15, 15, 15, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 20, 15, 15, 15, 15, 15, 15, 20, 20, 20, 20, 20, 20, 25, 25, 20, 15,15]
        # ]
    # 134路

        #  # 52路
        # self.point=[[0,300, 320, 340, 360, 375, 390, 405, 420, 435, 450, 465, 480, 505, 530, 550, 570, 590, 615, 640, 665, 690, 715, 740, 765, 790, 815, 840, 865, 890, 910, 930, 950, 970, 990, 1010, 1035, 1060, 1085, 1110, 1130, 1150, 1175, 1200,2000],
        # [0,360, 380, 400, 420, 440, 455, 475, 495, 515, 535, 550, 565, 585, 600, 615, 635, 655, 680, 705, 730, 755, 780, 805, 830, 855, 880, 905, 930, 955, 980, 1000, 1020, 1040, 1060, 1085, 1110, 1135, 1155, 1180, 1195, 1215, 1235, 1260,2000]]
        # self.time=[[20,20, 20, 20, 15, 15, 15, 15, 15, 15, 15, 15, 25, 25, 20, 20, 20, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 20, 20, 20, 20, 20, 20, 25, 25, 25, 25, 20, 20, 25, 25,25],
        # [20,20, 20, 20, 20, 15, 20, 20, 20, 20, 15, 15, 20, 15, 15, 20, 20, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 20, 20, 20, 20, 25, 25, 25, 20, 25, 15, 20, 20, 25,25]]

        # # 60路
        # self.point=[[0,280, 310, 335, 355, 375, 395, 415, 440, 465, 495, 525, 555, 585, 615, 650, 685, 725, 755, 785, 825, 855, 885, 915, 945, 975, 1005, 1030, 1055, 1080, 1110, 1140, 1170, 1200,1440],
        # [0,330, 360, 385, 410, 435, 460, 490, 515, 540, 565, 590, 615, 645, 675, 710, 745, 785, 815, 845, 885, 915, 945, 975, 1005, 1035, 1065, 1095, 1120, 1145, 1170, 1195, 1225, 1250,1440]]
        # self.time=[[30,30, 25, 20, 20, 20, 20, 25, 25, 30, 30, 30, 30, 30, 35, 35, 40, 30, 30, 40, 30, 30, 30, 30, 30, 30, 25, 25, 25, 30, 30, 30, 30,30],
        #   [30,30,25, 25, 25, 25, 30, 25, 25, 25, 25, 25, 30, 30, 35, 35, 40, 30, 30, 40, 30, 30, 30, 30, 30, 30, 30, 25, 25, 25, 25, 30, 25,25]]

        # #68路
        # self.point=[[0,360, 390, 415, 440, 460, 480, 500, 525, 550, 575, 600, 630, 655, 680, 710, 740, 770, 800, 830, 860, 890, 920, 945, 970, 990, 1010, 1030, 1055, 1085, 1120, 1155, 1190, 1230,2000],
        # [0,390, 420, 450, 480, 505, 525, 545, 565, 590, 615, 640, 665, 690, 715, 745, 775, 805, 835, 865, 895, 925, 955, 980, 1005, 1025, 1050, 1070, 1095, 1120, 1155, 1190, 1225, 1260,2000]]
        # self.time=[[30,30, 25, 25, 20, 20, 20, 25, 25, 25, 25, 30, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 20, 20, 25, 30, 35, 35, 35, 40,40],
        # [30,30, 30, 30, 25, 20, 20, 20, 25, 25, 25, 25, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 25, 20, 25, 25, 35, 35, 35, 35,35]]
        
        # 117路
        # self.time = [ [30,30, 30, 30, 30, 20, 20, 20, 20, 20, 20, 25, 25, 25, 30, 30, 40, 40, 40, 40, 40, 40, 40, 30, 30, 30, 20, 20, 20, 25, 25, 25, 25, 25, 40, 40,40],
        #       [30,30, 30, 20, 20, 20, 20, 20, 20, 25, 25, 25, 25, 30, 30, 40, 40, 40, 40, 40, 40, 40, 30, 30, 25, 20, 20, 25, 25, 25, 25, 25, 25, 35, 40, 40, 45, 45,45]]
        # self.point = [
        #    [0,330, 360, 390, 420, 450, 470, 490, 510, 530, 550, 570, 595, 620, 645, 675, 705, 745, 785, 825, 865, 905, 945, 985, 1015, 1045, 1075, 1095, 1115, 1135, 1160, 1185, 1210, 1235, 1260, 1300, 1340,2000],
        #    [0,310, 340, 370, 390, 410, 430, 450, 470, 490, 515, 540, 565, 590, 620, 650, 690, 730, 770, 810, 850, 890, 930, 960, 990, 1015, 1035, 1055, 1080, 1105, 1130, 1155, 1180, 1205, 1240, 1280, 1320, 1365, 1410,2000]]

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
        # 70路现状
        self.point=[[0, 390, 415, 440, 480, 500, 990, 1030, 1085, 2000],
                  [0, 390, 420, 480, 980, 1025, 1095, 2000]]
        self.time=[[25, 30, 35, 45, 35, 30, 35, 30, 25], 
                    [35, 30, 40, 30, 35, 30, 25]]
        
        # self.point=[[0, 360, 398, 406, 422, 450, 480, 1110, 1185, 2000], [0, 350, 388, 399, 410, 430, 454, 478, 490, 870, 987, 1083, 1107, 1131, 1180, 2000]]
        # self.time=[[30, 35, 40, 45, 50, 45, 40, 35, 30], [30, 35, 40, 45, 50, 55, 50, 45, 40, 45, 50, 45, 40, 35, 30]]       
        
        # #134路
        # self.point=[[0, 330, 350, 370, 385, 400, 475, 495, 535, 880, 1080, 1190, 2000], [0, 385, 410, 540, 945, 1040, 1130, 1190, 1275, 2000]]
        # self.time=[[65, 70, 75, 80, 85, 90, 85, 80, 75, 80, 75, 65], [65, 70, 80, 75, 80, 85, 80, 75, 65]]
        # # # 52路现状
        # self.point=[[0, 360, 390, 405, 420, 435, 480, 505, 530, 890, 990, 1060, 1110, 1150, 2000], [0, 360, 380, 420, 455, 495, 535, 565, 880, 980, 1060, 1135, 1195, 2000]]
        # self.time=[[50, 55, 60, 65, 70, 75, 65, 60, 55, 60, 65, 60, 55, 50], [50, 65, 70, 75, 70, 65, 60, 55, 60, 65, 60, 55, 50]]

        # # 60路现状
        # self.point=[[0, 355, 395, 465, 495, 1110, 1140, 2000], [0, 360, 385, 460, 745, 885, 1035, 1120, 1170, 2000]]
        # self.time=[[45, 50, 65, 60, 55, 50, 45], [45, 55, 65, 55, 60, 65, 55, 50, 45]]

        # # 68路现状
        # self.point=[[0, 350, 370, 390, 410, 450, 475, 950, 970, 1030, 1050, 1125, 1150, 2000], [0, 345, 370, 395, 470, 960, 985, 1035, 1055, 1115, 1135, 2000]]
        # self.time=[[40, 45, 50, 55, 60, 55, 50, 55, 60, 55, 50, 45, 40], [40, 45, 50, 60, 50, 55, 60, 55, 50, 45, 40]]

        # 117路
        # self.point = [[0, 390, 415, 440, 480, 500, 990, 1030, 1085, 2000], [0, 390, 420, 480, 980, 1025, 1095, 2000]]
        # self.time = [[25, 30, 35, 40, 35, 30, 35, 30, 25], [35, 30, 35, 30, 35, 30, 25,25]]
        # self.point=[[0, 2000], [0, 2000]]
        # self.time=[[45], [45]]

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

    @deprecated(version='1.0', reason="12-01 该用headway_search()")
    def modified_headway(self,flag='positive',direction=1):
        """
        修改车次对组的车头间隔
        flag: positive为增加,negative为减少
        direction: 自下而上，还是自上而下
        headway: 车头间隔类
        TODO 修改headway调整的逻辑
        """
        for j in range(len(self.trip_pair_group)-1):
            if flag=='positive':
                if direction==-1:
                    for i in range(len(self.trip_pair_group)-1):
                        if self.trip_pair_group[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_group[i]=TripPair(self.trip_pair_group[i].inbound_trip.start_time+5,
                                                            self.trip_pair_group[i].inbound_trip.block_id,
                                                            is_virtual=False)
                        yield self.trip_pair_group
                    break
                else:
                    for i in range(len(self.trip_pair_group)-1,j-1,-1):
                        if self.trip_pair_group[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_group[i]=TripPair(self.trip_pair_group[i].inbound_trip.start_time+5,
                                                            self.trip_pair_group[i].inbound_trip.block_id,
                                                            is_virtual=False)
                        yield self.trip_pair_group 
                    break
            elif flag=='negative':
                if direction==-1:
                    for i in range(len(self.trip_pair_group)-1):
                        if self.trip_pair_group[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_group[i]=TripPair(self.trip_pair_group[i].inbound_trip.start_time-5,
                                                            self.trip_pair_group[i].inbound_trip.block_id,
                                                            is_virtual=False)
                        yield self.trip_pair_group
                else:
                    for i in range(len(self.trip_pair_group)-1,j-1,-1):
                        if self.trip_pair_group[i].is_virtual==1:
                            continue
                        else:
                            self.trip_pair_group[i]=TripPair(self.trip_pair_group[i].inbound_trip.start_time-5,
                                                            self.trip_pair_group[i].inbound_trip.block_id,
                                                            is_virtual=False)
                        yield self.trip_pair_group
                    break
    
    def get_end_time(self):
        """
        返回车次对组的结束时间
        """
        for i in range(len(self.trip_pair_group)-1,-1,-1):
            if self.trip_pair_group[i].is_virtual==False:
                return self.trip_pair_group[i].inbound_trip.start_time
        raise Exception('该班次对组均为虚拟班次')

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

        mark=True
        # 生成可行的班次对组
        # 平峰时段不允许改变headway
        if self.group_list[-1].get_end_time()>=660 and self.group_list[-1].get_end_time()<=900:
            group=temp_trip_pair_group
        else:
            mark,group=self.Gen_feasible_trip_pair_group(temp_trip_pair_group)
        res=[group]
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
        """
        生成可行的班次对
        """
        # 休息时间的约束
        list=[]
        mark,index,new_meal_flag=self.rule_layover_time(trip_pair_group,self.meal_flag)
        print('line359 init mark to operate:',mark)
        if mark==0:
            self.meal_flag=new_meal_flag
            return True,trip_pair_group
        elif mark==1:
            # 减小headway
            for iter_trip_pair_group in TripPairGroup().headway_search(trip_pair_group=trip_pair_group,flag='negative'):
                mark,index,new_meal_flag=self.rule_layover_time(iter_trip_pair_group,self.meal_flag)
                if mark:
                    self.meal_flag=new_meal_flag
                    return True,iter_trip_pair_group
        elif mark==-1:
            # 增大headway
            for iter_trip_pair_group in TripPairGroup().headway_search(trip_pair_group=trip_pair_group,flag='positive'):
                mark,index,new_meal_flag=self.rule_layover_time(iter_trip_pair_group,self.meal_flag)
                if mark:
                    self.meal_flag=new_meal_flag
                    return True,iter_trip_pair_group
        elif mark==2:
            # 插入新的班次
            # 每次插入新的班次需要进行新的headway的搜索
            priority=self.find_priority()
            bid=self.find_bid()
            for iter_trip_pair_group in TripPairGroup().insert_search(trip_pair_group=trip_pair_group,priority=priority,bid=bid):
                mark,index,new_meal_flag=self.rule_layover_time(iter_trip_pair_group,self.meal_flag)
                print('begin for the inserr mark',mark)
                if mark==0:
                    self.meal_flag=new_meal_flag
                    return True,iter_trip_pair_group
                if mark==1:
                    # 减小headway
                    for iter_trip_pair_group2 in TripPairGroup().headway_search(trip_pair_group=iter_trip_pair_group,flag='negative'):
                        mark,index,new_meal_flag=self.rule_layover_time(iter_trip_pair_group2,self.meal_flag)
                        if mark:
                            self.meal_flag=new_meal_flag
                            return True,iter_trip_pair_group2
                elif mark==-1:
                    # 增大headway
                    for iter_trip_pair_group2 in TripPairGroup().headway_search(trip_pair_group=iter_trip_pair_group,flag='positive'):
                        mark,index,new_meal_flag=self.rule_layover_time(iter_trip_pair_group2,self.meal_flag)
                        if mark:
                            self.meal_flag=new_meal_flag
                            return True,iter_trip_pair_group2
                return True,iter_trip_pair_group
                
        
        mark=self.rule_basic(trip_pair_group,self.meal_flag)
        print('line 398 after oprated mark:',mark)
        if mark==0:
            pass
        else:
            pass
        return False,trip_pair_group
    
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
        if self.get_end_time()<800:
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
        if max(new_block_status)>24:
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
            try:
                return self.group_list[-1].get_end_time()
            except:
                return self.group_list[-2].get_end_time()

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
        if flag==2:
            return rest_ratio
        else:
            return work_time,banci,diff

    def finally_check(self):
        # 检查是否满足最终的约束条件

        # 条件1:工作时间的取值范围
        work_time=self.evaluate(timetable_array=self.to_timetable_array(),flag=1)
        if min(work_time)<360:
            return False
        if max(work_time)>840:
            return False
        
        # 条件2:工作时间均衡
        test_value=0
        test_balance=[]
        for i in range(len(work_time)):
            if work_time[i]<540:
                test_balance.append(work_time[i]*20.83/60)
            else:
                test_balance.append(work_time[i]*15/60)  
        if max(test_balance)-min(test_balance)>50:
            return False

        if sum(test_balance)/len(work_time)>200:
            return False
        
        # 条件3:连续的两头班的数目
        num_mode=[]

        for i in range(self.block_num):
            begin=0
            end=len(self.group_list)-1
            # 记录两头班的数量
            temp_count=0
            # 先删除上班和下班班次
            while self.group_list[begin].trip_pair_group[i].is_virtual==True:
                begin+=1
            while self.group_list[end].trip_pair_group[i].is_virtual==True:
                end-=1
            for j in range(begin,end+1):
                if self.group_list[j].trip_pair_group[i].is_virtual==True:
                    temp_count+=1
                    if temp_count==1:
                        pass
                    else:
                        try:
                            if self.group_list[j-1].trip_pair_group[i].is_virtual==False:
                                return False
                        except:
                            raise Exception('出现了两头班连续的情况')
            num_mode.append(temp_count)
        if max(num_mode)>3:
            return False
        
        if timetable.get_end_time()>timetable.end_trip_time+10 or timetable.get_end_time()<timetable.end_trip_time-10:
            return False
        
        rr=timetable.evaluate(timetable_array=timetable.to_timetable_array(),flag=2)
        if max(rr)>0.3:
            return False
        return True
    
    # 转换数字为时间格式
    def _num_to_time(self, num):
        hour = int(num / 60)
        minute = int(num % 60)
        return str(hour) + ':' + str(minute)
    
    def to_excel(self,index=1):
        # 将之前定义的格式转换成为dataframe，然后转换成为Excel
        import copy
        import pandas as pd
        import numpy as np
        filedir='./result_excel/result'+str(index)+'.xlsx'
        # 01--将之前的时刻表转换成为dataframe，写入sheet01中
        df_list=[]
        cnt=0
        col_template=['主站','时间','副站','时间']
        for TPG in self.group_list:
            temp_st=[]
            temp_running_time=[]
            temp_st_up=[]
            temp_running_time_up=[]
            for TP in TPG.trip_pair_group:
                if TP.is_virtual==False:
                    temp_st.append(self._num_to_time(TP.inbound_trip.start_time))
                    temp_running_time.append(RunningTime().get_moment_direction(TP.inbound_trip.start_time,TP.inbound_trip.direction))
                    temp_st_up.append(self._num_to_time(TP.outbound_trip.start_time))
                    temp_running_time_up.append(RunningTime().get_moment_direction(TP.outbound_trip.start_time,TP.outbound_trip.direction))
                else:
                    temp_st.append(self._num_to_time(0))
                    temp_running_time.append(-1)
                    temp_st_up.append(self._num_to_time(0))
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
        df2_list=self._headway_cal()
        df2=pd.DataFrame(df2_list)
        df2=df2.T
        df2.columns=['上行发车间隔','下行发车间隔']

        # df3分别计算一些评价指标
        df3_list=self.evaluate(timetable_array=self.to_timetable_array())
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

    def _headway_cal(self):
        # 计算上行和下行的发车时间间隔
        upstream_st=[]
        downstream_st=[]
        for i in range(len(self.group_list)):
            for j in range(len(self.group_list[i].trip_pair_group)):
                if self.group_list[i].trip_pair_group[j].is_virtual==False:
                    upstream_st.append(self.group_list[i].trip_pair_group[j].inbound_trip.start_time)
                    downstream_st.append(self.group_list[i].trip_pair_group[j].outbound_trip.start_time)
        upstream_st.sort()
        downstream_st.sort()
        upstream_headway=[]
        downstream_headway=[]
        for i in range(len(upstream_st)-1):
            upstream_headway.append(upstream_st[i+1]-upstream_st[i])
        for i in range(len(downstream_st)-1):
            downstream_headway.append(downstream_st[i+1]-downstream_st[i])
        return [upstream_headway,downstream_headway]




res=[]
import shutil
def backtracking(timetable):
    if timetable.get_end_time()>=timetable.end_trip_time:
        import copy
        for i in range(len(timetable.group_list[-1].trip_pair_group)):
            if timetable.group_list[-1].trip_pair_group[i].inbound_trip.start_time>timetable.end_trip_time:
                timetable.group_list[-1].trip_pair_group[i].is_virtual=True
        if timetable.finally_check():
            import pickle
            epochNum = len(res)//30
            with open('output/route70_4_'+str(epochNum)+'.pkl','wb') as f:
                pickle.dump(res,f)
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

timetable=Timetable(n_main=4,n_aid=0,first_trip_time=360,end_trip_time=1230,headway=Headway())


backtracking(timetable)
print('---最终结果---')
print(len(res))
index_cnt=0
for tt in res:
    # tt.view(tt.to_timetable_array())
    print('------------------')
    print('-                  -')
    print('******************')
    wk=tt.to_excel(index=index_cnt)
    wk.sort()
    import matplotlib.pyplot as plt
    plt.figure(figsize=(16,8))
    plt.subplot(3,2,1)
    for i in range(len(wk)):
        wk[i]=wk[i]/60
    plt.bar(list(range(len(wk))),height=wk,width=0.4)
    # wk2=sorted(wk2)
    # plt.bar([i+0.4 for i in range(len(wk))],height=wk2,width=0.4)
    for x,y in enumerate(wk):
        plt.text(x,y+0.05,'%.2f' % y,ha='center')
    # plt.legend(['code gen','jdbus'])
    plt.title('work time')
    # 在柱状图顶部标注数字
    plt.subplot(3,2,2)
    rrr=tt.evaluate(tt.to_timetable_array(),flag=2)
    plt.bar(list(range(len(wk))),height=rrr)
    plt.title('rest ratio')
    for x,y in enumerate(rrr):
        plt.text(x,y,'%.2f' % y,ha='center')
    plt.subplot(2,1,2)

    tt.to_array()
    
    tt.view(tt.to_timetable_array(),title='LINE_70_adjust '+'  '+'File_index= '+str(index_cnt)+'('+'Toal:'+str(len(res))+')')
    index_cnt+=1


# res=[]
# def backtracking(timetable):
#     if timetable.is_end():
#         res.append(timetable)
#         return
#     # 生成next_trip_pair_group
#     if timetable.group_list==[]:
#         next_trip_pair_group_list=timetable.init_trip_pair_group()
#     else:
#         next_trip_pair_group_list=timetable.search_next_trip_pair_group()
#     for next_trip_pair_group in next_trip_pair_group_list:
#         if timetable.check(next_trip_pair_group):
#             timetable.group_list.append(next_trip_pair_group)
#             backtracking(timetable)
#             timetable.group_list.pop()

# res=[]
# for init_trip_pair_group in timetable.Init_trip_pair_group():
#     try:
#         print('line515------------------')
#         print('*                  *')
#         print('try:',init_trip_pair_group.to_array())
#         print('*                  *')
#         print('*                  *')
#         print('line515------------------')
#         timetable.group_list.append(init_trip_pair_group)
#         # 设置两头班
#         # for i in range(len(init_trip_pair_group)):
#         #     if init_trip_pair_group[i].is_virtual==True:
#         #         timetable.block_mode[i]=1
#         while timetable.group_list[-1].get_end_time()<1000:
#             for group in timetable.Search_trip_pair_group():
#                 timetable.group_list.append(group)

#             print(timetable.group_list[-1].to_array())
#             timetable.Search_trip_pair_group()
#             print(timetable.group_list[-1].to_array())
#         res.append(timetable)
#         timetable=Timetable(n_main=4,n_aid=0,first_trip_time=360,end_trip_time=1240,headway=Headway())
#     except:
#         timetable=Timetable(n_main=4,n_aid=0,first_trip_time=360,end_trip_time=1240,headway=Headway())
#         continue


