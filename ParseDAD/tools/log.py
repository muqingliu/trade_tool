import time
import io
import traceback
import sys
import platform
import colorama # http://pypi.python.org/pypi/colorama

def format_exception():
    exception_list = traceback.format_stack()
    #exception_list = exception_list[-2:-2]
    exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
    exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
    exception_str = "Traceback (most recent call last):\n"
    exception_str += "".join(exception_list)
    # Removing the last \n
    exception_str = exception_str[:-1]
    return exception_str

class Log:
	enable = True
	clr_inited = False
	_file_path = ""
	_file = None
	is_windows = False

	clr_blue =  colorama.Style.BRIGHT + colorama.Fore.BLUE
	clr_green =  colorama.Style.BRIGHT + colorama.Fore.GREEN
	clr_red =  colorama.Style.BRIGHT + colorama.Fore.RED
	clr_yellow =  colorama.Style.BRIGHT + colorama.Fore.YELLOW
	clr_mag = colorama.Style.BRIGHT + colorama.Fore.MAGENTA

	def _color_in_file(this, clr):
		if clr == this.clr_mag: return "ERROR: "
		elif clr == this.clr_blue : return ''
		elif clr == this.clr_red : return ''
		elif clr == this.clr_yellow : return ''
		elif clr == this.clr_green : return ''
		return ''

	def __init__(this, path):
		this._file_path = path
		this._file = open(path,"w")
		this.is_windows = (platform.system() == 'Windows')

		if not this.clr_inited :
			colorama.init(autoreset=True)

	def __del__(this):
		if this.clr_inited:
			colorama.deinit()

	def write_console(this, clr, c):
		c = '\n' + clr + c
		#if this.is_windows : 
		#	sys.stdout.write(c.decode('utf-8', 'ignore').encode('GBK'))
		#else :
		sys.stdout.write(c)

		sys.stdout.write(''+colorama.Style.RESET_ALL)

	def write_file(this, clr, c):
		try:
			clr = this._color_in_file(clr)
			stime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
			this._file.write("%s%s %s\n" % (clr, stime, c))
			this._file.flush()
		except:
			print 'error in write file'
			pass

	def write(this, clr, c):
		if this.enable :
			this.write_console(clr, c)
		this.write_file(clr, c)

	def write_trace(this, c):
		strg = format_exception()
		#send_log_mail_exception(strg)

		this.write(this.clr_red, strg)
		this.write(this.clr_red, c)

	def close(this):
		this._file.close()

g_log = Log("logs/log %s.txt" % time.strftime('%Y-%m-%d', time.localtime(time.time())))

def WriteError(strg):
	try : 
		g_log.write(g_log.clr_mag, strg)
		#send_log_mail_error(strg)

	except : pass

def WriteExcept(strg):
	try : 
		g_log.write_trace(strg)

	except : pass
	# raise exception. 
	# don't put it into try block 
	sys.exit() 

def WriteBlock(strg):
	g_log.write(g_log.clr_red, '== %s =='%strg)

def WriteDetail(strg):
	g_log.write(g_log.clr_green, ' - %s'%strg)

def Disable(yes = True):
	g_log.enable = not yes