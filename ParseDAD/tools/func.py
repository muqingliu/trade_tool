import sys

def range_step(start, stop, step):
	r = start
	while r < stop:
		yield r
		r += step


def atoi(s):
	try:
		return int(s)
	except Exception as e:
		#print e
		return 0
