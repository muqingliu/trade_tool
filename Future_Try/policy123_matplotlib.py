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

from util import data_ohlc, log_csv, PPointer, Xval, ptype
from trade import trade
# http://ffmpeg.zeranoe.com/builds/


class Text_pool():
    def __init__(this):
        this.pool = []
        this.idx = 0

    def reset(this):
        this.idx = 0
        for o in this.pool:
            o.set_text("")

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
    # P3 = 6
    # P4 = 7
    # P5 = 8
    # P6 = 9
    # P7 = 10
    # P8 = 11

    # T1 = 12
    # T2 = 13
    # T3 = 14
    # T4 = 15
    # T5 = 16
    # T6 = 17
    # T7 = 18
    # T8 = 19

    L1 = 6
    L2 = 7
    # L2 = 21
    # L3 = 22
    # L4 = 23
    # L5 = 24

    NUM = 8

    # HI_LN = 2
    # LO_LN = 3

    # H = 5
    # L = 6

POINT_NAME =["BEGIN", "1", "2", "3", "4", "5", "6", "7", "8"]

class CONST:
    KLINE_NUM = 200

# plt.rcParams['animation.ffmpeg_path'] = u'.\\ffmpeg.exe'
plt.rcParams['animation.convert_path'] = u'C:\\Program Files\\ImageMagick-7.0.7-Q16\\magick.exe'
# sys.path.append("C:\\Program Files\\ImageMagick-7.0.7-Q16\\modules\\coders\\")

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
    objs_show = []
    text_pool.reset()

    draw_prices()

    df = dohlc.get_history(frame)
    leng = len(df)
    if leng == 0:
        return objs_show

    if cur_pos >= leng:
        cur_pos = leng - 1

    dt_td = df.iloc[cur_pos]

    plts[PLTS.TD].set_data(Xval(dt_td), dt_td.MA5)
    objs_show.append(plts[PLTS.TD])

    cur_pos = cur_pos + 1
    if cur_pos >=200: cur_pos = 200

    # ppointer.update_offset(1)
    ppointer.push(dt_td)
    print frame, len(ppointer.Pter)

    idx = 0
    idx_pt = PLTS.P1
    # idx_txt = PLTS.T1
    # print "-"*20
    # objs_show.extend(plts)

    points_L = []
    points_H = []

    text_node_end = text_pool.get_text_obj()
    for p in ppointer.Pter:
        if p.type == ptype.high:
            points_H.append((Xval(p.pt) - p.offset, p.pt.MA5))
        else:
            points_L.append((Xval(p.pt) - p.offset, p.pt.MA5))

        if  idx > 3: # 延续，后面的节点都算作3
            text_node_end.set_text(POINT_NAME[3])
            text_node_end.set_position((Xval(p.pt) - p.offset, p.pt.MA5 + 100))
            objs_show.append(text_node_end)
        else:
            text = text_pool.get_text_obj()
            text.set_text(POINT_NAME[idx])
            text.set_position((Xval(p.pt) - p.offset, p.pt.MA5 + 100))
            objs_show.append(text)

        idx  = idx + 1
        if idx > 8: break

    history_text = []
    for nodes in ppointer.success_node: # 历史成功的4(0~3)个点绘制出来
        idx = 0
        for p in nodes:
            if p.type == ptype.high:
                points_H.append((Xval(p.pt) - p.offset, p.pt.MA5))
            else:
                points_L.append((Xval(p.pt) - p.offset, p.pt.MA5))

            text = text_pool.get_text_obj()
            text.set_text(POINT_NAME[idx])
            text.set_position((Xval(p.pt) - p.offset - 2, p.pt.MA5 + 100))
            objs_show.append(text)

            idx = idx + 1

    if len(points_H) > 0:
        plts[PLTS.P1].set_data(map(list,zip(*points_H)))

    if len(points_L) > 0:
        plts[PLTS.P2].set_data(map(list,zip(*points_L)))

    objs_show.append(plts[PLTS.P1])
    objs_show.append(plts[PLTS.P2])

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

    objs_show.append(plts[PLTS.L1])
    objs_show.append(plts[PLTS.L2])

    return objs_show



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

    plt.tight_layout()

def init_fig_lines():
    plts[PLTS.MA5] = LineCollection([], linewidths=0.08, colors=((0, 0, 1, 0.5), ), antialiaseds=0, linestyles='-')
    ax.add_collection(plts[PLTS.MA5])
    ax.autoscale()

    plts[PLTS.L1] = LineCollection([], linewidths=0.05, colors=((1, 0, 0, 0.5), ), antialiaseds=0, linestyles='--')
    plts[PLTS.L2] = LineCollection([], linewidths=0.05, colors=((0, 0, 1, 0.5), ), antialiaseds=0, linestyles='--')
    ax.add_collection(plts[PLTS.L1])
    ax.add_collection(plts[PLTS.L2])

    plts[PLTS.TD], = ax.plot([], [], 'bo', markersize="14")
    plts[PLTS.P1], = ax.plot([], [], 'ro', markersize="14")
    plts[PLTS.P2], = ax.plot([], [], 'go', markersize="14")


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

    gAnim = animation.FuncAnimation(fig, update, frames=days, init_func = None, blit=True, interval=50, repeat=False)  # interval=50,
    # show_all()
    if save:
        print("save figure to mp4 ... ")
        # mpeg = animation.FFMpegWriter(bitrate=30000000, fps=10, extra_args=['-vcodec', 'libx264'])
        gAnim.save('%d.gif' % name, writer='imagemagick', fps=10, extra_args=['-delay',5000]);
        # gAnim.save('%d.mp4' % name, writer=mpeg)
        print("Done")
    else:
        plt.show()


def onClick(event):
    global pause
    pause ^= True
    print 'user click the mouse!'
    print 'you pressed', event.button, event.xdata, event.ydata
#   event.button=1



def main(save=False):

    fig.canvas.mpl_connect('button_press_event', onClick)
    # dohlc.set_range(0, CONST.KLINE_NUM)
    days = len(dohlc.df.index)
    days = 25
    days = 150
    days = 95
    days = 200

    x = 0
    beg_pos = x * 200
    dohlc.set_range(beg_pos, CONST.KLINE_NUM)
    start_fig(days, save, x )
    gc.collect()
    ax.clear()
    # dohlc.loop(update)

if __name__ == '__main__':
    main(False)
