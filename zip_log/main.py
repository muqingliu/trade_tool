
# coding: utf-8

# In[1]:

import zipfile
import os
import re
import time
import shutil
import subprocess
import multiprocessing

def p7zip(target, src):
    """最大压缩率打包"""
    cmd = ['7z', 'a', target, src, '-mx=9' ,'-ms=200m', '-mf', '-mhc', '-mhcf' ,'-mmt', '-r']
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    #print(proc.stdout.read().decode("gbk"))
    proc.stdout.close()
    proc.stderr.close()


def p7ziplist(target, listfile):
    """最大压缩率打包"""
    src = "@%s" % listfile
    #print src
    cmd = ['7z', 'a', target, src, '-mx=9' ,'-ms=200m', '-mf', '-mhc', '-mhcf' ,'-mmt', '-r']
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    print proc.stderr.read().decode("gbk")
    #print(proc.stdout.read().decode("gbk"))
    proc.stdout.close()
    proc.stderr.close()


def zip_test(target):
    """检查压缩包是否损坏"""
    cmd = ['7z', 't', target]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    is_ok = True
    error_str = proc.stderr.read()
    find_pos = error_str.find('ERROR')
    if find_pos != -1:
        print find_pos
        is_ok = False
    proc.stdout.close()
    proc.stderr.close()
    return is_ok


def get_dir_list(rootdir):
    dir_list = []
    for parent, dirnames, filenames in os.walk(rootdir):
        for dirname in dirnames:
            if(rootdir == parent):
                dir_list.append(dirname)

    return dir_list


def get_dir_content_list(rootdir):
    dir_list = get_dir_list(rootdir)

    dir_content_list = []
    for d in dir_list:
        m = re.search(r'(\d{4})-(\d{1,2})', d)
        if not m:
            continue

        subdir = os.path.join(rootdir,d)
        for parent, dirnames, filenames in os.walk(subdir):
            for dirname in dirnames:
                if subdir == parent:
                    fullpath = os.path.join(parent,dirname)
                    dir_content_list.append(fullpath)

            for filename in filenames:
                if subdir == parent:
                    fullpath = os.path.join(parent,filename)
                    dir_content_list.append(fullpath)

    return dir_content_list


def get_marched_dir(rootdir):
    """获得目标（将要压缩）的文件夹"""
    files = {}
    dir_content_list = get_dir_content_list(rootdir)
    for f in dir_content_list:
        #需将时间戳偏移为北京时间（东八区时）
        ctime = os.path.getmtime(f) + 28800
        st_time = time.gmtime(ctime)
        w = time.strftime("%W", st_time)
        zip_name = "%04d-%02d(%02d)" % (st_time.tm_year, st_time.tm_mon, int(w))
        if not files.has_key(zip_name):
            files[zip_name] = []

        files[zip_name].append(f)

    return files


def process_scheduler(rootdir, process_id):
    all_succ = True
    files = get_marched_dir(rootdir)
    for key in files:
        week_files = files[key]
        target_zip = os.path.join(rootdir,'%s.7z' % key)
        if os.path.exists(target_zip):#已经存在压缩包，检测该压缩包是否已损坏
            if not zip_test(target_zip):
                print "压缩文件损坏，删除"
                os.remove(target_zip)

        week_files = files[key]
        content = ""
        for file_path in week_files:
            #p7zip(target_zip, file_path)
            content += "%s\n" % (file_path)

        listfile = "%u_%s.txt" % (process_id, key)
        with open(listfile, "w") as fp:
            fp.write(content)

        print target_zip
        p7ziplist(target_zip, listfile)

        #只要确定压缩成功了，才将原始文件删除
        count = 0
        while not zip_test(target_zip):
            #因压缩进程运行为异步，因此需等待压缩成功，等待时间为1分钟
            count = count + 1
            if count >= 60:
                break

            time.sleep(1)

        if count < 60:
            for file_path in week_files:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)

            os.remove(listfile)
        else:
            all_succ = False

    if all_succ:
        dir_list = get_dir_list(rootdir)
        for d in dir_list:                
            m = re.search(r'(\d{4})-(\d{1,2})', d)
            if not m:
                continue

            file_path = os.path.join(rootdir,d)
            if not os.path.isdir(file_path):
                continue

            shutil.rmtree(file_path) 


def my_proc(path, process_id):
    process_scheduler(path, process_id)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    import pyetc
    conf = pyetc.load(r'sys.conf')

    pool = multiprocessing.Pool(processes = conf.process_number)
    process_id = 0
    for p in conf.list_path:
        pool.apply_async(my_proc, (p, process_id, ))   #维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
        process_id = process_id + 1
    pool.close()
    pool.join()   #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
        # process_scheduler(p)
    print("all done.")
