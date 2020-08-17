import scanf


days = []
f = open("IFL0.TXT", "rt")
if f:
	l = f.readline()
	while l:
		try:
			y,m,d = scanf.sscanf(l, "%d/%d/%d")
			days.append(y*10000+m*100+d)
		except Exception, e:
			pass
		l = f.readline()


	f.close()

f = open("days.txt", "wt")
for day in days:
	f.write("%d\n"% day)
f.close()


