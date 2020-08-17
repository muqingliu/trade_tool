import sys,os

file_path, file_name = os.path.split(sys.argv[0])
f = open("%s\\z.txt" % file_path, "w")

for arg in sys.argv:
	line = arg	
	print line
	f.write("%s\n" % line)
f.close()

# print sys.argv
print(os.getcwd())

os.system("pause")
