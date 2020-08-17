import sys,os,shutil
import subprocess
import ConfigParser
import traceback


def init_sys_path():
    try:
        cur_fullpath = sys.argv[0]
        r_idx = cur_fullpath.rfind("\\")
        cur_path = cur_fullpath[0:r_idx]
        os.chdir(cur_path)
        return cur_path
    except Exception, e:
        print e
        os.system('pause')


def get_dir_list():
    ini_parser = ConfigParser.ConfigParser()
    ini_parser.read("account.ini")

    dir_list = []
    for option in ini_parser.options("account"):
        path = ini_parser.get("account", option)
        dir_list.append(path)

    return dir_list


def get_dir_files(dir_name):
    file_list = []
    for file in os.listdir(dir_name):
        fullpath = os.path.join(dir_name,file)
        if not os.path.isdir(fullpath):
            r_spot_idx = fullpath.rfind(".")
            ext = fullpath[r_spot_idx + 1:]
            if ext == 'xls' or ext == 'csv' or ext == 'xlsx':
                file_list.append(fullpath)
            elif ext == 'account':
                account_path = fullpath

    return (account_path, file_list)


def produce_html(root_dir, account_path, file_list):
    del_files = []
    for root,dirs,filenames in os.walk("res\\db"):
        for filename in filenames:
            ext_info = os.path.splitext(filename)
            if ext_info[1] == ".xls" or ext_info[1] == ".account":
                full_path = os.path.join(root, filename)
                del_files.append(full_path)

    del_file_size = len(del_files)
    for i in xrange(0,del_file_size):
        del_file = del_files[i]
        os.remove(del_file)

    file_list_str = ""
    file_count = len(file_list)
    for i in xrange(0,file_count):
        tar_path = "\\res\\db\\table%u.xls" % (i+1)
        tar_path = root_dir + tar_path

        shutil.copyfile(file_list[i], tar_path)

    r_idx = account_path.rfind("\\")
    account_file = account_path[r_idx+1:]
    tar_account_path = "\\res\\db\\%s" % account_file
    tar_account_path = root_dir + tar_account_path
    shutil.copy(account_path, tar_account_path)

    proc = subprocess.Popen("res\\php\\php.exe code/php/stock_equity_pos_merge_db.php", shell=True, stdout=subprocess.PIPE)

    script_response = proc.stdout.read()


def main():
    try:
        root_dir = init_sys_path()
        dir_list = get_dir_list()
        for dir_name in dir_list:
            dir_info = get_dir_files(dir_name)
            produce_html(root_dir, dir_info[0], dir_info[1])
    except Exception, e:
        print traceback.print_exc()
        print e
        os.system('pause')


if __name__ == '__main__':
    main()