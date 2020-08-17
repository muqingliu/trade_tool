from __future__ import unicode_literals
import time
import io
import os
import sys
import platform
import colorama # http://pypi.python.org/pypi/colorama
import chardet
import threading
import Queue
#from common import web

_log_files = {}
_log_console_enable = {}
_log_mode = 'w'
log_queue = Queue.Queue()

def set_log_mode(mode):
    global _log_mode
    _log_mode = mode

class class_log:
    enable = False
    clr_inited = False
    _file_path = ""
    _file = None
    isWindows = False

    clr_blue =  colorama.Style.BRIGHT + colorama.Fore.BLUE
    clr_green =  colorama.Style.BRIGHT + colorama.Fore.GREEN
    clr_red =  colorama.Style.BRIGHT + colorama.Fore.RED
    clr_yellow =  colorama.Style.BRIGHT + colorama.Fore.YELLOW
    clr_mag = colorama.Style.BRIGHT + colorama.Fore.MAGENTA

    def __init__(this, path):
        this._file_path = path
        this._file = open(path,_log_mode)

        if not this.clr_inited :
            colorama.init(autoreset=True)

        this.isWindows = ('win32' == sys.platform)

    def __del__(this):
        if this.clr_inited:
            colorama.deinit()
        this.close()

    def _write_file(this, c):
        try:
            #stime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            c = '%s\n' % c
            c = c.encode("gbk")
            this._file.write(c)
            this._file.flush()
        except:
            pass

    def write_console(this, c):        
        # if this.isWindows : c = c.encode('utf8', errors='ignore')
        # else : c = c.encode('utf8')
        if not sys.stdout.encoding: c = c.encode('utf8')
        sys.stdout.write(c)

    def write(this, clr, c):
        this._write_file(c)

        if this.enable :
            c = clr + c + colorama.Style.RESET_ALL + '\n'
            this.write_console(c)

    def write_trace(this, c):
        strg = func.format_traceback()
        if not strg:
            this.write(this.clr_red, 'trace lost.%s'%c)
            return
        send_log_mail_exception(strg)
        this.write(this.clr_red, strg)
        this.write(this.clr_red, c)

    def close(this):
        this._file.close()

_sys_log = None

def _Get_sys_log():
    global _sys_log
    if not _sys_log: _sys_log = class_log("log/sys.log")
    return _sys_log

# 设置日志是否显示在控制台
def SetConsoleEnable(file_name, enable):
    _log_console_enable[file_name] = enable

def close_all():
    global _log_files
    for k,v in _log_files.items():
        v.close()
    _log_files ={}

def WriteLog(file_name, content):
    HandleLog(file_name, content)
    #log_queue.put((file_name, content))

# 写日志，如果没有日志对象则创建
def HandleLog(file_name, content):
    global _log_files

    if not isinstance(content, unicode) and not isinstance(content, str): 
        content = content.__str__()

    # 创建log目录
    base_path = os.getcwd()
    if not os.path.exists(base_path + "/log"): os.makedirs(base_path+"/log") 

    path = "log/%s.log" % file_name
    if not _log_files.has_key(path): _log_files[path] = class_log(path)

    if not isinstance(content, unicode):
        if chardet.detect(content)["encoding"] == "utf-8":
            content = content.decode("utf-8")
        elif chardet.detect(content)["encoding"] == "GB2312":
            content = content.decode("GB2312")

    try : 
        if class_log.enable:
            _log_files[path].write_console("%s: " % file_name)
        _log_files[path].write(class_log.clr_mag, content)
    except Exception as e:
        print e

def WriteError(strg):
    try : 
        _Get_sys_log().write(class_log.clr_mag, strg)
    except Exception as e:
        print e

def WriteWarning(strg):
    try : 
        _Get_sys_log().write(class_log.clr_mag, strg)
    except : pass

def WriteExcept(strg):
    try :
        _Get_sys_log().write_trace(strg)

    except Exception as e:
        print e
    # raise exception. 
    # don't put it into try block 
    sys.exit() 

def WriteBlock(strg):
    _Get_sys_log().write(class_log.clr_blue, '======= %s ========'%strg)

def WriteEntry(strg):
    _Get_sys_log().write(class_log.clr_green, '▶ %s'%strg)

def WriteDetail(strg):
    _Get_sys_log().write(class_log.clr_yellow, ' - %s'%strg)

def WriteRaw(strg):
    if not _Get_sys_log().enable:return
    sys.stdout.write(strg)

def Disable(yes = True):
    _Get_sys_log().enable = not yes

if __name__ == '__main__':
    WriteLog('log.aa', "开盘")
    