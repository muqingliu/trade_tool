import sys,os,shutil
import subprocess

cur_fullpath = sys.argv[0]
r_idx = cur_fullpath.rfind("\\")
cur_path = cur_fullpath[0:r_idx]
os.chdir(cur_path)

def produce_html(record_file_path):
    tar_path = cur_path + "\\res\\db\\table1.xls"

    shutil.copyfile(record_file_path, tar_path)

    proc = subprocess.Popen("res\\php\\php.exe code/php/stock_equity_pos.php", shell=True, stdout=subprocess.PIPE)

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
    script_response = script_response.replace("\r\n", "")
    web_content = web_content.replace("result", '"' + script_response + '"')

    r_slash_idx = record_file_path.rfind("\\")
    name_with_ext = record_file_path[r_slash_idx + 1:]
    r_spot_idx = name_with_ext.rfind(".")
    name = name_with_ext[0:r_spot_idx]

    html_name = name + ".html"

    fp_ret = open(html_name, "wb")
    if fp_ret:
        fp_ret.write(web_content.encode("utf8"))
        fp_ret.close()
        
argv_len = len(sys.argv)
if argv_len > 1:
    produce_html(sys.argv[1])
else:
    for file in os.listdir(cur_path):
        fullpath = os.path.join(cur_path,file)
        if not os.path.isdir(fullpath):
            r_spot_idx = fullpath.rfind(".")
            ext = fullpath[r_spot_idx + 1:]
            if ext == 'xls' or ext == 'csv' or ext == 'xlsx':
                print(fullpath)
                produce_html(fullpath)
