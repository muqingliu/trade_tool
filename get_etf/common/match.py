from __future__ import unicode_literals
import match_name
import db
from manga import *
from common import text

#----------------------
def setup_db(test):
	pass

#----------------------
def get_matched_manga(mng_name, test=False):
	mdb = db.MDB()
	for mng in mdb.YieldAll():
		manga_cmp = mng['name']
		if mng_name == manga_cmp : return mng
		if match_name.is_manga_name_similar(mng_name, manga_cmp):
			return mng

	return {}




