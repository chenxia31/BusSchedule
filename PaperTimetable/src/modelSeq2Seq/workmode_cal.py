# 需要安装cplex环境
from pyomo.environ import *

# creation of a concrete model
model = ConcreteModel()

# Set defination
N=10 # the number of the driver
upstream_work=103.5
downstream_work=101.5
drive_id=[i for i in range(N)] 
model.drive_id = Set(initialize=drive_id)
M=8
workmode_id=[i for i in range(M)] # the number of the work-mode
model.workmode_id = Set(initialize=workmode_id)

# Parameter defination
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# workmode-time的上限和下限设置对最终的解答会造成影响，会导致找不到解
# 之后可以考虑对于workmode time进行比例的设置，来得到不同的求解结果
# sum_weekday & sum_weekend 
# 计算可以是根据发车间隔计算出全天的班次总数，之后根据运营时间的取值得到建议值
# 后续可以考虑对于weekday和weekend的班次进行划分，分别进行计算
# ------------------------------------------------------------------------------
# the workmode_time is defined with the upper and lower bound
model.workmode_time = Param(model.workmode_id, within=NonNegativeReals)
upper=[i*1.1 for i in [0,13.1,9.86,8.76,8.21,7.88,9.2,7.66]]
lower=[i*0.9 for i in [0,11.6,8.71,7.74,7.26,6.97,8.13,6.77]]
model.workmode_time.ub = upper
model.workmode_time.lb = lower
# the total number of the shift time for weekday and weekend
model.sum_weekday=Param(initialize=upstream_work)
model.sum_weekend=Param(initialize=downstream_work)
# ratio in the j work-mode
model.x_ratio=Param(model.workmode_id,initialize=[1,1,2,3,4,5,1,6])
model.y_ratio=Param(model.workmode_id,initialize=[1,2,3,4,5,6,1,7])

# Variable defination
model.is_work=Var(model.drive_id, model.workmode_id, within=Binary)
# the i driver  work in the j work-mode and his work_cnt may defined as the following:
model.work_cnt = Var(model.drive_id, model.workmode_id, initialize=0,within=NonNegativeReals) # 是否需要NonNegativeIntegers
# the month toal number of the j work-mode
model.y=Var(model.workmode_id,within=NonNegativeIntegers)


# Objective defination
def obj_rule(model):
    return sum(model.y[j] for j in model.workmode_id)
model.obj = Objective(rule=obj_rule, sense=minimize)

# Constraint defination
def y_init(model,j):
    # y is the total number of the j work-mode and interger constraint
    return model.y[j] == sum(model.is_work[i,j] for i in model.drive_id)*model.y_ratio[j]/model.x_ratio[j]
model.y_init = Constraint(model.workmode_id, rule=y_init)

def rule1(model):
    # rule1: the planing bus should be equal to the total number of the driver
    return sum(model.work_cnt[i,j] for j in model.workmode_id for i in model.drive_id) >= model.sum_weekday
model.rule1 = Constraint(rule=rule1)

def rule1_weekend(model):
    # rule1_weekend: the planing bus should be equal to the total number of the driver
    return sum(model.work_cnt[i,j] for i in model.drive_id for j in [6,7]) >= (model.sum_weekday-model.sum_weekend)
model.rule1_weekend = Constraint(rule=rule1_weekend)

def rule2(model,i,j):
    # rule2: the average work_cnt of the i driver in the j work-mode should be less than the upper bound
    return model.work_cnt[i,j]<= (model.workmode_time.ub[j]*model.is_work[i,j])
model.rule2 = Constraint(model.drive_id,model.workmode_id, rule=rule2)

def rule3(model,i,j):
    # rule3: the average work_cnt of the i driver in the j work-mode should be greater than the lower bound
    return model.work_cnt[i,j]>= (model.workmode_time.lb[j]*model.is_work[i,j])
model.rule3 = Constraint(model.drive_id,model.workmode_id, rule=rule3)


solver = SolverFactory('cplex')
solver.options['mip tolerances mipgap'] = 0.2
result = solver.solve(model, tee=True)
for i in range(M):
    print('different work_mode'+str(i)+' for different work_cnt')
    print(model.y[i]())
for i in range(M):
    for j in range(N):
        if model.is_work[j,i]() != 0:
            print(model.work_cnt[j,i]())