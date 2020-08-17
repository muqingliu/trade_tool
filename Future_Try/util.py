import pandas as pd
import os,sys
import numpy
from pandas.tseries.offsets import DateOffset


def get_max(df, find_max):
    max_val = 0
    max_x = 0
    min_val = sys.float_info.max
    min_x = 0

    if find_max:
        for x in xrange(0,len(df)):
            if df[x].pt.MA5 > max_val:
                max_val = df[x].pt.MA5
                max_x = x
        return max_x
    else:
        for x in xrange(0,len(df)):
            if df[x].pt.MA5 < min_val:
                min_val = df[x].pt.MA5
                min_x = x
        return min_x

def Xval(data):
    '''
    get X axis value for figure
    '''
    if len(data.shape) == 2:  # list
        return list(data.index)
    else:
        return int(data.name)

class log_csv:
    logf = None

    def __init__(self, log_csv, titles, append=True):
        log_csv = 'save/' + log_csv + '.csv'
        save_title = not os.path.exists(log_csv)
        if append:
            self.logf = open(log_csv, 'a+')
        else:
            self.logf = open(log_csv, 'w')

        if save_title:
            if len(titles) > 1:
                titles_str = ','.join(map(str, titles))
            else:
                titles_str = str(titles[0])
            self.logf.write(titles_str)
            self.logf.write('\n')

    def __del__(self):
        if self.logf is not None:
            self.logf.close()

    def write(self, titles):
        if len(titles) > 1:
            titles_str = ','.join(map(str, titles))
        else:
            titles_str = str(titles[0])
        self.logf.write(titles_str)
        self.logf.write('\n')
        self.logf.flush()


class data_ohlc:
    df = None
    df_len = 0
    df_beg = 0
    df_total_len = 0

    def __init__(self, filen, original=False):
        if original:
            self.df = pd.read_csv('data/' + filen, sep='\t', header=None, names=['', 'O', 'H', 'L', 'C', 'V'], parse_dates={'D': [0]})
            self.df.D = self.df.D.apply(lambda x: x + DateOffset(days=1))
        else:
            self.df = pd.read_csv('data/' + filen + '_n.csv', index_col=0)

        self.df_len = len(self.df.index)
        self.df_total_len = self.df_len
        print(self.df.index)

        self.df = self.__MA(self.df, 5)
        pass


    def __del__(self):
        pass

    def __MA(self, df, n):
        df = df.join(pd.Series(df['C'].rolling(window=n,center=False).mean(), name='MA' + str(n)))
        # df = df.join(pd.Series(pd.rolling_mean(df['C'], n), name='MA' + str(n)))
        return df

    def set_range(self, begin=0, leng=0):
        self.df_beg = begin
        if leng > 0:
            self.df_len = self.df_beg + leng

            if self.df_len >= self.df_total_len:
                self.df_len = self.df_total_len
                self.df_beg = self.df_total_len - leng

    def update(self, func):
        for i in range(self.df_beg, self.df_len):
            df = self.df.iloc[self.df_beg:i]
            df.index = df.index - self.df_beg
            func(df)

    def get_range(self):
        df = self.df.iloc[self.df_beg:self.df_len]
        df.index = df.index - self.df_beg
        return df, len(df.index)

    def get_history(self, idx=-1):
        if idx >= self.df_len or idx < 0:
            df, leng = self.get_range()
            return df
        df = self.df.iloc[self.df_beg:self.df_beg + idx + 1]
        df.index = df.index - self.df_beg
        return df

class ptype:
    high = 0
    low = 1

class Pter:
    def __init__(self, pt, type):
        self.pt = pt
        self.type = type
        self.offset = 0

class PPointer:
    def __init__(self):
        self.Pter = []
        self.flag = []
        self.success_node = []
        self.minInterval = 50

    def update_offset(self, offset):
        for p in self.Pter:
            p.offset = p.offset + offset

    def is_success(self):
        size_pt = len(self.Pter)
        if size_pt < 5:
            return False

        if (self.Pter[1].type == ptype.low and self.Pter[3].pt.MA5 < self.Pter[1].pt.MA5)\
            or (self.Pter[1].type == ptype.high and self.Pter[3].pt.MA5 > self.Pter[1].pt.MA5):
            return True
        return False

    def push_success_node(self, pointers):
        nodes = [pointers[0], pointers[1], pointers[2], self.Pter[get_max(self.Pter, self.Pter[1].type == ptype.high)]]
        self.success_node.append(nodes)

    def push(self, dt):
        if numpy.isnan(dt.MA5):
            return

        if len(self.Pter) == 0:
            self.Pter.append(Pter(dt, ptype.low))
            return

        lastPT = self.Pter[-1]
        lastPT_y = lastPT.pt.MA5

        # 只间隔一个点跳过
        # if Xval(lastPT.pt) + 1 == Xval(dt):
        #     return

        # 继续刷新高低点
        if (lastPT.type == ptype.low and lastPT_y - dt.MA5 > 0)\
            or (lastPT.type == ptype.high and dt.MA5 - lastPT_y > 0):
            self.Pter[-1].pt = dt

            size_pt = len(self.Pter)

            # 刷新高低点时，破前高或前低，偶数点走错，奇数点这里不判断
            if size_pt % 2 != 0:
                if size_pt >= 5: # 超过3点的比较
                    print "@1", size_pt, self.Pter[1].type, self.Pter[-1].pt.MA5, self.Pter[-2].pt.MA5, self.Pter[-4].pt.MA5
                    if (self.Pter[1].type == ptype.low and self.Pter[-1].pt.MA5 > self.Pter[-3].pt.MA5)\
                        or (self.Pter[1].type == ptype.high and self.Pter[-1].pt.MA5 < self.Pter[-3].pt.MA5):

                        if self.is_success(): # 如果第3点形成，并且成功，则画线
                            self.flag.append((self.Pter[0].pt, 0))
                            self.flag.append((self.Pter[get_max(self.Pter, self.Pter[1].type == ptype.high)].pt, 1))
                            self.push_success_node(self.Pter)

                        self.Pter = self.Pter[-2:]
                        print "$1" * 10
                        return

                if size_pt >= 3:
                    print "@2", size_pt, self.Pter[1].type, self.Pter[-1].pt.MA5, self.Pter[-2].pt.MA5, self.Pter[-3].pt.MA5
                    if (self.Pter[1].type == ptype.low and self.Pter[-1].pt.MA5 > self.Pter[-3].pt.MA5)\
                        or (self.Pter[1].type == ptype.high and self.Pter[-1].pt.MA5 < self.Pter[-3].pt.MA5):
                        self.Pter = self.Pter[-2:]
                        print "$2" * 10
                        return

            # 判断是否延续状态
           # if size_pt == 6:
           #      if (self.Pter[-4].type == ptype.low and self.Pter[-2].pt.MA5 < self.Pter[-4].pt.MA5)\
           #          or (self.Pter[-4].type == ptype.high and self.Pter[-2].pt.MA5 > self.Pter[-4].pt.MA5):
           #          self.Pter = self.Pter[-3:]
           #          return
           #  return

        # 走势相反
        if (lastPT.type == ptype.low and  dt.MA5 - lastPT_y> self.minInterval)\
            or (lastPT.type == ptype.high and lastPT_y - dt.MA5 > self.minInterval):

            self.Pter.append(Pter(dt, 1 - lastPT.type))
            size_pt = len(self.Pter)
            print "add node",  size_pt

            # if size_pt == 5:
            #     self.flag.append((self.Pter[0].pt, 0))

if __name__ == '__main__':

    def update(df):
        print(df)

    ohlc = data_ohlc('lL0.txt', True)
    ohlc.set_range(0, 3)
    # print(ohlc.get_range()[0])
    print(ohlc.get_history())
    # ohlc.loop(update)


