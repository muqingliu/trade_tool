from __future__ import unicode_literals
import func
import urllib2
import re

cht2chs_dict = {}

def init():
	table_url = 'http://svn.wikimedia.org/svnroot/mediawiki/trunk/phase3/includes/ZhConversion.php'

	response = urllib2.urlopen(table_url)
	content = response.read()
	entries = func.str_middle(content, ('$zh2Hans = array(',), ')')

	m = re.findall(r"(?mu)'(\w)' => '(\w)',", entries)

	cht2chs_dict = { key:value for key, value in m}


def translate(uchar):
	if uchar in cht2chs_dict:
		return cht2chs_dict[uchar]
	return uchar