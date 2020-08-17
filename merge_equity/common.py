#!/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime

def AddDay(cur_day, days):
	cur_date = datetime.date(cur_day / 10000 + 2000, cur_day / 100 % 100, cur_day % 100)
	new_date = cur_date + datetime.timedelta(days=days)
	new_day = new_date.year % 100 * 10000 + new_date.month * 100 + new_date.day
	return new_day