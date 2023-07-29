from solution import Headway,Running_time,timetableBacktraking
import sys
sys.path.append('PaperTimetable/src/model_rulebased/src/util')
from util.timetableview import timetableVisualize
import copy
    
headway_time=[[30, 30, 25, 25, 25, 20, 20, 20, 25, 25, 25, 25, 30, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 20, 20,
         25, 30, 35, 35, 35, 40],
        [30, 30, 30, 30, 30, 25, 20, 20, 20, 25, 25, 25, 25, 25, 25, 30, 30, 30, 30, 30, 30, 30, 30, 25, 25, 20, 25, 20,
         25, 25, 35, 35, 35, 35]]

headway_time=[                    [15,15, 15, 10, 10, 10, 10, 10, 10, 8, 8, 8, 8, 8, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 30, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 15, 15, 15, 15, 15, 15,15],
                    [15,15, 15, 12, 11, 11, 11, 10, 10, 12, 12, 12, 12, 12, 10, 10, 10, 10, 10, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 15, 15, 15, 10,10]
]
headway_point=[
        [0, 360, 390, 415, 440, 460, 480, 500, 525, 550, 575, 600, 630, 655, 680, 710, 740, 770, 800, 830, 860, 890,
         920, 945, 970, 990, 1010, 1030, 1055, 1085, 1120, 1155, 1190, 1230, 2000],
        [0, 390, 420, 450, 480, 505, 525, 545, 565, 590, 615, 640, 665, 690, 715, 745, 775, 805, 835, 865, 895, 925,
         955, 980, 1005, 1025, 1050, 1070, 1095, 1120, 1155, 1190, 1225, 1260, 2000]]

headway_point=[
[0,300, 315, 330, 340, 350, 360, 370, 380, 390, 398, 406, 414, 422, 430, 440, 450, 465, 480, 495, 510, 525, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 942, 954, 966, 978, 990, 1002, 1014, 1026, 1038, 1050, 1062, 1074, 1086, 1098, 1110, 1125, 1140, 1155, 1170, 1185, 1200,1440],
 [0,335, 350, 365, 377, 388, 399, 410, 420, 430, 442, 454, 466, 478, 490, 500, 510, 520, 530, 540, 555, 570, 585, 600, 615, 630, 645, 660, 675, 690, 705, 720, 735, 750, 765, 780, 795, 810, 825, 840, 855, 870, 885, 900, 915, 930, 945, 960, 975, 987, 999, 1011, 1023, 1035, 1047, 1059, 1071, 1083, 1095, 1107, 1119, 1131, 1143, 1155, 1167, 1180, 1195, 1210, 1225, 1235,1440] 
        ]
running_time_time=[[25, 30, 35, 45, 35, 30, 35, 30, 25], 
                    [35, 30, 40, 30, 35, 30, 25]]
runnning_time_point=[[0, 390, 415, 440, 480, 500, 990, 1030, 1085, 2000],
                     [0, 390, 420, 480, 980, 1025, 1095, 2000]]
                     
runnning_time_point=[[0, 360, 398, 406, 422, 450, 480, 1110, 1185, 2000], [0, 350, 388, 399, 410, 430, 454, 478, 490, 870, 987, 1083, 1107, 1131, 1180, 2000]]
running_time_time=[[30, 35, 40, 45, 50, 45, 40, 35, 30], [30, 35, 40, 45, 50, 55, 50, 45, 40, 45, 50, 45, 40, 35, 30]]  

headway=Headway(time=headway_time,point=headway_point)
running_time=Running_time(time=running_time_time,point=runnning_time_point)


tbFIFOsearch=timetableBacktraking(n_main=12,n_aid=0,first_trip=300,end_trip=1200,headway=headway,running_time=running_time)

res=[]
def backtracking(tbFIFOsearch):
    if tbFIFOsearch.get_end_time()>=tbFIFOsearch.end_trip_time:
        for i in range(len(tbFIFOsearch.groups[-1].trips)):
            if tbFIFOsearch.groups[-1].trips[i].inbound_trip.start_time>tbFIFOsearch.end_trip_time+10:
                tbFIFOsearch.groups[-1].trips[i].is_virtual=True
        if tbFIFOsearch.finally_check():
            print('INFO: find a solution')
            res.append(copy.deepcopy(tbFIFOsearch))
        return

    # 生成next_trip_pair_group
    if tbFIFOsearch.groups==[]:
        next_trip_pair_group_list=tbFIFOsearch.Init_trip_pair_group()
    else:
        next_trip_pair_group_list=tbFIFOsearch.Search_trip_pair_group(tbFIFOsearch.groups[-1])

    for next_trip_pair_group in next_trip_pair_group_list:
        # 判断新加入的trip——pair-group是否合法
        # 如果合法就不修改
        if tbFIFOsearch.check(next_trip_pair_group):
            tbFIFOsearch.groups.append(next_trip_pair_group) 

            # 更新司机的两头班的状态
            if next_trip_pair_group.get_lasted_virtual_index():
                if len(tbFIFOsearch.groups)==1:
                    tbFIFOsearch.block_mode[next_trip_pair_group.get_lasted_virtual_index()]=0
                else:
                    if next_trip_pair_group.trips[0].inbound_trip.start_time>800:
                        pass
                    else:
                        tbFIFOsearch.block_mode_status[next_trip_pair_group.get_lasted_virtual_index()]+=1

            backtracking(tbFIFOsearch)

            temp=tbFIFOsearch.groups.pop()

            # group list update的同时，司机的mode 和mode status也需要更新
            if temp.get_lasted_virtual_index():
                if len(tbFIFOsearch.groups)==0:
                    tbFIFOsearch.block_mode[next_trip_pair_group.get_lasted_virtual_index()]=0
                else:
                    tbFIFOsearch.block_mode_status[next_trip_pair_group.get_lasted_virtual_index()]-=1

    if next_trip_pair_group_list==[]:
        return
backtracking(tbFIFOsearch)

import pickle
with open('res.pickle','wb') as f:
    pickle.dump(res,f)
    
print(len(res))
for i in range(len(res)):
    timetableVisualize.view(res[i])
