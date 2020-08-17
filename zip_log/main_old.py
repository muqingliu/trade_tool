
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
    print(proc.stdout.read().decode("gbk"))
    proc.stdout.close()
    proc.stderr.close()

def zip_test(target):
    """检查压缩包是否损坏"""
    cmd = ['7z', 't', target]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    is_ok = True
    find_pos = proc.stderr.read().find('ERROR')
    if find_pos != -1:
        is_ok = False
    proc.stdout.close()
    proc.stderr.close()
    return is_ok

def iter_dir(rootdir):
    for parent, dirnames, filenames in os.walk(rootdir):
        for dirname in dirnames:
            if(rootdir == parent):
                yield dirname

def get_marched_dir(rootdir):
    """获得目标（将要压缩）的文件夹"""
    now_dt = int(time.strftime("%Y%m"))

    dirs = []
    for d in iter_dir(rootdir):
        m = re.search(r'(\d{4})-(\d{1,2})', d)
        if(m):
            dir_name = m.group(0)
            year = int(m.group(1))
            month = int(m.group(2))

            if year*100+month < now_dt:
                dirs.append(dir_name)
    return dirs

def process_scheduler(rootdir):
    dirs = get_marched_dir(rootdir)
    print(rootdir, "find marched", dirs)
    for d in dirs:
        path = os.path.join(rootdir, d)
        target = os.path.join(rootdir,'%s.7z' % d)

        if os.path.exists(target):#已经存在压缩包，但是原始文件还在，一般是以前压缩被中断，该压缩包是坏包
            os.remove(target)

        print("generate to", target)
        p7zip(target, path)
        print("done!")

        if zip_test(target):#只要确定压缩成功了，才将原始文件删除
            shutil.rmtree(path)
        else:
            os.remove(target)
            print("target [%s] is broken，deleted!!!" % target)



def my_proc(path):
    process_scheduler(path)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    import pyetc
    conf = pyetc.load(r'sys.conf')

    pool = multiprocessing.Pool(processes = conf.process_number)
    for p in conf.list_path:
        pool.apply_async(my_proc, (p, ))   #维持执行的进程总数为processes，当一个进程执行完毕后会添加新的进程进去
    pool.close()
    pool.join()   #调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
        # process_scheduler(p)
    print("all done.")



# In[ ]:



