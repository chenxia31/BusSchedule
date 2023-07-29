def Busnumber(timetable_array, turning_time, turning_point):
    '''
    input:时刻表数据、行程时间、行程时间中断点
    output：最小配车数
    '''
    launch = []  # name has no meaning
    for index in timetable_array:
        for bus in index:
            launch_bus = []
            launch_bus.append(bus[0])  # start_time
            launch_bus.append(bus[1])  # 0 for upstream and 1 for downstream
            launch_bus.append(1)
            launch.append(launch_bus)
            arrive_bus = []
            arrive_bus.append(bus[0] + work_time_gen(turning_time, turning_point, bus[0], bus[1]))
            arrive_bus.append(bus[1])
            arrive_bus.append(-1)
            launch.append(arrive_bus)
    launch = np.array(launch)
    launch = launch[launch[:, 0].argsort()]
    plot_up = launch[launch[:, 1] == 0, :]
    plot_down = launch[launch[:, 1] == 1, :]
    plot_up = plot_up[:, [0, 2]]
    plot_up[:, 1] = plot_up[:, 1].cumsum()
    plot_down = plot_down[:, [0, 2]]
    plot_down[:, 1] = plot_down[:, 1].cumsum()
    plot_all = launch[:, [0, 2]]
    plot_all[:, 1] = plot_all[:, 1].cumsum()
    change_time = np.unique(launch[:, 0])
    num_up = []
    num_down = []
    for time in change_time:
        if time < plot_up[0, 0]:
            # before the beginning
            num_up.append(0)
        if time > plot_up[plot_up.shape[0] - 1, 0]:
            # after the end
            num_up.append(plot_up[plot_up.shape[0] - 1, 1])
        for i in range(plot_up.shape[0] - 1):
            # just in the right time
            if plot_up[i, 0] <= time and plot_up[i + 1, 0] > time:
                num_up.append(plot_up[i, 1])
                break
    for time in change_time:
        if time < plot_down[0, 0]:
            # before the beginning
            num_down.append(0)
        if time > plot_down[plot_down.shape[0] - 1, 0]:
            # after the end
            num_down.append(plot_down[plot_down.shape[0] - 1, 1])
        for i in range(plot_down.shape[0] - 1):
            # just in the right time
            if plot_down[i, 0] <= time and plot_down[i + 1, 0] > time:
                num_down.append(plot_down[i, 1])
                break
    num = num_up + num_down
    busNumber = ''
    busNumber = busNumber + '理论最小配车数：' + str(max(plot_all[:, 1])) + '\n'
    busNumber = busNumber + '实际配车数' + str(len(timetable_array))
    return busNumber


def work_time_gen(times_input, points_input, start_time, pattern):
    '''
    input：输入行程时间、时间的转折点、发车时间和模式
    output: 理论工作时间
    '''
    # 功能是计算已知模式和发车时间班次的实际运行时间
    # times_input 输入的行程时间间断
    # points_input 输入的行程时间的间断点
    # start_time 指的是目标行程时间
    # pattern 目标的上行或者下行间隔
    for i in range(len(points_input[pattern])):
        if start_time < (points_input[pattern][i] + 1):
            work_time_return = times_input[pattern][i - 1]
            break
    return work_time_return  # times——input开始的时间一定是0。所以一定会有值
