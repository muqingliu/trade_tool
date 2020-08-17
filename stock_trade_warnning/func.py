from __future__ import unicode_literals
import sys
import traceback

def atoi(s):
	try:
		return int(s)
	except Exception as e:
		#print e
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
