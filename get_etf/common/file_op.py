from __future__ import unicode_literals
import os

def get_all_files(direct, file_type):

	if not os.path.isdir(direct) : return []
	post_fixt = '.%s'%file_type

	#----------------------
	def file_name_filter(file_name):
		# special case:
		if file_name.startswith('.'):return False
		# match all
		if not file_type:return True
		if file_type == '*':return True
		# real filter
		return f.endswith(post_fixt)

	#----------------------
	for root, dirs, files in os.walk(direct):
		files = [f for f in files if file_name_filter(f)]
		return files

	return []


#----------------------
def make_sure_dir(path):
	if(os.path.isdir(path)):return
	os.mkdir(path)

#----------------------
# TESTED
def check_is_all_pages_really_got(site_chpt_path, save_num, pg_num):
	pic_files = get_all_files(site_chpt_path, '*')
	pic_num = len(pic_files)
	return pic_num == save_num and pic_num == pg_num

#----------------------
def get_manga_group_id(mid):
	return int( (mid / 1000) * 1000 )

#----------------------
# books/g0/m15/c30/chs/p1.jpg
# ->  get_book_dir(15, 30, 'chs', p1.jpg)
#
# books/g0/m15/m.db
# ->  get_book_dir(15, file='m.db')
# 
# 目录一定会存在
# 更具id范围来区分不同的包
# 每 1000个漫画一个组(group)  [0 - 999],[1000 - 1999], ...
# 目录名为： books/g0, books/g1000, books/g2000, ...

def get_book_dir(mid, cid=None, lang='', file='', mk = True):

	dire = '../books/g%d'%get_manga_group_id(mid)
	if mk : make_sure_dir(dire)
	
	dire = '%s/m%d'%(dire, mid)
	if mk : make_sure_dir(dire)
	
	if cid != None:
		dire = dire + '/c%d'%cid
		if mk : make_sure_dir(dire)
		if lang :
			dire = dire + '/' + lang
			if mk : make_sure_dir(dire)
	if file :
		dire = '%s/%s'%(dire, file)

	return dire

