import sys
sys.path.append('..')
sys.path.append('utils')
from utils import runningtimeGen
from utils.timetableVisual import *
class Headway:
    def __init__(self) -> None:
        """
        初始化车头时距
        time: 车头时距
        point: 时刻
        """
        # 70路
        self.time=[[30,20,30,35,30,30],[30,20,30,35,30,30]]
        self.point=[[360,420,600,960,1200],[360,420,600,960,1200]]

headway=Headway()
runningTimeView(headway.time,headway.point,'what')