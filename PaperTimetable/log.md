## 2023-06-08
生成数据集，其中正常的时刻表的名单
### 名单list
data/DrivingPlanJDBUS/嘉定13路 行车时刻表2022.11.22.xlsx
data/DrivingPlanJDBUS/嘉定12路行车时刻表2021.8.xlsx
data/DrivingPlanJDBUS/嘉定56路 行车时刻表2022.11.22.xlsx
data/DrivingPlanJDBUS/嘉定9路行车时刻表2022. 12.10.xlsx
data/DrivingPlanJDBUS/嘉定133路 行车时刻表2022.12.xlsx
data/DrivingPlanJDBUS/嘉定1路 行车时刻表2021.4.xls
data/DrivingPlanJDBUS/嘉定13路 行车时刻表2022.11.22 2.xlsx
data/DrivingPlanJDBUS/嘉定51路 行车时刻表2022.7.xls
data/DrivingPlanJDBUS/嘉定107路  行车时刻表2022.9.24.xls

### 保存格式
dict形式，不同时刻表的 工作日和双休日都有
    res={
        'timetableChain':timetableChain,
        'headwayPoint':headwayPoint,
        'headwayTime':headwayTime,
        'runningPoint':runningPoint,
        'runningTime':runningTime,
        'mealInterval':mealInterval,
        'mealCount':mealCount,
        'workmodeInterval':workmodeInterval,
        'workmodeCount':workmodeCount
    }

weekday
weekend
保存在 data/virtualTimetable/timetableSeqGroundTruth.pkl 目录中

2023-06-08 尝试使用ANN，发现不可行
原因：
1. 没有归一化，同时数据集中并不是所有的班次
2. 数据中没有加入虚拟的班次，完整性不够
3. 数据的可替换顺序导致结果不可行，需要用PointerNet之类的工具来实现
4. 需要使用seq2se的模型