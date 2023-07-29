class BaseRunningTime:
    def __init__(self) -> None:
        time=[1,2,3]
        point=[4,5,6]
        self.time=time
        self.point=point

class RunningTime(BaseRunningTime):
    def __init__(self,gamma=1) -> None:
        super().__init__()
        t1=[t*gamma for t in self.time]
        self.time=t1
    
g=RunningTime(2)
print(g.time)