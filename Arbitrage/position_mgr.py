
import pandas as pd
import numpy as np

class class_position(object):
    def __init__(this, datetime, price, number, dir):
        this.datetime = datetime
        this.price = price
        this.number = number
        this.dir = dir  #买多还是卖空


class class_position_mgr(object):
    def __init__(this):
        this.dict_positions = {}
        this.wait_change_period_ids = {} #等待换期的合约
        pass


    def add_position(this, datestamp, id, price, number, dir):
        #datetime = str(datestamp)
        if not this.dict_positions.has_key(id):
            this.dict_positions[id] = class_position(datestamp, price, number, dir)
            return 

        pos = this.dict_positions[id]
        if pos.dir != dir: return 
        total = pos.price * pos.number + price * number
        pos.number = pos.number + number
        pos.price = total/float(pos.number)
        pos.datetime = datestamp


    def remove_position(this, id, number):
        if not this.dict_positions.has_key(id):return 
        pos = this.dict_positions[id]
        if number > pos.number:  number = pos.number
        pos.number -= number
        if pos.number == 0:del this.dict_positions[id]
        return pos.price, number

    def wait_change_period(this, id, datestamp):
        if not this.wait_change_period_ids.has_key(id):this.wait_change_period_ids[id] = []
        this.wait_change_period_ids[id].append(datestamp)

    def get_wait_change_period(this, id):
        if not this.wait_change_period_ids.has_key(id): return None
        return this.wait_change_period_ids[id]
        

    def get_position_by_id(this, id):
        if not this.dict_positions.has_key(id):return None
        return this.dict_positions[id]

    def get_position_dir_by_id(this,id):
        pos = this.get_position_by_id(id)
        if pos is None: return None
        return pos.dir

    def get_all_positions(this):
        return this.dict_positions

    def get_position_ids(this):
        return this.dict_positions.keys()

    def get_position_number_by_id(this, id):
        pos = this.get_position_by_id(id)
        if pos is None: return None
        return pos.number


    def get_position_price_by_id(this,id):
        pos = this.get_position_by_id(id)
        if pos is None: return None
        return pos.price


