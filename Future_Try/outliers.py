# import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
# from matplotlib import finance
import mpl_finance as finance

from matplotlib.collections import LineCollection

from util import data_ohlc, log_csv
from trade import trade
# http://ffmpeg.zeranoe.com/builds/


class PLTS:
    LN1 = 0
    LN2 = 1
    HI_LN = 2
    LO_LN = 3

    TD = 4  # today
    H = 5
    L = 6

    NUM = 7

plt.rcParams['animation.ffmpeg_path'] = u'.\\ffmpeg.exe'

# filen = '601318.XSHG.txt'
filen = 'lL0.txt'

fig = plt.figure()
ax = fig.add_subplot(111)
dohlc = data_ohlc(filen, True)
trd = trade()
plts = list(range(PLTS.NUM))
maxs = []
mins = []
csv = log_csv(filen, ['D', 'P'], False)

opened = [False, False]
seq = []


class V:
    summit_range = 15
    open_percentage = 0.5
    waiting_for_input = False


def Xval(data):
    '''
    get X axis value for figure
    '''
    if len(data.shape) == 2:  # list
        return list(data.index)
    else:
        return int(data.name)


def get_loc_summit(df, idx, rng, greater):
    for offset in range(1, rng + 1):
        val_b = df.iloc[idx - offset]
        val = df.iloc[idx]
        val_a = df.iloc[idx + 1]

        cond = False
        if greater:
            cond = (val.H > val_b.H) and (val.H > val_a.H)
        else:
            cond = (val.L < val_b.L) and (val.L < val_a.L)

        if not cond:
            return False

    return True


def get_summit(df, offset=1):
    max_val = 0
    max_x = 0
    min_val = sys.float_info.max
    min_x = 0

    len_df = len(df)
    for i in range(offset, len_df - 1):
        val = df.iloc[i]
        if get_loc_summit(df, i, offset, True):
            # print("%d(%d)<%d(%d)>%d(%d)" %(val_b.H, val_b.name, val.H,
            # val.name, val_a.H, val_a.name) )
            if val.H > max_val:
                max_val = val.H
                max_x = Xval(val)

        if get_loc_summit(df, i, offset, False):
            # print("%d(%d)>%d(%d)<%d(%d)" %(val_b.L, val_b.name, val.L,
            # val.name, val_a.L, val_a.name) )
            if val.L < min_val:
                min_val = val.L
                min_x = Xval(val)

    return (max_x, min_x)


def make_line(idx0, idx1, Ys, idxn):
    y0 = Ys[idx0]
    y1 = Ys[idx1]
    # print("idx1", idx1, "idx0", idx0, "y0:", y0, "y1:", y1)

    yn = (idxn - idx0) / (idx1 - idx0) * (y1 - y0) + y0
    return ((idx0, y0), (idxn, yn))


def is_point_inline(points, Ys):
    first = points[0]
    last = points[-1]
    for pt in points[1:-1]:
        xyxy = make_line(first, last, Ys, pt)
        real_y = Ys[pt]
        percent = abs(real_y - xyxy[1][1]) / real_y
        # print("%d-%d-%d :%f"%(first, pt, last, percent) )
        if percent >= 0.015:
            return False

    return True


def get_far_idxs(idxs, Ys):
    points = []
    len_idxs = len(idxs)
    for first in range(-3, -len_idxs - 1, -1):
        pts = idxs[first:]
        if is_point_inline(pts, Ys):
            # if line is None:
            # return points[-1]
            points.append(first)

    if len(points) == 0:
        return None
    return idxs[points[-1]]


def get_lines(idxs, Ys, today_idx):
    lines = []
    if len(idxs) >= 2:
        lines.append(make_line(idxs[-2], idxs[-1], Ys, today_idx))

    if len(idxs) >= 3:
        idx0 = get_far_idxs(idxs, Ys)
        if idx0 is not None:
            lines.append(make_line(idx0, idxs[-1], Ys, today_idx))

    return lines


def push_maxmin(lst, val):
    if val == 0:
        return lst
    if len(lst) > 0 and lst[-1] == val:
        return lst
    lst.append(val)
    return lst
    # if len(lst)>outlier_keep:
    #     lst = lst[-outlier_keep:]


def op_than_any(lst, func):
    if len(lst) == 0:
        return False
    for i in lst:
        if func(i):
            return True
    return False


def op_than_all(lst, func):
    if len(lst) == 0:
        return False
    for i in lst:
        if not func(i):
            return False
    return True


def open_per(today, typ=''):
    date = today.D.strftime('%y.%m.%d')
    if typ == 'UP' and (not opened[0]):
        num = trd.get_max_holds(today.H)
        trd.open('UP', today.H, num * V.open_percentage, ds=date)
        opened[0] = True

    if typ == 'DN' and (not opened[1]):
        num = trd.get_max_holds(today.L)
        trd.open('DN', today.L, num * V.open_percentage, ds=date)
        opened[1] = True


def close_all(today, typ=''):
    date = today.D.strftime('%y.%m.%d')
    if typ == 'UP' or typ == '':
        if opened[0]:
            trd.close('UP', today.H, ds=date)
            opened[0] = False

    if typ == 'DN' or typ == '':
        if opened[1]:
            trd.close('DN', today.L, ds=date)
            opened[1] = False


def trade_logic(today, lns_h, lns_l):
    # print()
    global seq

    highs = np.array([[x1, y1] for (x0, y0), (x1, y1) in lns_h])
    lows = np.array([[x1, y1] for (x0, y0), (x1, y1) in lns_l])
    # print('highs:', highs, 'lows:', lows)

    # for h in highs:
    #     if op_than_any(lows, lambda v: h <= v):
    # close_all(today)
    #         return

    # for l in lows:
    #     if op_than_any(highs, lambda v: l >= v):
    # close_all(today)
    #         return

    gtm = op_than_all(highs, lambda v: today.H >= v[1])
    ltm = op_than_all(lows, lambda v: today.L <= v[1])
    if gtm:
        open_per(today, 'UP')
    else:
        close_all(today)

    csv.write([today.D.strftime('%y/%m/%d'), trd.get_fund_tital(today.C, 0)])
    return

    today_h = today.H * (1 - 0.001)
    today_l = today.L * (1 - 0.001)
    # print('today_h:', today_h, 'today_l:', today_l)
    gt = op_than_all(highs, lambda v: today_h >= v[1])
    lt = op_than_all(lows, lambda v: today_l <= v[1])
    # print("gt:", gt, gtm, "  lt:", lt, ltm)

    if (not gtm) and (not ltm):
        print(seq)
        seq.append('MI')
    elif gt:
        print(seq)
        seq.append('HI')
    elif lt:
        print(seq)
        seq.append('LO')

    if len(seq) > 5:
        seq = seq[-5:]

    if len(seq) > 0:
        if seq[-1] == 'HI':
            close_all(today)
            open_per(today, 'UP')
        if seq[-1] == 'LO':
            close_all(today)
            open_per(today, 'DN')

    if len(seq) > 1:
        if seq[-1] == 'MI':
            close_all(today)
            if seq[-2] == 'HI':
                print('HI.MI')
                open_per(today, 'DN')
            if seq[-2] == 'LO':
                print('LO.MI')
                open_per(today, 'UP')


def update(frame, *fargs):
    global maxs, mins, gAnim

    draw_prices()


    df = dohlc.get_history(frame)
    if len(df) == 0:
        return plts

    # today indecator
    dt_td = df.iloc[-1]
    plts[PLTS.TD].set_data(Xval(dt_td), dt_td.C)

    # outlier of last n days
    sr = V.summit_range
    (mai, mii) = get_summit(df[-sr:])
    maxs = push_maxmin(maxs, mai)
    mins = push_maxmin(mins, mii)

    if len(maxs) == 0:
        return plts

    dt = df.loc[maxs]
    plts[PLTS.H].set_data(Xval(dt), list(dt.H))
    dt = df.loc[mins]
    plts[PLTS.L].set_data(Xval(dt), list(dt.L))

    rng_df, leng = dohlc.get_range()

    # high/low lines:
    lns_h = get_lines(maxs, rng_df.H, dt_td.name + 1)
    plts[PLTS.HI_LN].set_paths(lns_h)

    lns_l = get_lines(mins, rng_df.L, dt_td.name + 1)
    plts[PLTS.LO_LN].set_paths(lns_l)

    trade_logic(dt_td, lns_h, lns_l)
    # prices moves as realtime:
    # plts[PLTS.LN1].set_data(list(rng_df.D), list(rng_df.C))
    # ax.set_title(dt_td.D.strftime('%d-%m-%Y') )

    if V.waiting_for_input:
        gAnim.paused = True
    return plts


def draw_prices():
    rng_df, leng = dohlc.get_range()

    plts[PLTS.LN1], plts[PLTS.LN2] = finance.candlestick2_ohlc(
        ax, list(rng_df.O), list(rng_df.H), list(rng_df.L), list(rng_df.C),
        width=0.5,
        colordown='g', colorup='r')

    # fig.autofmt_xdate()

    dt = rng_df.index[::leng / 20]
    datestrs = [d.strftime('%y.%m.%d') for d in rng_df.D[dt]]

    ax.set_xticks(dt)
    ax.set_xlim(dt[0], dt[-1])

    ax.set_xticklabels(datestrs, rotation=70)


def press(e):
    global gAnim
    if e.key == ' ':
        gAnim.paused = not gAnim.paused


def init_fig_lines():
    ax.grid(True, color='b')

    plts[PLTS.HI_LN] = LineCollection([], linewidths=0.05, colors=((1, 0, 0, 0.5), ), antialiaseds=0, linestyles='--')
    plts[PLTS.LO_LN] = LineCollection([], linewidths=0.05, colors=((0, 1, 0, 0.5), ), antialiaseds=0, linestyles='--')

    plts[PLTS.TD], = ax.plot([], [], 'bo')
    plts[PLTS.H], = ax.plot([], [], 'ro')
    plts[PLTS.L], = ax.plot([], [], 'go')

    ax.add_collection(plts[PLTS.HI_LN])
    ax.add_collection(plts[PLTS.LO_LN])

    fig.canvas.mpl_connect('key_press_event', press)


def show_all():
    draw_prices()
    # ax.set_title('Simple plot')
    plt.tight_layout()
    return plts


def start_fig(days, save):
    global gAnim
    init_fig_lines()
    ax.set_title('Simple plot')
    gAnim = animation.FuncAnimation(fig, update, days, None, blit=True, repeat=False)  # interval=50,
    # show_all()
    if save:
        print("save figure to mp4 ... ")
        mpeg = animation.FFMpegWriter()
        gAnim.save('outlier.mp4', writer=mpeg)
        print("Done")
    else:
        plt.show()


def main(save=False):
    V.summit_range = 20
    V.waiting_for_input = False
    V.open_percentage = 1

    base_days = 1900
    days = dohlc.df_len - base_days - 1

    dohlc.set_range(base_days, days)
    start_fig(days, save)

    # dohlc.loop(update)

if __name__ == '__main__':
    main(False)
