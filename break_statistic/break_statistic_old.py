import log

#计算平均数
def calc_average(arrs):
    arr_len = len(arrs)
    if 0 == arr_len:
        return 0
    
    total = 0
    for i in xrange(0,arr_len):
        total = total + arrs[i]
    
    return float(total) / arr_len


#计算两数之积平均数
def calc_pro_average(arrs1,arrs2):
    len1 = len(arrs1)
    len2 = len(arrs2)
    if len1 != len2 or len1 == 0:
        return 0
    
    pro_sum = 0
    for i in xrange(0,len1):
        pro_sum = pro_sum + arrs1[i] * arrs2[i]
    
    return float(pro_sum) / len1


#计算线性回归方程的斜率和截距
def calc_average_back(time_idx_arr, price_arr):
    #计算时间索引序列（X轴）平均数
    ave_time_idx = calc_average(time_idx_arr)
    #计算价格序列（Y轴）平均数
    ave_close_price = calc_average(price_arr)
    #计算时间索引和对应价格乘积平均数
    ave_x_y_pro = calc_pro_average(time_idx_arr, price_arr)
    #计算时间索引平方平均数
    ave_x_power = calc_pro_average(time_idx_arr, time_idx_arr)

    log.WriteLog("points", "time_idx:%u\tprice:%f" % (time_idx_arr[0], price_arr[0]))
    log.WriteLog("points", "time_idx:%f\tprice:%f\txy:%f\tx_power:%f" % (ave_time_idx, ave_close_price, ave_x_y_pro, ave_x_power))
    log.WriteLog("points", "\n")
    #计算斜率
    a = (ave_time_idx * ave_close_price - ave_x_y_pro) / (ave_time_idx * ave_time_idx - ave_x_power)
    #计算截距
    b = ave_close_price - a * ave_time_idx
    return [a,b]


#读取高低点信息
def read_high_low(filename):
    high_low_set = []
    with open(filename, "rb") as fp:
        line = fp.readline()
        while line:
            eles = line.split('\t')
            high_low_set.append([eles[0], int(eles[1]), int(eles[2]), float(eles[3])])

            line = fp.readline()

    return high_low_set


def traverse(high_low_set):
    results = []
    flag_info = []
    #上一旗形线性回归斜率和截距（无需区分高低）
    last_back_info = []
    #旗形高点线性回归斜率和截距
    high_back_info = []
    #旗形低点线性回归斜率和截距
    low_back_info = []
    #旗形高点的时间索引、时间戳、价格
    high_points = [[],[],[]]
    #临时旗形高点的时间索引、时间戳、价格
    temp_high_points = [[],[],[]]
    #旗形低点的时间索引、时间戳、价格
    low_points = [[],[],[]]
    #临时旗形低点的时间索引、时间戳、价格
    temp_low_points = [[],[],[]]
    for high_low in high_low_set:
        high_len = len(high_points[0])
        low_len = len(low_points[0])
        change_turning = False
        if high_low[0] == "high":
            #在高点达到2个以前，不进行是否加入线性回归方程的判断
            if high_len < 2:
                high_points[0].append(high_low[1])
                high_points[1].append(high_low[2])
                high_points[2].append(high_low[3])
                #在高点达到2个的时候，计算初始线性回归方程信息
                if high_len == 1:
                    for i in xrange(0,len(high_points[0])):
                        log.WriteLog("points", "high_point_idx:%u\thigh_point_time:%u\thigh_point_price:%f" % (high_points[0][i], 
                            high_points[1][i], high_points[2][i]))

                    high_back_info = calc_average_back(high_points[0], high_points[2])

                    log.WriteLog("function", "point:%f\tslope:%f\tintercept:%f" % (high_low[2], high_back_info[0], high_back_info[1]))
            #在高点达到2个后，从第3个点开始，进行是否加入方程的判断
            else:
                a = high_back_info[0]
                b = high_back_info[1]

                #以线性回归方程做计算，算出时间索引对应下的目标价格
                tar_price = a * high_low[1] + b
                #若实际价格偏离目标价格2.5%以上，则判断该点不属于当前方程
                if (high_low[3] - tar_price) > tar_price * 0.03:
                    #若斜率向上，则方程斜率变高，需去除旧的高点，用最后一个旧高点与最新一点做线性回归运算
                    if a > 0:
                        #在斜率本就大于0的情况下增大，不可能出现斜率转向
                        temp_high_points = [[],[],[]]
                        temp_high_points[0].append(high_points[0][high_len-1])
                        temp_high_points[1].append(high_points[1][high_len-1])
                        temp_high_points[2].append(high_points[2][high_len-1])
                        temp_high_points[0].append(high_low[1])
                        temp_high_points[1].append(high_low[2])
                        temp_high_points[2].append(high_low[3])                        
                        high_back_info = calc_average_back(temp_high_points[0], temp_high_points[2])

                        high_points[0].append(high_low[1])
                        high_points[1].append(high_low[2])
                        high_points[2].append(high_low[3])   
                    #若斜率向下，则考虑低点斜率的情况
                    else:
                        #若低点斜率向下则为突破成功
                        if low_back_info[0] < 0:
                            if a >= -9:
                                #记录突破信息
                                if len(last_back_info) > 0:
                                    log.WriteLog("break", "break high\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                        high_low[1], high_low[2], high_low[3], tar_price, last_back_info[0], last_back_info[1]))
                                else:
                                    log.WriteLog("break", "break high\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f" % (high_low[1], high_low[2], high_low[3], 
                                        tar_price))

                                #记录突破时高低点坐标，斜率与截距
                                log.WriteLog("function", "high:time:%u\tslope:%f\tintercept:%f\tlow:time:%u\tslope:%f\tintercept:%f" % (
                                    high_points[1][0],high_back_info[0],high_back_info[1],low_points[1][0],low_back_info[0],low_back_info[1]))

                                #以突破点横坐标为横坐标找出延长点坐标
                                high_extend_price = high_back_info[0] * high_low[1] + high_back_info[1]
                                low_extend_price = low_back_info[0] * high_low[1] + low_back_info[1]

                                #先记录此次旗形信息
                                flag_info.append(high_points[0][0])                                 #阻力线起始点时间戳索引
                                flag_info.append(0)                                                 #阻力线起始点类型0为最高值 1为最低值
                                flag_info.append(high_points[1][0])                                 #阻力线起始点时间戳
                                flag_info.append(high_points[2][0])                                 #阻力线起始点价格
                                if len(temp_high_points[0]) > 0:
                                    flag_info.append(temp_high_points[1][0])
                                    flag_info.append(temp_high_points[2][0])
                                else:
                                    flag_info.append(high_points[1][0])
                                    flag_info.append(high_points[2][0])
                                flag_info.append(high_low[2])                                       #阻力线结束点时间戳
                                flag_info.append(high_extend_price)                                 #阻力线结束点价格
                                flag_info.append(low_points[1][0])                                  #阻力线起始点时间戳
                                flag_info.append(low_points[2][0])                                  #阻力线起始点价格
                                if len(temp_low_points[0]) > 0:
                                    flag_info.append(temp_low_points[1][0])
                                    flag_info.append(temp_low_points[2][0])
                                else:
                                    flag_info.append(low_points[1][0])
                                    flag_info.append(low_points[2][0])
                                flag_info.append(high_low[2])                                       #阻力线结束点时间戳
                                flag_info.append(low_extend_price)                                  #阻力线结束点价格                            
                                flag_info.append(high_back_info[0])                                 #阻力线斜率
                                flag_info.append(high_back_info[1])                                 #阻力线截距

                                #若上一次旗形为空，即此次旗形并非突破而来，则从阻力起始点开始计算经过距离
                                if len(last_back_info) == 0:
                                    flag_info.append(low_points[0][low_len-1] - high_points[0][0])      #阻力线经过时间戳数量
                                    flag_info.append(high_points[2][0] - low_points[2][low_len-1])      #阻力线经过价格
                                #否则以上一阻力线突破点计算经过距离，突破点由第一低点横坐标代入上一旗形方程计算所得
                                else:
                                    break_point_price = last_back_info[0] * low_points[0][0] + last_back_info[1]
                                    flag_info.append(low_points[0][low_len-1] - low_points[0][0])
                                    flag_info.append(break_point_price - low_points[2][low_len-1])

                                    result_len = len(results)
                                    if result_len > 0:
                                        results[result_len - 1][18] = low_points[0][low_len-1] - low_points[0][0]
                                        results[result_len - 1][19] = break_point_price - low_points[2][low_len-1]

                                flag_info.append(0)                                                 #阻力线突破后经过时间戳数量（暂空）
                                flag_info.append(0)                                                 #阻力线突破后经过价格（暂空）

                                #将此次阻力线信息存入集合
                                results.append(flag_info)

                                #清空阻力线信息以便下次接收
                                flag_info = []

                                #记录此次线性回归方程斜率和截距
                                last_back_info = []
                                last_back_info.extend(high_back_info)
                            else:
                                #上一次旗形非空，以上一阻力线突破点计算经过距离，突破点由第一低点横坐标代入上一旗形方程计算所得
                                if len(last_back_info) > 0:
                                    break_point_price = last_back_info[0] * low_points[0][0] + last_back_info[1]

                                    result_len = len(results)
                                    if result_len > 0:
                                        results[result_len - 1][18] = low_points[0][low_len-1] - low_points[0][0]
                                        results[result_len - 1][19] = break_point_price - low_points[2][low_len-1]

                                last_back_info = []

                            #此次旗形已结束，更新高低点集合，最新点为第一高点，原旗形最后一点为第一低点
                            high_points = [[],[],[]]
                            high_points[0].append(high_low[1])
                            high_points[1].append(high_low[2])
                            high_points[2].append(high_low[3])                         
                            low_points[0] = low_points[0][low_len-1:]
                            low_points[1] = low_points[1][low_len-1:]
                            low_points[2] = low_points[2][low_len-1:]

                            #突破发生则清空临时低点集合
                            temp_high_points = [[],[],[]]
                            temp_low_points = [[],[],[]]

                            #清空此次方程斜率和截距
                            high_back_info = []
                            low_back_info = []
                        #若低点斜率向上则重新统计斜率
                        else:
                            log.WriteLog("break", "cross:%u" % high_low[2])

                            temp_high_points = [[],[],[]]
                            temp_high_points[0].append(high_points[0][high_len-1])
                            temp_high_points[1].append(high_points[1][high_len-1])
                            temp_high_points[2].append(high_points[2][high_len-1])
                            temp_high_points[0].append(high_low[1])
                            temp_high_points[1].append(high_low[2])
                            temp_high_points[2].append(high_low[3])
                            high_back_info = calc_average_back(temp_high_points[0], temp_high_points[2])

                            if high_back_info[0] > 0:
                                change_turning = True

                            high_points[0].append(high_low[1])
                            high_points[1].append(high_low[2])
                            high_points[2].append(high_low[3])
                #若实际价格偏离目标价格2.5%以上，则判断该点不属于当前方程
                elif (high_low[3] - tar_price) < -tar_price * 0.03:
                    #无论斜率方向如何，方程斜率变低，需去除旧的高点，用最后一个旧高点与最新一点做线性回归运算
                    temp_high_points = [[],[],[]]
                    temp_high_points[0].append(high_points[0][high_len-1])
                    temp_high_points[1].append(high_points[1][high_len-1])
                    temp_high_points[2].append(high_points[2][high_len-1])
                    temp_high_points[0].append(high_low[1])
                    temp_high_points[1].append(high_low[2])
                    temp_high_points[2].append(high_low[3])
                    high_back_info = calc_average_back(temp_high_points[0], temp_high_points[2])

                    #在斜率本就小于0的情况下变小，不可能出现斜率转向
                    #只有在斜率大于0的情况下变小，才可能出现斜率转向
                    if a > 0 and high_back_info[0] < 0:
                        change_turning = True

                    high_points[0].append(high_low[1])
                    high_points[1].append(high_low[2])
                    high_points[2].append(high_low[3])
                #若实际价格未偏离目标的2.5%以上，则加入线性回归方程计算 
                else:
                    high_points[0].append(high_low[1])
                    high_points[1].append(high_low[2])
                    high_points[2].append(high_low[3])

                    #若经过斜率偏离的重新计算，则以高点临时集合进行计算
                    if len(temp_high_points[0]) > 0:
                        temp_high_points[0].append(high_low[1])
                        temp_high_points[1].append(high_low[2])
                        temp_high_points[2].append(high_low[3])
                        high_back_info = calc_average_back(temp_high_points[0], temp_high_points[2])
                    #否则在原先的高点集合中计算
                    else:
                        high_back_info = calc_average_back(high_points[0], high_points[2])

                    #此种情况下可以出现任意斜率转向的情况
                    if a > 0 and high_back_info[0] < 0 or a < 0 and high_back_info[0] > 0:
                        change_turning = True
        elif high_low[0] == "low":
            #在低点达到2个以前，不进行是否加入线性回归方程的判断
            if low_len < 2:
                low_points[0].append(high_low[1])
                low_points[1].append(high_low[2])
                low_points[2].append(high_low[3])
                #在低点达到2个的时候，计算初始线性回归方程信息
                if low_len == 1:
                    for i in xrange(0,len(low_points[0])):
                        log.WriteLog("points", "low_point_idx:%u\tlow_point_time:%u\tlow_point_price:%f" % (low_points[0][i], low_points[1][i], 
                            low_points[2][i]))

                    low_back_info = calc_average_back(low_points[0], low_points[2])

                    log.WriteLog("function", "point:%f\tslope:%f\tintercept:%f" % (high_low[2], low_back_info[0], low_back_info[1]))
            #在低点达到2个后，从第3个点开始，进行是否加入方程的判断
            else:
                a = low_back_info[0]
                b = low_back_info[1]

                #以线性回归方程做计算，算出时间索引对应下的目标价格
                tar_price = a * high_low[1] + b

                #若实际价格偏离目标价格2.5%以上，则判断该点不属于当前方程
                if (high_low[3] - tar_price) < -tar_price * 0.03:
                    #若斜率向下，则方程斜率变低，需去除旧的低点，用最后一个旧低点与最新一点做线性回归运算
                    if a < 0:
                        #在斜率本就小于0的情况下减小，不可能出现斜率转向
                        temp_low_points = [[],[],[]]
                        temp_low_points[0].append(low_points[0][low_len-1])
                        temp_low_points[1].append(low_points[1][low_len-1])
                        temp_low_points[2].append(low_points[2][low_len-1])
                        temp_low_points[0].append(high_low[1])
                        temp_low_points[1].append(high_low[2])
                        temp_low_points[2].append(high_low[3])                        
                        low_back_info = calc_average_back(temp_low_points[0], temp_low_points[2])

                        low_points[0].append(high_low[1])
                        low_points[1].append(high_low[2])
                        low_points[2].append(high_low[3])
                    #若斜率向上，则考虑高点斜率的情况
                    else:
                        #若高点斜率向上则为突破成功
                        if high_back_info[0] > 0:
                            if a <= 9:
                                #记录突破信息
                                if len(last_back_info) > 0:
                                    log.WriteLog("break", "break low\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                        high_low[1], high_low[2], high_low[3], tar_price, last_back_info[0], last_back_info[1]))
                                else:
                                    log.WriteLog("break", "break low\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f" % (high_low[1], high_low[2], high_low[3], 
                                        tar_price))

                                #记录突破时高低点坐标，斜率与截距
                                log.WriteLog("function", "high:time:%u\tslope:%f\tintercept:%f\tlow:time:%u\tslope:%f\tintercept:%f" % (
                                    high_points[1][0],high_back_info[0],high_back_info[1],low_points[1][0],low_back_info[0],low_back_info[1]))

                                #以突破点横坐标为横坐标找出延长点坐标
                                high_extend_price = high_back_info[0] * high_low[1] + high_back_info[1]
                                low_extend_price = low_back_info[0] * high_low[1] + low_back_info[1]                     

                                #先记录此次旗形信息
                                flag_info.append(low_points[0][0])                                 #阻力线起始点时间戳索引
                                flag_info.append(1)                                                #阻力线起始点类型0为最高值 1为最低值
                                flag_info.append(low_points[1][0])                                 #阻力线起始点时间戳
                                flag_info.append(low_points[2][0])                                 #阻力线起始点价格
                                if len(temp_low_points[0]) > 0:
                                    flag_info.append(temp_low_points[1][0])
                                    flag_info.append(temp_low_points[2][0])
                                else:
                                    flag_info.append(low_points[1][0])
                                    flag_info.append(low_points[2][0])
                                flag_info.append(high_low[2])                                      #阻力线结束点时间戳
                                flag_info.append(low_extend_price)                                 #阻力线结束点价格
                                flag_info.append(high_points[1][0])                                #阻力线起始点时间戳
                                flag_info.append(high_points[2][0])                                #阻力线起始点价格
                                if len(temp_high_points[0]) > 0:
                                    flag_info.append(temp_high_points[1][0])
                                    flag_info.append(temp_high_points[2][0])
                                else:
                                    flag_info.append(high_points[1][0])
                                    flag_info.append(high_points[2][0])
                                flag_info.append(high_low[2])                                      #阻力线结束点时间戳
                                flag_info.append(high_extend_price)                                #阻力线结束点价格
                                flag_info.append(low_back_info[0])                                 #阻力线斜率
                                flag_info.append(low_back_info[1])                                 #阻力线截距

                                #若上一次旗形为空，即此次旗形并非突破而来，则从阻力起始点开始计算经过距离
                                if len(last_back_info) == 0:
                                    flag_info.append(high_points[0][high_len-1] - low_points[0][0])       #阻力线经过时间戳数量
                                    flag_info.append(high_points[2][high_len-1] - low_points[2][0])       #阻力线经过价格
                                #否则以上一阻力线突破点计算经过距离，突破点由第一低点横坐标代入上一旗形方程计算所得
                                else:
                                    break_point_price = last_back_info[0] * high_points[0][0] + last_back_info[1]
                                    flag_info.append(high_points[0][high_len-1] - low_points[0][0])
                                    flag_info.append(high_points[2][high_len-1] - break_point_price)

                                    result_len = len(results)
                                    if result_len > 0:
                                        results[result_len - 1][18] = high_points[0][high_len-1] - low_points[0][0]
                                        results[result_len - 1][19] = high_points[2][high_len-1] - break_point_price

                                flag_info.append(0)                                                 #阻力线突破后经过时间戳数量（暂空）
                                flag_info.append(0)                                                 #阻力线突破后经过价格（暂空）

                                #将此次阻力线信息存入集合
                                results.append(flag_info)

                                #清空阻力线信息以便下次接收
                                flag_info = []

                                #记录此次线性回归方程斜率和截距
                                last_back_info = []
                                last_back_info.extend(low_back_info)
                            else:
                                #上一次旗形非空，以上一阻力线突破点计算经过距离，突破点由第一低点横坐标代入上一旗形方程计算所得
                                if len(last_back_info) > 0:
                                    break_point_price = last_back_info[0] * high_points[0][0] + last_back_info[1]

                                    result_len = len(results)
                                    if result_len > 0:
                                        results[result_len - 1][18] = high_points[0][high_len-1] - low_points[0][0]
                                        results[result_len - 1][19] = high_points[2][high_len-1] - break_point_price

                                last_back_info = []

                            #此次旗形已结束，更新高低点集合，最新点为第一低点，原旗形最后一点为第一高点
                            low_points = [[],[],[]]
                            low_points[0].append(high_low[1])
                            low_points[1].append(high_low[2])
                            low_points[2].append(high_low[3])                         
                            high_points[0] = high_points[0][high_len-1:]
                            high_points[1] = high_points[1][high_len-1:]
                            high_points[2] = high_points[2][high_len-1:]

                            #突破发生则清空临时低点集合
                            temp_high_points = [[],[],[]]
                            temp_low_points = [[],[],[]]

                            #清空此次方程斜率和截距
                            high_back_info = []
                            low_back_info = []
                        #若高点斜率向下则重新统计斜率
                        else:
                            log.WriteLog("break", "cross:%u" % high_low[2])

                            temp_low_points = [[],[],[]]
                            temp_low_points[0].append(low_points[0][low_len-1])
                            temp_low_points[1].append(low_points[1][low_len-1])
                            temp_low_points[2].append(low_points[2][low_len-1])
                            temp_low_points[0].append(high_low[1])
                            temp_low_points[1].append(high_low[2])
                            temp_low_points[2].append(high_low[3])
                            low_back_info = calc_average_back(temp_low_points[0], temp_low_points[2])

                            if low_back_info[0] < 0:
                                change_turning = True

                            low_points[0].append(high_low[1])
                            low_points[1].append(high_low[2])
                            low_points[2].append(high_low[3])                            
                #若实际价格偏离目标价格2.5%以上，则判断该点不属于当前方程
                elif (high_low[3] - tar_price) > tar_price * 0.03:
                    #无论斜率方向如何，方程斜率变高，需去除旧的低点，用最后一个旧低点与最新一点做线性回归运算
                    temp_low_points = [[],[],[]]
                    temp_low_points[0].append(low_points[0][low_len-1])
                    temp_low_points[1].append(low_points[1][low_len-1])
                    temp_low_points[2].append(low_points[2][low_len-1])
                    temp_low_points[0].append(high_low[1])
                    temp_low_points[1].append(high_low[2])
                    temp_low_points[2].append(high_low[3])
                    low_back_info = calc_average_back(temp_low_points[0], temp_low_points[2])

                    #在斜率本就大于0的情况下变大，不可能出现斜率转向
                    #只有在斜率小于0的情况下变大，才可能出现斜率转向
                    if a < 0 and low_back_info[0] > 0:
                        change_turning = True

                    low_points[0].append(high_low[1])
                    low_points[1].append(high_low[2])
                    low_points[2].append(high_low[3])
                #若实际价格未偏离目标的2.5%以上，则加入线性回归方程计算 
                else:
                    low_points[0].append(high_low[1])
                    low_points[1].append(high_low[2])
                    low_points[2].append(high_low[3])

                    #若经过斜率偏离的重新计算，则以高点临时集合进行计算
                    if len(temp_low_points[0]) > 0:
                        temp_low_points[0].append(high_low[1])
                        temp_low_points[1].append(high_low[2])
                        temp_low_points[2].append(high_low[3])
                        low_back_info = calc_average_back(temp_low_points[0], temp_low_points[2])
                    #否则在原先的高点集合中计算
                    else:
                        low_back_info = calc_average_back(low_points[0], low_points[2])

                    #此种情况下可以出现任意斜率转向的情况
                    if a > 0 and low_back_info[0] < 0 or a < 0 and low_back_info[0] > 0:
                        change_turning = True

        #考虑线性回归方程斜率的各种情况，筛选出突破后未能形成旗形的情况
        #1.高点方程尚未成型而低点方程已成型
        if len(high_back_info) == 0 and len(low_back_info) > 0:
            #若上一旗形线性回归方程与低点方程方向一致(在此情况下理论上只会出现上一旗形方程与低点方程
            #斜率都小于0的情况)，说明突破失败
            if len(last_back_info) > 0:
                if last_back_info[0] < 0 and low_back_info[0] < 0:
                    #填充上一旗形突破距离
                    high_len = len(high_points[0])
                    break_point_price = last_back_info[0] * high_points[0][high_len-1] + last_back_info[1]

                    #记录未转折就失败信息
                    log.WriteLog("break", "unsucc_point high\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                        high_low[1], high_low[2], high_low[3], break_point_price, last_back_info[0], last_back_info[1]))

                    result_len = len(results)
                    results[result_len - 1][18] = 0
                    results[result_len - 1][19] = high_points[2][high_len-1] - break_point_price

                    #清空清空方程斜率和截距
                    last_back_info = []
        #2.低点方程未成型而高点方程已成型
        elif len(low_back_info) == 0 and len(high_back_info) > 0:
            #若上一旗形线性回归方程与高点方程方向一致(在此情况下理论上只会出现上一旗形方程与低点方程
            #斜率都大于0的情况)，说明突破失败
            if len(last_back_info) > 0:
                if last_back_info[0] > 0 and high_back_info[0] > 0:
                    #填充上一旗形突破距离
                    low_len = len(low_points[0])
                    break_point_price = last_back_info[0] * low_points[0][low_len-1] + last_back_info[1]

                    #记录未转折就失败信息
                    log.WriteLog("break", "unsucc_point low\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                        high_low[1], high_low[2], high_low[3], break_point_price, last_back_info[0], last_back_info[1]))

                    result_len = len(results)
                    results[result_len - 1][18] = 0
                    results[result_len - 1][19] = break_point_price - low_points[2][low_len-1]

                    #清空清空方程斜率和截距
                    last_back_info = []
        #3.高低点方程都已成型，但方向不一致
        elif len(low_back_info) > 0 and len(high_back_info) > 0:
            if low_back_info[0] > 0 and high_back_info[0] < 0 or low_back_info[0] < 0 and high_back_info[0] > 0:
                #区分没有出现中途转向的情况和出现中途转向的情况
                #中途转向（说明突破后旗形发展了一段时间）
                if change_turning:
                    if len(last_back_info) > 0:
                        #上一旗形向上的情况下
                        if last_back_info[0] > 0:
                            #填充上一旗形突破距离
                            low_len = len(low_points[0])
                            break_point_price = last_back_info[0] * low_points[0][0] + last_back_info[1]

                            #记录旗形成型转折失败信息
                            log.WriteLog("break", "unsucc_change low\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                high_low[1], high_low[2], high_low[3], break_point_price, last_back_info[0], last_back_info[1]))

                            #既然转向，则导致转向的那个点必然高于倒数第二点
                            result_len = len(results)
                            results[result_len - 1][18] = low_points[0][low_len-2] - low_points[0][0]
                            results[result_len - 1][19] = break_point_price - low_points[2][low_len-2]

                            temp_high_points = [[],[],[]]
                            temp_low_points = [[],[],[]]

                            high_len = len(high_points[0])
                            high_points[0] = high_points[0][high_len-1:]
                            high_points[1] = high_points[1][high_len-1:]
                            high_points[2] = high_points[2][high_len-1:]
                            low_points[0] = low_points[0][low_len-2:]
                            low_points[1] = low_points[1][low_len-2:]
                            low_points[2] = low_points[2][low_len-2:]

                            low_back_info = calc_average_back(low_points[0], low_points[2])
                            high_back_info = []
                        #上一旗形向下的情况下
                        elif last_back_info[0] < 0:
                            #填充上一旗形突破距离
                            high_len = len(high_points[0])
                            break_point_price = last_back_info[0] * high_points[0][0] + last_back_info[1]

                            #记录旗形成型转折失败信息
                            log.WriteLog("break", "unsucc_change high\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                high_low[1], high_low[2], high_low[3], break_point_price, last_back_info[0], last_back_info[1]))

                            #既然转向，则导致转向的那个点必然低于倒数第二点
                            result_len = len(results)
                            results[result_len - 1][18] = high_points[0][high_len-2] - high_points[0][0]
                            results[result_len - 1][19] = high_points[2][high_len-2] - break_point_price

                            temp_high_points = [[],[],[]]
                            temp_low_points = [[],[],[]]

                            low_len = len(low_points[0])
                            low_points[0] = low_points[0][low_len-1:]
                            low_points[1] = low_points[1][low_len-1:]
                            low_points[2] = low_points[2][low_len-1:]
                            high_points[0] = high_points[0][high_len-2:]
                            high_points[1] = high_points[1][high_len-2:]
                            high_points[2] = high_points[2][high_len-2:]

                            high_back_info = calc_average_back(high_points[0], high_points[2])
                            low_back_info = []

                        #清空清空方程斜率和截距
                        last_back_info = []
                #并非中途转向（说明旗形一开始就未成型）
                else:
                    if len(last_back_info) > 0:
                        #上一旗形向上的情况下
                        if last_back_info[0] > 0:
                            #填充上一旗形突破距离
                            low_len = len(low_points[0])
                            break_point_price = last_back_info[0] * low_points[0][0] + last_back_info[1]

                            #记录旗形未成型转折失败信息
                            log.WriteLog("break", "unsucc_line low\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                high_low[1], high_low[2], high_low[3], break_point_price, last_back_info[0], last_back_info[1]))

                            result_len = len(results)
                            results[result_len - 1][18] = 0
                            results[result_len - 1][19] = break_point_price - low_points[2][0]

                            high_len = len(high_points[0])
                            high_points[0] = high_points[0][high_len-1:]
                            high_points[1] = high_points[1][high_len-1:]
                            high_points[2] = high_points[2][high_len-1:]

                            high_back_info = []
                        #上一旗形向下的情况下
                        elif last_back_info[0] < 0:
                            #填充上一旗形突破距离
                            high_len = len(high_points[0])
                            break_point_price = last_back_info[0] * high_points[0][0] + last_back_info[1]

                            #记录旗形未成型转折失败信息
                            log.WriteLog("break", "unsucc_line high\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                high_low[1], high_low[2], high_low[3], break_point_price, last_back_info[0], last_back_info[1]))

                            result_len = len(results)
                            results[result_len - 1][18] = 0
                            results[result_len - 1][19] = high_points[2][0] - break_point_price

                            low_len = len(low_points[0])
                            low_points[0] = low_points[0][low_len-1:]
                            low_points[1] = low_points[1][low_len-1:]
                            low_points[2] = low_points[2][low_len-1:]

                            low_back_info = []

                        #清空清空方程斜率和截距
                        last_back_info = []
            else:
                #只需考虑转向后高低线性回归方程斜率变一致的情况
                if change_turning:
                    if high_low[0] == "high":
                        high_len = len(high_points[0])
                        high_points[0] = high_points[0][high_len-2:]
                        high_points[1] = high_points[1][high_len-2:]
                        high_points[2] = high_points[2][high_len-2:]

                        high_back_info = calc_average_back(high_points[0], high_points[2])

                        low_len = len(low_points[0])
                        low_points[0] = low_points[0][low_len-2:]
                        low_points[1] = low_points[1][low_len-2:]
                        low_points[2] = low_points[2][low_len-2:]

                        low_back_info = calc_average_back(low_points[0], low_points[2])

                        #记录旗形重新成型信息
                        log.WriteLog("break", "resucc high\ttime:%u\ttime:%u\treal:%f\tslope:%f\tintercept:%f" % (high_low[1], high_low[2], 
                            high_low[3], low_back_info[0], low_back_info[1]))
                    elif high_low[0] == "low":
                        low_len = len(low_points[0])
                        low_points[0] = low_points[0][low_len-2:]
                        low_points[1] = low_points[1][low_len-2:]
                        low_points[2] = low_points[2][low_len-2:]

                        low_back_info = calc_average_back(low_points[0], low_points[2])

                        high_len = len(high_points[0])
                        high_points[0] = high_points[0][high_len-2:]
                        high_points[1] = high_points[1][high_len-2:]
                        high_points[2] = high_points[2][high_len-2:]

                        high_back_info = calc_average_back(high_points[0], high_points[2])

                        #记录旗形重新成型信息
                        log.WriteLog("break", "resucc low\ttime:%u\ttime:%u\treal:%f\tslope:%f\tintercept:%f" % (high_low[1], high_low[2], 
                            high_low[3], high_back_info[0], high_back_info[1]))

                    temp_high_points = [[],[],[]]
                    temp_low_points = [[],[],[]]

                    last_back_info = []

    return results


def main():
    high_low_set = read_high_low("rb_high_low_producer_high_low.log")
    results = traverse(high_low_set)
    with open ("result.txt", "wb") as fp:
        for flag_info in results:
            # fp.write("idx:%u\ttype:%s\ttime:%u\tprice:%f\tSlope:%f\tIntercept:%f\tkeep_idxs:%u\tkeep_prices:%f\tbreak_idxs:%u\tbreak_prices:%f\n" % 
            #  (flag_info[0], "high" if flag_info[1] == 0 else "low", flag_info[2], flag_info[3], flag_info[4], flag_info[5], flag_info[6], \
            #  flag_info[7], flag_info[8], flag_info[9]))
            print flag_info
            fp.write("%u\t%f\t%u\t%f\t%u\t%f\t%u\t%f\n" % (flag_info[4], flag_info[5], flag_info[6], flag_info[7],flag_info[10], 
                flag_info[11], flag_info[12], flag_info[13]))


if __name__ == '__main__':
    main()