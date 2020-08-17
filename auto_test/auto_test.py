import os
import ConfigParser
import subprocess
import time
import log
import sys


class SystemConfig(object):
    def __init__(self, path_ini):
        ini_parser = ConfigParser.ConfigParser()
        ini_parser.read(path_ini)

        self.tool_path_set = []
        for x in xrange(1,100):
            option = "tool_path%u" % (x)
            if ini_parser.has_option("main", option):
                tool_path = ini_parser.get("main", option)
                self.tool_path_set.append(tool_path)
            else:
                break

        self.process_count = ini_parser.getint("main", "process_count")
        if ini_parser.has_option("main", "last_exe"):
            self.last_exe = ini_parser.get("main", "last_exe")
        else:
            self.last_exe = ""


def print_log(msg):
    log.set_log_mode('a')

    now_datetime = time.localtime()
    content = u"%u-%02u-%02u %02u:%02u:%02u %s"%(now_datetime.tm_year, now_datetime.tm_mon, now_datetime.tm_mday, now_datetime.tm_hour, 
              now_datetime.tm_min, now_datetime.tm_sec, msg)
    log.WriteLog("sys", content)


def main():
    # cur_file = sys.path[0]
    # cur_path = cur_file
    # index = cur_file.rfind("\\")
    # if index >= 0:
    #     cur_path = cur_file[0:index]
    cur_path = sys.path[0]
    os.chdir(cur_path)    

    sys_full_path = os.path.join(cur_path, "system.ini")
    sys_info = SystemConfig(sys_full_path)

    file_end_flag = {}
    for filepath in sys_info.tool_path_set:
        if os.path.exists(filepath) and os.path.isfile(filepath) and os.path.splitext(filepath)[1] == '.exe':
            file_end_flag[filepath] = False

    file_process = {}
    process_count = 0
    while True:
        isAllEnd = True
        filepaths = file_end_flag.keys()
        for filepath in filepaths:
            if not file_end_flag[filepath]:
                isAllEnd = False
                break

        if isAllEnd:
            break

        if process_count < sys_info.process_count:
            for filepath in filepaths:
                if file_process.has_key(filepath):
                    continue

                cmd = "%s autorun" % (filepath)
                p = subprocess.Popen(cmd)
                file_process[filepath] = p
                process_count = process_count + 1
                if process_count >= sys_info.process_count:
                    break

        for filepath in filepaths:
            if file_process.has_key(filepath):
                if file_end_flag[filepath]:
                    continue

                result = file_process[filepath].poll()
                if result is not None:
                    file_end_flag[filepath] = True
                    process_count = process_count - 1

        time.sleep(1)

    if len(sys_info.last_exe) > 0 and os.path.exists(sys_info.last_exe) and os.path.isfile(sys_info.last_exe) \
        and os.path.splitext(sys_info.last_exe)[1] == '.exe':
        subprocess.Popen(sys_info.last_exe)


if __name__ == '__main__':
    try:
        main()
    except Exception, msg:
        import traceback
        print_log("error msg:%s" % (msg))
        print msg, traceback.print_exc()
