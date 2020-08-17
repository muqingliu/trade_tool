import re
import os
import shutil
import equity_sort
import excel_paint


def search_margin_files(rootdir):
    margin_files = []
    for parent, dirnames, filenames in os.walk(rootdir):
        for filename in filenames:
            ma = re.match("sma.*margin.*", filename)
            if ma:
                margin_files.append(filename)
            # _path,_file=os.path.split(fullname)

            # print _file.find("equity")
            # print filename
    return margin_files


def iter_dir(rootdir):
    for parent, dirnames, filenames in os.walk(rootdir):
        for dirname in dirnames:
            if(rootdir == parent):
                yield dirname


def calc_align_position(files_datas):
    number = len(files_datas.values())
    size = len(files_datas.values()[0])
    index = 0
    for x in xrange(0,size):
        zero_number = number
        for datas in files_datas.values():
            if datas[x][1] != 0: zero_number -= 1
        if zero_number == 0: break
        index += 1
    return index


def main():
    rootdir = r"N:\Project\trader\bin\TradeTool\log\2017-12"
    tardir = r"N:\Project\trader_work\tools\paint_equity"

    for dir in iter_dir(rootdir):
        path = r"%s\%s\%s" % (rootdir, dir, dir)
        tarpath = r"%s\equity_%s" % (tardir, dir)

        if not os.path.exists(tarpath):
            os.makedirs(tarpath)
            margin_files = search_margin_files(path)

            for f in margin_files:
                shutil.copyfile('%s/%s' % (path, f), "%s/%s" % (tarpath, f))

            # 评估排序
            full_path_magin_file = ["%s/%s" % (tarpath, f) for f in margin_files]

            files_datas = equity_sort.process_files(full_path_magin_file)

            # 筛选
            # margin_files = excel_paint.choose_margin_files(tarpath, 0)
            # excel_paint.do_excel(tarpath, margin_files, True)

            align_pos = calc_align_position(files_datas)#可为None
            align_pos = 477

            excel_paint.do_excel(tarpath, files_datas, align_pos, True)

            # full_path = os.getcwd() + "\\equity"
            excel_paint.do_chart(tarpath)

    # files = search_dir(rootdir)
    # print(files)

if __name__ == '__main__':
    main()
