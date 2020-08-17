from __future__ import unicode_literals
import time
import datetime

class timer:
    startTime = 0

    def __init__(this):
        pass

    def start(this):
        this.startTime = time.time();

    def spent(this):   
        return time.time()-this.startTime


def to_day_str(t):
	'''
	print like this '20121018'
	'''
	return time.strftime('%Y%m%d',time.localtime(t))

def to_date_str(t):
	return time.strftime('%d %b %Y',time.localtime(t))

def get_offset_day_str(offset_day):
	return (datetime.date.today() + datetime.timedelta(days=offset_day)).strftime('%Y%m%d')

def get_today_str():
	return get_offset_day_str(0)

def get_yesterday_str():
	return get_offset_day_str(-1)


def get_date_name(date, disp_date = False):
	dn_today = get_today_str()
	dn_yesterday = get_yesterday_str()
	if dn_today == to_day_str(date):
		return 'Today'
	if dn_yesterday == to_day_str(date): 
		return 'Yesterday'
	return disp_date and to_date_str(date) or 'Older'




if __name__=="__main__":
 
	print to_date_str(time.time())