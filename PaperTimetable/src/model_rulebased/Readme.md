# 基于 回溯搜索(bakctracking search) & 人工规则(rule based) 的公交时刻表调度编制

## Introduction
这是之前七月份写的，在输入《headway、runningtime》的情况下，利用FIFO的规则来排除时刻表，其中的规则很简单
后续的更改思路就是在这个基础上修改，增加删除班次、时间调整等等
有时刻表的可视化代码

## Content of the repository

``` python
- timetable_FIFO_[tag]_%mm%dd.py #当时版本的基于FIFO生成时刻表的过程
- src #源代码文件夹
    - backup #可能会需要用到的备份数据
    - matureModel # 后续会使用的强化学习的model
    - problem # 问题运行的目录
        - timetableDefine.py #相关类的定义，trip、trip pair、trip pair group、timetable
        - solution.py #回溯算法的定义，timetableBacktraking的继承
        - runScripts.py #运行脚本
    - util # 一些工具的文件夹
        - timetableview.py # 时刻表可视化、评估的东西
        - datashow.py # 数据对比和可视化的东西
    - intro.md 
```
## Instructions

## Technologies and tool used


