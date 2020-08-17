def make_trade_days():
	days = []
	f = open("days.txt", "rt")

	l = f.readline()
	while l:
		days.append(int(l))
		l = f.readline()
	f.close()
	return days

def get_days(start):
	days = make_trade_days()
	for x in xrange(0,len(days)):
		if start == days[x]:
			return days[x:]
	return []


