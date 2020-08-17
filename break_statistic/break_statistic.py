import log

#与线性回归线偏离百分比极值
OFFSET_RATE = 0.03
#最大斜率，斜率超过此的旗形都过滤
MAX_SLOPE = 9

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


class HighLowParser(object):
    """docstring for high_low_parser"""
    def __init__(self):
        super(HighLowParser, self).__init__()

        #统计结果
        self.results = []
        #当前正统计中的旗形
        self.flag_info = []
        #上一旗形线性回归斜率和截距（无需区分高低）
        self.last_back_info = []
        #旗形线性回归斜率和截距，分高点和低点两种情况
        self.back_info = {"high":[],"low":[]}
        #旗形高低点的时间索引、时间戳、价格
        self.points = {"high":[[],[],[]],"low":[[],[],[]]}
        #临时旗形高低点的时间索引、时间戳、价格
        self.temp_points = {"high":[[],[],[]],"low":[[],[],[]]}
        #读取的高低点坐标
        self.high_low_set = []
        #线性回归线中途是否转向
        self.change_turning = False


    #读取高低点信息
    def read_high_low(self, filename):
        self.high_low_set = []
        with open(filename, "rb") as fp:
            line = fp.readline()
            while line:
                eles = line.split('\t')
                self.high_low_set.append([eles[0], int(eles[1]), int(eles[2]), float(eles[3])])

                line = fp.readline()


    def process_point(self, high_low):
        self.temp_points = {"high":[[],[],[]],"low":[[],[],[]]}
        self.change_turning = False
        point_type = high_low[0]
        other_point_type = "low" if point_type == "high" else "high"
        other_points_len = len(self.points[other_point_type][0])
        points_len = len(self.points[point_type][0])
        #在极值点达到2个以前，不进行是否加入线性回归方程的判断
        if points_len < 2:
            self.points[point_type][0].append(high_low[1])
            self.points[point_type][1].append(high_low[2])
            self.points[point_type][2].append(high_low[3])
            #在极值达到2个的时候，计算初始线性回归方程信息
            if points_len == 1:
                for i in xrange(0,len(self.points[point_type][0])):
                    log.WriteLog("points", "type:%s\tpoint_idx:%u\tpoint_time:%u\tpoint_price:%f" % (point_type, self.points[point_type][0][i], 
                        self.points[point_type][1][i], self.points[point_type][2][i]))

                self.back_info[point_type] = calc_average_back(self.points[point_type][0], self.points[point_type][2])

                log.WriteLog("function", "point:%f\tslope:%f\tintercept:%f" % (high_low[2], self.back_info[point_type][0], 
                    self.back_info[point_type][1]))
        #在极值点达到2个后，从第3个点开始，进行是否加入方程的判断
        else:
            a = self.back_info[point_type][0]
            b = self.back_info[point_type][1]

            #以线性回归方程做计算，算出时间索引对应下的目标价格
            tar_price = a * high_low[1] + b
            #若实际价格偏离目标价格2.5%以上，则判断该点不属于当前方程
            if (point_type == "high" and (high_low[3] - tar_price) > tar_price * OFFSET_RATE) \
                or (point_type == "low" and (tar_price - high_low[3]) > tar_price * OFFSET_RATE):
                #若斜率与偏离方向同向，则方程斜率绝对值变大，需去除旧的高点，用最后一个旧高点与最新一点做线性回归运算
                if point_type == "high" and a > 0 or point_type == "low" and a < 0:
                    #在斜率往原本方向同一方向偏离时，不可能出现斜率转向
                    self.temp_points[point_type] = [[],[],[]]
                    self.temp_points[point_type][0].append(self.points[point_type][0][points_len-1])
                    self.temp_points[point_type][1].append(self.points[point_type][1][points_len-1])
                    self.temp_points[point_type][2].append(self.points[point_type][2][points_len-1])
                    self.temp_points[point_type][0].append(high_low[1])
                    self.temp_points[point_type][1].append(high_low[2])
                    self.temp_points[point_type][2].append(high_low[3])                        
                    self.back_info[point_type] = calc_average_back(self.temp_points[point_type][0], self.temp_points[point_type][2])

                    self.points[point_type][0].append(high_low[1])
                    self.points[point_type][1].append(high_low[2])
                    self.points[point_type][2].append(high_low[3])   
                #若斜率与偏离方向不同向，则考虑另一线性回归线的情况
                else:
                    #若另一线性回归线与原线性回归线同向则突破成功
                    if (other_point_type == "low" and len(self.back_info[other_point_type]) and self.back_info[other_point_type][0]) < 0 \
                        or (other_point_type == "high" and len(self.back_info[other_point_type]) and self.back_info[other_point_type][0] > 0):
                        if abs(a) <= MAX_SLOPE:
                            #记录突破信息
                            if len(self.last_back_info) > 0:
                                log.WriteLog("break", "break %s\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                    point_type, high_low[1], high_low[2], high_low[3], tar_price, self.last_back_info[0], 
                                    self.last_back_info[1]))
                            else:
                                log.WriteLog("break", "break %s\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f" % (point_type, high_low[1], 
                                    high_low[2], high_low[3], tar_price))

                            #记录突破时高低点坐标，斜率与截距
                            log.WriteLog("function", "%s:time:%u\tslope:%f\tintercept:%f\t%s:time:%u\tslope:%f\tintercept:%f" % (point_type, 
                                self.points[point_type][1][0], self.back_info[point_type][0], self.back_info[point_type][1], other_point_type, 
                                self.points[other_point_type][1][0], self.back_info[other_point_type][0], 
                                self.back_info[other_point_type][1]))

                            #以突破点横坐标为横坐标找出延长点坐标
                            extend_price = self.back_info[point_type][0] * high_low[1] + self.back_info[point_type][1]
                            other_extend_price = self.back_info[other_point_type][0] * high_low[1] + self.back_info[other_point_type][1]

                            #先记录此次旗形信息
                            self.flag_info.append(self.points[point_type][0][0])                     #阻力线起始点时间戳索引
                            self.flag_info.append(0 if point_type == "high" else 1)                  #阻力线起始点类型0为最高值 1为最低值
                            self.flag_info.append(self.points[point_type][1][0])                     #阻力线起始点时间戳
                            self.flag_info.append(self.points[point_type][2][0])                     #阻力线起始点价格
                            if len(self.temp_points[point_type][0]) > 0:
                                self.flag_info.append(self.temp_points[point_type][1][0])
                                self.flag_info.append(self.temp_points[point_type][2][0])
                            else:
                                self.flag_info.append(self.points[point_type][1][0])
                                self.flag_info.append(self.points[point_type][2][0])
                            self.flag_info.append(high_low[2])                                       #阻力线结束点时间戳
                            self.flag_info.append(extend_price)                                      #阻力线结束点价格
                            self.flag_info.append(self.points[other_point_type][1][0])               #阻力线起始点时间戳
                            self.flag_info.append(self.points[other_point_type][2][0])               #阻力线起始点价格
                            if len(self.temp_points[other_point_type][0]) > 0:
                                self.flag_info.append(self.temp_points[other_point_type][1][0])
                                self.flag_info.append(self.temp_points[other_point_type][2][0])
                            else:
                                self.flag_info.append(self.points[other_point_type][1][0])
                                self.flag_info.append(self.points[other_point_type][2][0])
                            self.flag_info.append(high_low[2])                                       #阻力线结束点时间戳
                            self.flag_info.append(other_extend_price)                                #阻力线结束点价格                            
                            self.flag_info.append(self.back_info[point_type][0])                        #阻力线斜率
                            self.flag_info.append(self.back_info[point_type][1])                        #阻力线截距

                            #若上一次旗形为空，即此次旗形并非突破而来，则从阻力起始点开始计算经过距离
                            if len(self.last_back_info) == 0:
                                self.flag_info.append(self.points[other_point_type][0][other_points_len-1] - self.points[point_type][0][0])      #阻力线经过时间戳数量
                                self.flag_info.append(self.points[point_type][2][0] - self.points[other_point_type][2][other_points_len-1])      #阻力线经过价格
                            #否则以上一阻力线突破点计算经过距离，突破点由第一低点横坐标代入上一旗形方程计算所得
                            else:
                                break_point_price = self.last_back_info[0] * self.points[other_point_type][0][0] + self.last_back_info[1]
                                self.flag_info.append(self.points[other_point_type][0][other_points_len-1] - self.points[other_point_type][0][0])
                                self.flag_info.append(break_point_price - self.points[other_point_type][2][other_points_len-1])

                                result_len = len(self.results)
                                if result_len > 0:
                                    self.results[result_len - 1][18] = self.points[other_point_type][0][other_points_len-1] - self.points[other_point_type][0][0]
                                    self.results[result_len - 1][19] = break_point_price - self.points[other_point_type][2][other_points_len-1]

                            self.flag_info.append(0)                                                 #阻力线突破后经过时间戳数量（暂空）
                            self.flag_info.append(0)                                                 #阻力线突破后经过价格（暂空）

                            #将此次阻力线信息存入集合
                            self.results.append(self.flag_info)

                            #清空阻力线信息以便下次接收
                            self.flag_info = []

                            #记录此次线性回归方程斜率和截距
                            self.last_back_info = []
                            self.last_back_info.extend(self.back_info[point_type])
                        else:
                            #上一次旗形非空，以上一阻力线突破点计算经过距离，突破点由第一低点横坐标代入上一旗形方程计算所得
                            if len(self.last_back_info) > 0:
                                break_point_price = self.last_back_info[0] * self.points[other_point_type][0][0] + self.last_back_info[1]

                                result_len = len(self.results)
                                if result_len > 0:
                                    self.results[result_len - 1][18] = self.points[other_point_type][0][other_points_len-1] - self.points[other_point_type][0][0]
                                    self.results[result_len - 1][19] = break_point_price - self.points[other_point_type][2][other_points_len-1]

                            self.last_back_info = []

                        #此次旗形已结束，更新高低点集合，最新点为第一高点，原旗形最后一点为第一低点
                        self.points[point_type] = [[],[],[]]
                        self.points[point_type][0].append(high_low[1])
                        self.points[point_type][1].append(high_low[2])
                        self.points[point_type][2].append(high_low[3])                         
                        self.points[other_point_type][0] = self.points[other_point_type][0][other_points_len-1:]
                        self.points[other_point_type][1] = self.points[other_point_type][1][other_points_len-1:]
                        self.points[other_point_type][2] = self.points[other_point_type][2][other_points_len-1:]

                        #突破发生则清空临时极值点集合
                        self.temp_points[point_type] = [[],[],[]]
                        self.temp_points[other_point_type] = [[],[],[]]

                        #清空此次方程斜率和截距
                        self.back_info[point_type] = []
                        self.back_info[other_point_type] = []
                    #若低点斜率向上则重新统计斜率
                    else:
                        log.WriteLog("break", "cross:%u" % high_low[2])

                        self.temp_points[point_type] = [[],[],[]]
                        self.temp_points[point_type][0].append(self.points[point_type][0][points_len-1])
                        self.temp_points[point_type][1].append(self.points[point_type][1][points_len-1])
                        self.temp_points[point_type][2].append(self.points[point_type][2][points_len-1])
                        self.temp_points[point_type][0].append(high_low[1])
                        self.temp_points[point_type][1].append(high_low[2])
                        self.temp_points[point_type][2].append(high_low[3])
                        self.back_info[point_type] = calc_average_back(self.temp_points[point_type][0], self.temp_points[point_type][2])

                        if self.back_info[point_type][0] > 0:
                            self.change_turning = True

                        self.points[point_type][0].append(high_low[1])
                        self.points[point_type][1].append(high_low[2])
                        self.points[point_type][2].append(high_low[3])
            #若实际价格偏离目标价格3%以上，则判断该点不属于当前方程
            elif point_type == "high" and (tar_price - high_low[3]) > tar_price * OFFSET_RATE \
                or point_type == "low" and (high_low[3] - tar_price) > tar_price * OFFSET_RATE:
                #无论斜率方向如何，方程斜率变低，需去除旧的高点，用最后一个旧高点与最新一点做线性回归运算
                self.temp_points[point_type] = [[],[],[]]
                self.temp_points[point_type][0].append(self.points[point_type][0][points_len-1])
                self.temp_points[point_type][1].append(self.points[point_type][1][points_len-1])
                self.temp_points[point_type][2].append(self.points[point_type][2][points_len-1])
                self.temp_points[point_type][0].append(high_low[1])
                self.temp_points[point_type][1].append(high_low[2])
                self.temp_points[point_type][2].append(high_low[3])
                self.back_info[point_type] = calc_average_back(self.temp_points[point_type][0], self.temp_points[point_type][2])

                #只有在斜率大于0的情况下变小或斜率小于0的情况下变大，才可能出现斜率转向
                if point_type == "high" and a > 0 and self.back_info[point_type][0] < 0 \
                    or point_type == "low" and a < 0 and self.back_info[point_type][0] > 0:
                    self.change_turning = True

                self.points[point_type][0].append(high_low[1])
                self.points[point_type][1].append(high_low[2])
                self.points[point_type][2].append(high_low[3])
            #若实际价格未偏离目标的3%以上，则加入线性回归方程计算 
            else:
                self.points[point_type][0].append(high_low[1])
                self.points[point_type][1].append(high_low[2])
                self.points[point_type][2].append(high_low[3])

                #若经过斜率偏离的重新计算，则以高点临时集合进行计算
                if len(self.temp_points[point_type][0]) > 0:
                    self.temp_points[point_type][0].append(high_low[1])
                    self.temp_points[point_type][1].append(high_low[2])
                    self.temp_points[point_type][2].append(high_low[3])
                    self.back_info[point_type] = calc_average_back(self.temp_points[point_type][0], self.temp_points[point_type][2])
                #否则在原先的高点集合中计算
                else:
                    self.back_info[point_type] = calc_average_back(self.points[point_type][0], self.points[point_type][2])

                #此种情况下可以出现任意斜率转向的情况
                if a > 0 and self.back_info[point_type][0] < 0 or a < 0 and self.back_info[point_type][0] > 0:
                    self.change_turning = True


    def ProcessAfterProcess(self, high_low):
        #考虑线性回归方程斜率的各种情况，筛选出突破后未能形成旗形的情况
        #1.高点方程尚未成型而低点方程已成型
        if len(self.back_info["high"]) == 0 and len(self.back_info["low"]) > 0:
            #若上一旗形线性回归方程与低点方程方向一致(在此情况下理论上只会出现上一旗形方程与低点方程
            #斜率都小于0的情况)，说明突破失败
            if len(self.last_back_info) > 0:
                if self.last_back_info[0] < 0 and self.back_info["low"][0] < 0:
                    #填充上一旗形突破距离
                    high_len = len(self.points["high"][0])
                    break_point_price = self.last_back_info[0] * self.points["high"][0][high_len-1] + self.last_back_info[1]

                    #记录未转折就失败信息
                    log.WriteLog("break", "unsucc_point high\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                        high_low[1], high_low[2], high_low[3], break_point_price, self.last_back_info[0], self.last_back_info[1]))

                    result_len = len(self.results)
                    self.results[result_len - 1][18] = 0
                    self.results[result_len - 1][19] = self.points["high"][2][high_len-1] - break_point_price

                    #清空清空方程斜率和截距
                    self.last_back_info = []
        #2.低点方程未成型而高点方程已成型
        elif len(self.back_info["low"]) == 0 and len(self.back_info["high"]) > 0:
            #若上一旗形线性回归方程与高点方程方向一致(在此情况下理论上只会出现上一旗形方程与低点方程
            #斜率都大于0的情况)，说明突破失败
            if len(self.last_back_info) > 0:
                if self.last_back_info[0] > 0 and self.back_info["high"][0] > 0:
                    #填充上一旗形突破距离
                    low_len = len(self.points["low"][0])
                    break_point_price = self.last_back_info[0] * self.points["low"][0][low_len-1] + self.last_back_info[1]

                    #记录未转折就失败信息
                    log.WriteLog("break", "unsucc_point low\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                        high_low[1], high_low[2], high_low[3], break_point_price, self.last_back_info[0], self.last_back_info[1]))

                    result_len = len(self.results)
                    self.results[result_len - 1][18] = 0
                    self.results[result_len - 1][19] = break_point_price - self.points["low"][2][low_len-1]

                    #清空清空方程斜率和截距
                    self.last_back_info = []
        #3.高低点方程都已成型，但方向不一致
        elif len(self.back_info["low"]) > 0 and len(self.back_info["high"]) > 0:
            if self.back_info["low"][0] > 0 and self.back_info["high"][0] < 0 or self.back_info["low"][0] < 0 and self.back_info["high"][0] > 0:
                #区分没有出现中途转向的情况和出现中途转向的情况
                #中途转向（说明突破后旗形发展了一段时间）
                if self.change_turning:
                    if len(self.last_back_info) > 0:
                        #上一旗形向上的情况下
                        if self.last_back_info[0] > 0:
                            #填充上一旗形突破距离
                            low_len = len(self.points["low"][0])
                            break_point_price = self.last_back_info[0] * self.points["low"][0][0] + self.last_back_info[1]

                            #记录旗形成型转折失败信息
                            log.WriteLog("break", "unsucc_change low\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                high_low[1], high_low[2], high_low[3], break_point_price, self.last_back_info[0], self.last_back_info[1]))

                            #既然转向，则导致转向的那个点必然高于倒数第二点
                            result_len = len(self.results)
                            self.results[result_len - 1][18] = self.points["low"][0][low_len-2] - self.points["low"][0][0]
                            self.results[result_len - 1][19] = break_point_price - self.points["low"][2][low_len-2]

                            self.temp_points["high"] = [[],[],[]]
                            self.temp_points["low"] = [[],[],[]]

                            high_len = len(self.points["high"][0])
                            self.points["high"][0] = self.points["high"][0][high_len-1:]
                            self.points["high"][1] = self.points["high"][1][high_len-1:]
                            self.points["high"][2] = self.points["high"][2][high_len-1:]
                            self.points["low"][0] = self.points["low"][0][low_len-2:]
                            self.points["low"][1] = self.points["low"][1][low_len-2:]
                            self.points["low"][2] = self.points["low"][2][low_len-2:]

                            self.back_info["low"] = calc_average_back(self.points["low"][0], self.points["low"][2])
                            self.back_info["high"] = []
                        #上一旗形向下的情况下
                        elif self.last_back_info[0] < 0:
                            #填充上一旗形突破距离
                            high_len = len(self.points["high"][0])
                            break_point_price = self.last_back_info[0] * self.points["high"][0][0] + self.last_back_info[1]

                            #记录旗形成型转折失败信息
                            log.WriteLog("break", "unsucc_change high\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                high_low[1], high_low[2], high_low[3], break_point_price, self.last_back_info[0], self.last_back_info[1]))

                            #既然转向，则导致转向的那个点必然低于倒数第二点
                            result_len = len(self.results)
                            self.results[result_len - 1][18] = self.points["high"][0][high_len-2] - self.points["high"][0][0]
                            self.results[result_len - 1][19] = self.points["high"][2][high_len-2] - break_point_price

                            self.temp_points["high"] = [[],[],[]]
                            self.temp_points["low"] = [[],[],[]]

                            low_len = len(self.points["low"][0])
                            self.points["low"][0] = self.points["low"][0][low_len-1:]
                            self.points["low"][1] = self.points["low"][1][low_len-1:]
                            self.points["low"][2] = self.points["low"][2][low_len-1:]
                            self.points["high"][0] = self.points["high"][0][high_len-2:]
                            self.points["high"][1] = self.points["high"][1][high_len-2:]
                            self.points["high"][2] = self.points["high"][2][high_len-2:]

                            self.back_info["high"] = calc_average_back(self.points["high"][0], self.points["high"][2])
                            self.back_info["low"] = []

                        #清空清空方程斜率和截距
                        self.last_back_info = []
                #并非中途转向（说明旗形一开始就未成型）
                else:
                    if len(self.last_back_info) > 0:
                        #上一旗形向上的情况下
                        if self.last_back_info[0] > 0:
                            #填充上一旗形突破距离
                            low_len = len(self.points["low"][0])
                            break_point_price = self.last_back_info[0] * self.points["low"][0][0] + self.last_back_info[1]

                            #记录旗形未成型转折失败信息
                            log.WriteLog("break", "unsucc_line low\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                high_low[1], high_low[2], high_low[3], break_point_price, self.last_back_info[0], self.last_back_info[1]))

                            result_len = len(self.results)
                            self.results[result_len - 1][18] = 0
                            self.results[result_len - 1][19] = break_point_price - self.points["low"][2][0]

                            high_len = len(self.points["high"][0])
                            self.points["high"][0] = self.points["high"][0][high_len-1:]
                            self.points["high"][1] = self.points["high"][1][high_len-1:]
                            self.points["high"][2] = self.points["high"][2][high_len-1:]

                            self.back_info["high"] = []
                        #上一旗形向下的情况下
                        elif self.last_back_info[0] < 0:
                            #填充上一旗形突破距离
                            high_len = len(self.points["high"][0])
                            break_point_price = self.last_back_info[0] * self.points["high"][0][0] + self.last_back_info[1]

                            #记录旗形未成型转折失败信息
                            log.WriteLog("break", "unsucc_line high\ttime_idx:%u\ttime:%u\treal:%f\ttar:%f\tlast_slope:%f\tlast_intercept:%f" % (
                                high_low[1], high_low[2], high_low[3], break_point_price, self.last_back_info[0], self.last_back_info[1]))

                            result_len = len(self.results)
                            self.results[result_len - 1][18] = 0
                            self.results[result_len - 1][19] = self.points["high"][2][0] - break_point_price

                            low_len = len(self.points["low"][0])
                            self.points["low"][0] = self.points["low"][0][low_len-1:]
                            self.points["low"][1] = self.points["low"][1][low_len-1:]
                            self.points["low"][2] = self.points["low"][2][low_len-1:]

                            self.back_info["low"] = []

                        #清空清空方程斜率和截距
                        self.last_back_info = []
            else:
                #只需考虑转向后高低线性回归方程斜率变一致的情况
                if self.change_turning:
                    if high_low[0] == "high":
                        high_len = len(self.points["high"][0])
                        self.points["high"][0] = self.points["high"][0][high_len-2:]
                        self.points["high"][1] = self.points["high"][1][high_len-2:]
                        self.points["high"][2] = self.points["high"][2][high_len-2:]

                        self.back_info["high"] = calc_average_back(self.points["high"][0], self.points["high"][2])

                        low_len = len(self.points["low"][0])
                        self.points["low"][0] = self.points["low"][0][low_len-2:]
                        self.points["low"][1] = self.points["low"][1][low_len-2:]
                        self.points["low"][2] = self.points["low"][2][low_len-2:]

                        self.back_info["low"] = calc_average_back(self.points["low"][0], self.points["low"][2])

                        #记录旗形重新成型信息
                        log.WriteLog("break", "resucc high\ttime:%u\ttime:%u\treal:%f\tslope:%f\tintercept:%f" % (high_low[1], high_low[2], 
                            high_low[3], self.back_info["low"][0], self.back_info["low"][1]))
                    elif high_low[0] == "low":
                        low_len = len(self.points["low"][0])
                        self.points["low"][0] = self.points["low"][0][low_len-2:]
                        self.points["low"][1] = self.points["low"][1][low_len-2:]
                        self.points["low"][2] = self.points["low"][2][low_len-2:]

                        self.back_info["low"] = calc_average_back(self.points["low"][0], self.points["low"][2])

                        high_len = len(self.points["high"][0])
                        self.points["high"][0] = self.points["high"][0][high_len-2:]
                        self.points["high"][1] = self.points["high"][1][high_len-2:]
                        self.points["high"][2] = self.points["high"][2][high_len-2:]

                        self.back_info["high"] = calc_average_back(self.points["high"][0], self.points["high"][2])

                        #记录旗形重新成型信息
                        log.WriteLog("break", "resucc low\ttime:%u\ttime:%u\treal:%f\tslope:%f\tintercept:%f" % (high_low[1], high_low[2], 
                            high_low[3], self.back_info["high"][0], self.back_info["high"][1]))

                        self.temp_points["high"] = [[],[],[]]
                        self.temp_points["low"] = [[],[],[]]

                    self.last_back_info = []


    def traverse(self):
        for high_low in self.high_low_set:
            self.process_point(high_low)
            self.ProcessAfterProcess(high_low)

        return self.results


def main():
    parser = HighLowParser()
    parser.read_high_low("rb_high_low_producer_high_low.log")
    results = parser.traverse()
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