from __future__ import unicode_literals
import re
import log

#---------------------------------------------------------------
def get_url_file_postfix(purl):
	m = re.search(r'(?ui).+?\.([^\.]+?)$', purl)
	if m is None : return ''
	return m.group(1)

#---------------------------------------------------------------
#format dictionary into a readable string format:
def dict_str(c):

	def brace_group_str(v, beg, end):
		fill = beg
		app = False
		for val in v:
			fill += var_str(val) + ', '
			app = True
		if app : fill = fill[:-2]
		return fill + end

	def list_str(v):
		return brace_group_str(v, '[', ']')

	def tuple_str(v):
		return brace_group_str(v, '(', ')')
	
	def str_str(v):
		fill = '"' + v.decode('utf8') + '"'
		return fill

	def uni_str(v):
		fill = '"' + v + '"'
		return fill
		
	def var_str(v):
		if isinstance(v, str) : return str_str(v)
		if isinstance(v, unicode) : return uni_str(v)
		if isinstance(v, dict) : return dict_str(v)
		if isinstance(v, list) : return list_str(v)
		if isinstance(v, tuple) : return tuple_str(v)
		return str(v)

	fill = '{'
	for k, v in c.iteritems():
		fill += '\n ' + var_str(k) + ' : ' + var_str(v) + ', '

	return fill[:-2] + '\n}'


#---------------------------------------------------------------
def str_middle(co, tuple_begin_anchol, str_end, case=False):
	c = co
	beg_off_set = 0

	if not case:
		c = co.lower()
		str_end = str_end.lower()
		tuple_begin_anchol = (x.lower() for x in tuple_begin_anchol)
	
	for anchol in tuple_begin_anchol:
		try:
			beg_off_set = c.find(anchol, beg_off_set)
		except:
			log.WriteError("find error")
			return ''

		if beg_off_set == -1 : return ''
		beg_off_set += len(anchol)

	end_pt = c.find(str_end, beg_off_set)
	if end_pt == -1 : return c[beg_off_set:]
	#return the original string, not the lower cased.
	return co[beg_off_set : end_pt]


#----------------------
def trim_to_unicode(strg):
	if strg is None : return ''
	if not isinstance(strg, basestring): return strg

	if isinstance(strg, str):
		return strg.strip().decode('utf8')
		
	if isinstance(strg, unicode):
		return strg.strip()
