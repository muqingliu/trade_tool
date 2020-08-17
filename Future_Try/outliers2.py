# import pandas as pd
import gc
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
# from matplotlib import finance
import mpl_finance as finance

from matplotlib.collections import LineCollection

from util import data_ohlc, log_csv, PPointer, Xval
from trade import trade
# http://ffmpeg.zeranoe.com/builds/


class Text_pool():
    def __init__(this):
        this.pool = []
        this.idx = 0

    def reset(this):
        this.idx = 0

    def get_text_obj(this):
        if this.idx >= len(this.pool):
           this.pool.append(ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red'))
        obj = this.pool[this.idx]
        this.idx = this.idx + 1
        return obj

text_pool = Text_pool()
pause  = False
class PLTS:
    LN1 = 0
    LN2 = 1
    MA5 = 2
    TD  = 3 # today

    P1 = 4
    P2 = 5
    P3 = 6
    P4 = 7
    P5 = 8
    P6 = 9
    P7 = 10
    P8 = 11

    T1 = 12
    T2 = 13
    T3 = 14
    T4 = 15
    T5 = 16
    T6 = 17
    T7 = 18
    T8 = 19

    L1 = 20
    L2 = 21
    # L2 = 21
    # L3 = 22
    # L4 = 23
    # L5 = 24

    NUM = 22

    # HI_LN = 2
    # LO_LN = 3

    # H = 5
    # L = 6

POINT_NAME =["BEGIN", "1", "2", "3", "4", "5", "6", "7", "8"]

class CONST:
    KLINE_NUM = 200


text_pool = []

plt.rcParams['animation.ffmpeg_path'] = u'.\\ffmpeg.exe'

# filen = '601318.XSHG.txt'
filen = 'lL0.txt'

fig = plt.figure(figsize=(20, 10), dpi=80)
ax = fig.add_subplot(111)

dohlc = data_ohlc(filen, True)
trd = trade()
plts = list(range(PLTS.NUM))
maxs = []
mins = []
csv = log_csv(filen, ['D', 'P'], False)

ppointer = PPointer()

opened = [False, False]
seq = []

def _blit_draw(self, artists, bg_cache):
    # Handles blitted drawing, which renders only the artists given instead
    # of the entire figure.
    updated_ax = []
    for a in artists:
        # If we haven't cached the background for this axes object, do
        # so now. This might not always be reliable, but it's an attempt
        # to automate the process.
        if a.axes not in bg_cache:
            # bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
            # change here
            bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)

    # After rendering all the needed artists, blit each axes individually.
    for ax in set(updated_ax):
        # and here
        # ax.figure.canvas.blit(ax.bbox)
        ax.figure.canvas.blit(ax.figure.bbox)

# MONKEY PATCH!!
matplotlib.animation.Animation._blit_draw = _blit_draw


def get_loc_summit(df, idx_pt, rng, greater):
    for offset in range(1, rng + 1):
        val_b = df.iloc[idx_pt - offset]
        val = df.iloc[idx_pt]
        val_a = df.iloc[idx_pt + 1]

        cond = False
        if greater:
            cond = (val.H > val_b.H) and (val.H > val_a.H)
        else:
            cond = (val.L < val_b.L) and (val.L < val_a.L)

        if not cond:
            return False

    return True


def get_summit(df, offset=2):
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


def make_line(idx_pt0, idx_pt1, Ys, idx_ptn):
    y0 = Ys[idx_pt0]
    y1 = Ys[idx_pt1]
    # print("idx_pt1", idx_pt1, "idx_pt0", idx_pt0, "y0:", y0, "y1:", y1)

    yn = (idx_ptn - idx_pt0) / (idx_pt1 - idx_pt0) * (y1 - y0) + y0
    return ((idx_pt0, y0), (idx_ptn, yn))


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


def get_far_idx_pts(idx_pts, Ys):
    points = []
    len_idx_pts = len(idx_pts)
    for first in range(-3, -len_idx_pts - 1, -1):
        pts = idx_pts[first:]
        if is_point_inline(pts, Ys):
            # if line is None:
            # return points[-1]
            points.append(first)

    if len(points) == 0:
        return None
    return idx_pts[points[-1]]


def get_lines(idx_pts, Ys, today_idx_pt):
    lines = []
    if len(idx_pts) >= 2:
        lines.append(make_line(idx_pts[-2], idx_pts[-1], Ys, today_idx_pt))

    if len(idx_pts) >= 3:
        idx_pt0 = get_far_idx_pts(idx_pts, Ys)
        if idx_pt0 is not None:
            lines.append(make_line(idx_pt0, idx_pts[-1], Ys, today_idx_pt))

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

cur_pos = 0
def update(frame, *fargs):
    # global maxs, mins, gAnim

    global cur_pos


    draw_prices()

    # if None == frame:
    #     print 'not frame',fargs
    #     # return plts
    # else:
    #     print "frame", frame
    # fig.canvas.draw()

    # df = dohlc.get_history(frame)
    # if len(df) == 0:
    #     return plts

    # today indecator
    # rng_df, leng = dohlc.get_range()
    # pos = 80
    # if pos >= leng : pos = leng-1
    # print pos,leng
    # dt_td = rng_df.iloc[pos]
    df = dohlc.get_history(frame)
    leng = len(df)
    if leng == 0:
        return plts

    if cur_pos >= leng:
        cur_pos = leng - 1

    dt_td = df.iloc[cur_pos]
    plts[PLTS.TD].set_data(Xval(dt_td), dt_td.MA5)

    cur_pos = cur_pos + 1
    if cur_pos >=200: cur_pos = 200

    # ppointer.update_offset(1)
    ppointer.push(dt_td)
    print frame, len(ppointer.Pter)

    if frame == 8:
        a = 5
    idx_pt = PLTS.P1
    idx_txt = PLTS.T1
    # print "-"*20
    if type(plts[PLTS.T1]) == type(1):
        plts[PLTS.T1] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')


    points = []
    for p in ppointer.Pter:
        # print idx_pt, p.pt.MA5, Xval(p.pt)- p.offset, p.type

        if idx_pt > PLTS.P3: # 延续，后面的节点都算作3
            plts[PLTS.P4].set_data(Xval(p.pt) - p.offset, p.pt.MA5)
            points.append((Xval(p.pt) - p.offset, p.pt.MA5))
            plts[PLTS.T4].set_text(POINT_NAME[3])
            plts[PLTS.T4].set_position((Xval(p.pt) - p.offset, p.pt.MA5 + 50))
        else:
            plts[idx_pt].set_data(Xval(p.pt) - p.offset, p.pt.MA5)
            points.append((Xval(p.pt) - p.offset, p.pt.MA5))
            plts[idx_txt].set_text(POINT_NAME[idx_txt - PLTS.T1])
            plts[idx_txt].set_position((Xval(p.pt) - p.offset, p.pt.MA5 + 50))

        idx_pt = idx_pt + 1
        idx_txt = idx_txt + 1
        if idx_pt > PLTS.P8: break



    # for idx in xrange(idx_pt,PLTS.P8+1):
    for idx in xrange(PLTS.P1,PLTS.P8+1):
        plts[idx].set_data(-1, -1)
    plts[PLTS.P1].set_data(map(list,zip(*points)))

    for idx in xrange(idx_txt,PLTS.T8+1):
        plts[idx].set_text("")

    # print "-"*20,"END"


    pt1 = []
    pt2 = []
    for idx in xrange(0,len(ppointer.flag)):
        x = Xval(ppointer.flag[idx][0])

        if ppointer.flag[idx][1] == 0:
            pt1.append(((x, 0),(x,50000)))
        else:
            pt2.append(((x, 0),(x,50000)))

    plts[PLTS.L1].set_paths(pt1)
    plts[PLTS.L2].set_paths(pt2)

    # outlier of last n days
    # sr = V.summit_range
    # (mai, mii) = get_summit(df[-sr:])
    # maxs = push_maxmin(maxs, mai)
    # mins = push_maxmin(mins, mii)
    #
    # if len(maxs) == 0:
    #     return plts
    #
    # dt = df.loc[maxs]
    # plts[PLTS.H].set_data(Xval(dt), list(dt.H))
    # dt = df.loc[mins]
    # plts[PLTS.L].set_data(Xval(dt), list(dt.L))
    #
    # rng_df, leng = dohlc.get_range()

    # high/low lines:
    # lns_h = get_lines(maxs, rng_df.H, dt_td.name + 1)
    # plts[PLTS.HI_LN].set_paths(lns_h)

    # lns_l = get_lines(mins, rng_df.L, dt_td.name + 1)
    # plts[PLTS.LO_LN].set_paths(lns_l)

    # trade_logic(dt_td, lns_h, lns_l)
    # prices moves as realtime:
    # plts[PLTS.LN1].set_data(list(rng_df.D), list(rng_df.C))
    # ax.set_title(dt_td.D.strftime('%d-%m-%Y') )

    # if V.waiting_for_input:
    #     gAnim.paused = True

    # ax.clear()
    # ax.plot(plts[PLTS.MA5])

    # plt.draw()
    return plts#[PLTS.MA5], #plts



def show_all():

    # draw_prices()
    for idx in xrange(PLTS.T1, PLTS.T8):
        plts[idx].set_text("")

    return plts



def draw_prices():
    rng_df, leng = dohlc.get_range()

    plts[PLTS.LN1], plts[PLTS.LN2] = finance.candlestick2_ohlc(
        ax, list(rng_df.O), list(rng_df.H), list(rng_df.L), list(rng_df.C),
        width=0.5,
        colordown='g', colorup='r')

    ma5 = [d for d in zip(rng_df.index, rng_df.MA5)]
    plts[PLTS.MA5].set_paths((ma5,))

    ax.set_yticks(np.linspace(rng_df.H.min(), rng_df.H.max(),10))
    ax.set_ylim(rng_df.H.min()-200, rng_df.H.max()+200)

    # dt = rng_df.index[::leng / 20]
    # datestrs = [d.strftime('%y.%m.%d') for d in rng_df.D[dt]]
    # ax.set_xticks(dt)
    # ax.set_xlim(dt[0], dt[-1])
    # ax.set_xticklabels(datestrs, rotation=90)
    plt.tight_layout()

    # ax.clear()
    # ax.figure.canvas.draw()
# def press(e):
#     global gAnim
#     if e.key == ' ':
#         gAnim.paused = not gAnim.paused


def init_fig_lines():
    plts[PLTS.MA5] = LineCollection([], linewidths=0.08, colors=((0, 0, 1, 0.5), ), antialiaseds=0, linestyles='-')
    ax.add_collection(plts[PLTS.MA5])
    ax.autoscale()
    #\\ax.grid(False, color='b')

    # plts[PLTS.HI_LN] = LineCollection([], linewidths=0.05, colors=((1, 0, 0, 0.5), ), antialiaseds=0, linestyles='--')
    # plts[PLTS.LO_LN] = LineCollection([], linewidths=0.05, colors=((0, 1, 0, 0.5), ), antialiaseds=0, linestyles='--')

    plts[PLTS.L1] = LineCollection([], linewidths=0.05, colors=((1, 0, 0, 0.5), ), antialiaseds=0, linestyles='--')
    plts[PLTS.L2] = LineCollection([], linewidths=0.05, colors=((0, 0, 1, 0.5), ), antialiaseds=0, linestyles='--')
    ax.add_collection(plts[PLTS.L1])
    ax.add_collection(plts[PLTS.L2])
    # plts[PLTS.L2] = LineCollection([], linewidths=0.05, colors=((1, 0, 0, 0.5), ), antialiaseds=0, linestyles='--')
    # plts[PLTS.L3] = LineCollection([], linewidths=0.05, colors=((1, 0, 0, 0.5), ), antialiaseds=0, linestyles='--')
    # plts[PLTS.L4] = LineCollection([], linewidths=0.05, colors=((1, 0, 0, 0.5), ), antialiaseds=0, linestyles='--')
    # plts[PLTS.L5] = LineCollection([], linewidths=0.05, colors=((1, 0, 0, 0.5), ), antialiaseds=0, linestyles='--')

    plts[PLTS.TD], = ax.plot([], [], 'bo', markersize="14")

    plts[PLTS.P1], = ax.plot([], [], 'ro', markersize="14")
    plts[PLTS.P2], = ax.plot([], [], 'go', markersize="14")
    plts[PLTS.P3], = ax.plot([], [], 'ro', markersize="14")
    plts[PLTS.P4], = ax.plot([], [], 'go', markersize="14")
    plts[PLTS.P5], = ax.plot([], [], 'go', markersize="14")
    plts[PLTS.P6], = ax.plot([], [], 'go', markersize="14")
    plts[PLTS.P7], = ax.plot([], [], 'go', markersize="14")
    plts[PLTS.P8], = ax.plot([], [], 'go', markersize="14")

    # plts[PLTS.T1] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')
    plts[PLTS.T2] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')
    plts[PLTS.T3] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')
    plts[PLTS.T4] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')
    plts[PLTS.T5] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')
    plts[PLTS.T6] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')
    plts[PLTS.T7] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')
    plts[PLTS.T8] = ax.text(0, 0, "", fontsize=20, fontstyle='oblique', color='red')


    # plts[PLTS.H], = ax.plot([], [], 'ro')
    # plts[PLTS.L], = ax.plot([], [], 'go')

    # ax.add_collection(plts[PLTS.HI_LN])
    # ax.add_collection(plts[PLTS.LO_LN])

    #fig.canvas.mpl_connect('key_press_event', press)
    pass


def frame_update(count):
    index = 0
    while index < count:
        if not pause:
            index = index + 1
        yield index


def start_fig(days, save, name):
    global gAnim
    init_fig_lines()
    ax.set_title('')

    gAnim = animation.FuncAnimation(fig, update, frames=frame_update(days), init_func = None, blit=True, interval=20, repeat=False)  # interval=50,
    # show_all()
    if save:
        print("save figure to mp4 ... ")
        mpeg = animation.FFMpegWriter()
        gAnim.save('%d.mp4' % name, writer=mpeg)
        print("Done")
    else:
        plt.show()
#ax = plt.axes(xlim=(0, 700), ylim=(0, 255))
#line, = ax.plot([], [], lw=2)
def onClick(event):
    global pause
    pause ^= True
    print 'user click the mouse!'
    print 'you pressed', event.button, event.xdata, event.ydata
#   event.button=1 鼠标左键按下 2 中键按下 3 右键按下



def main(save=False):
    # V.summit_range = 20
    # V.waiting_for_input = False
    # V.open_percentage = 1

    # base_days = 1500
    # days = dohlc.df_len - base_days - 1
    # days = 100
    # dohlc.set_range(base_days, days)
    fig.canvas.mpl_connect('button_press_event', onClick)
    # dohlc.set_range(0, CONST.KLINE_NUM)
    days = len(dohlc.df.index)
    days = 25
    days = 150
    days = 95
    days = 200

    x = 1
    beg_pos = x * 200 +100
    dohlc.set_range(beg_pos, CONST.KLINE_NUM)
    start_fig(days, save, x )
    gc.collect()
    ax.clear()
    # dohlc.loop(update)

if __name__ == '__main__':
    main(False)
