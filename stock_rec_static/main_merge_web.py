import sys,os,shutil
import subprocess

cur_fullpath = sys.argv[0]
r_idx = cur_fullpath.rfind("\\")
cur_path = cur_fullpath[0:r_idx]
os.chdir(cur_path)


def produce_html(account_id, file_list):
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
        tar_path = cur_path + tar_path

        shutil.copyfile(file_list[i], tar_path)

    proc = subprocess.Popen("res\\php\\php.exe code/php/stock_equity_pos_merge_web.php", shell=True, stdout=subprocess.PIPE)

    script_response = proc.stdout.read()
    script_response = script_response.decode("utf8")

    web_content = ""
    fp = open("code/php/stock_static.php", "rb")
    if fp:
        line = fp.readline()
        while(len(line) > 0):
            web_content += line.decode("utf8")
            line = fp.readline()

        fp.close()

    script_response = script_response.replace("'", r"\'")
    script_response = script_response.replace('"', r'\"')
    script_response = script_response.replace(r'\\"', r'\\\"')
    script_response = script_response.replace("\r\n", "")
    script_response = script_response.replace(r"\r\n", "")
    web_content = web_content.replace("result", '"' + script_response + '"')

    html_name = account_id + ".html"

    fp_ret = open(html_name, "wb")
    if fp_ret:
        fp_ret.write(web_content.encode("utf8"))
        fp_ret.close()

        
#argv_len = len(sys.argv)
#if argv_len > 1:
#    file_list = []
#    for i in xrange(0,argv_len):
#        file_list.append(sys.argv[i])
#    produce_html(file_list)
#else:
account_id = ""
file_list = []
for file in os.listdir(cur_path):
    fullpath = os.path.join(cur_path,file)
    if not os.path.isdir(fullpath):
        r_spot_idx = file.rfind(".")
        ext = file[r_spot_idx + 1:]
        if ext == 'xls' or ext == 'csv' or ext == 'xlsx':
            file_list.append(fullpath)
        elif ext == 'account':
            account_id = file[0:r_spot_idx]
produce_html(account_id, file_list)
