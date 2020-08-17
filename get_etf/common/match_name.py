from __future__ import unicode_literals
import unicodedata
import re

#适合相同语言对比
def is_manga_name_similar(str1, str2) :
	dic1 = split_by_catagory(str1)
	dic2 = split_by_catagory(str2)

	same = [False, False]
	has = [False, False]
	L = (dic1['C'], dic2['C'], dic1['E'], dic2['E'])
	S = (len(L[0]) > 0, len(L[1]) > 0, len(L[2]) > 0, len(L[3]) > 0)

	if S[0] and S[1] :
		same[0] = list_is_same(L[0], L[1])
		has[0] = True

	if S[2] and S[3] :
		same[1] = list_is_same(L[2], L[3])
		has[1] = True

	if has[0] and has[1] : return same[0] and same[1]
	return same[0] or same[1]


#两个list中不同的元素
def list_is_same(list1, list2):
	diff1 = set(list1).difference(set(list2))
	diff2 = set(list2).difference(set(list1))
	diff = diff1.union(diff2)
	return len(diff) == 0


#返回字符分类
def split_by_catagory(strg):
	#strg = TranslateNumbers(strg)

	dic = {'E':[], 'C':[], 'N':[]}

	last_catf = 'X'
	for c in strg:
		catf = unicodedata.category(c)

		if IsNumber(c) :
			if last_catf == 'E' and catf == 'Lo':# 英文后接的中文数字，不认为是数字
				pass
			elif last_catf == 'X' :# 语句的第一个数字不认为是数字
				catf = unicodedata.category(c) 
			else:		
				catf = last_catf

		#print c, catf

		if catf[0] == 'N' : catf = 'N'
		elif catf in ('L', 'Ll') : catf = 'E' #不分大小写
		elif catf == 'Lo' : catf = 'C' # 中文
		elif catf in ('N', 'E', 'C') : pass
		else : continue #其他都忽略

		if catf == last_catf:
			cat_list = dic[catf]
			cnt = len(cat_list)
			dic[catf][cnt-1] = cat_list[cnt-1] + c
		else:
			dic[catf].append(c)

		last_catf = catf

	for key, val in dic.iteritems():
		dic[key] = [TranslateNumbers(strg) for strg in val]

	return dic


text_nums = [
	('10', '9', '8', '7', '6', '5', '4', '3', '2', '1'),
	('X', 'IX', 'VIII', 'VII', 'VI', 'V', 'IV', 'III', 'II', 'I'),
	('十', '九', '八', '七', '六', '五', '四', '三', '二', '一'),	
	('拾', '玖', '捌', '柒', '陆', '伍', '肆', '叁', '贰', '壹'),
]

text_nums = zip(text_nums[0], text_nums[1], text_nums[2], text_nums[3])


def IsNumber(c):
	for tup in text_nums:
		if c in tup: return True
	return False


def TranslateNumbers(uchar):
	for group in text_nums :
		for uchr in group[1:] :
			reg = r'(?ui)%s$' % uchr
			uchar = re.sub(reg, '%s' % group[0], uchar)

	return uchar



