from __future__ import unicode_literals
import sys
import traceback
import log
import db
import config.config as config


def atoi(s):
	try:
		return int(s)
	except Exception as e:
		#print(e)
		return 0

def format_traceback():
	lines = []
	lines.extend(traceback.format_stack())
	lines.extend(traceback.format_tb(sys.exc_info()[2]))
	lines.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

	join_line = ["Traceback (most recent call last):\n"]
	for strg in lines:
		if not isinstance(strg, unicode):
			join_line.append(strg.decode("utf8"))
		else:
			join_line.append(strg)

	except_str = ''.join(join_line)

	# Removing the last \n
	except_str = except_str[:-1]
	return except_str

#复权后写库操作
def insertDB_Instruments(InstrumentsName,sourcelist,recoveredlist,mydb):
    tmplist=[]
    if len(sourcelist) != len(recoveredlist):
        print ("err sourcelen %s != reclen %s" % (len(sourcelist),len(recoveredlist)))
        return
    for i in range(len(sourcelist)):
        tmpValues = (InstrumentsName,sourcelist[i]['Time'],sourcelist[i]['OpenPrice'],sourcelist[i]['ClosePrice'],sourcelist[i]['HighestPrice']
        ,sourcelist[i]['LowestPrice'],round(recoveredlist[i]['OpenPrice'],3),round(recoveredlist[i]['ClosePrice'],3),round(recoveredlist[i]['HighestPrice'],3),round(recoveredlist[i]['LowestPrice'],3),round(recoveredlist[i]['Volume'],3))
        tmplist.append(tmpValues)
        if sourcelist[i]['Time'] != recoveredlist[i]['Time']:
            print ("Timeerror",sourcelist[i]['Time'],recoveredlist[i]['Time'])
            return
    try:
        log.WriteLog('LOG_TRADE',"BEGIN INSERT SQL :...")
        _sql = "INSERT INTO `future_redetails`(`InstrumentsName`,`Time`,`OpenPrice`,`ClosePrice`,`HighestPrice`,`LowestPrice`,`rOpenPrice`,"\
           "`rClosePrice`,`rHighestPrice`,`rLowestPrice`,`Volume` )VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        mydb.Executemany(_sql,tmplist)
        log.WriteLog('LOG_TRADE',"====FINISH  %s=="%InstrumentsName)

    except Exception as err:
        print(err)
    finally:
        pass



def create_database():
    mydb = db.DB(host = config.ConnetionINC['host'],
                 user = config.ConnetionINC['user'],
                 passwd = config.ConnetionINC['passwd'],
                 db = config.ConnetionINC['db'],
                 port = config.ConnetionINC['port'],
                 charset = config.ConnetionINC['charset'])
    return mydb
