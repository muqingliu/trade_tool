MAX_POSITION_NUMBER = 9999999999
USE_REFERENDUM_PRICE = False

LOG_ERROR = "error"
LOG_DATA = "data_error"
LOG_TRADE = "trade_error"
LOG_RECORD = "trade_record"
LOG_POSITION_CHANGE = "position_change"
LOG_MONTH_NET_VALUE = "month_net_value"
LOG_YEAR_NET_VALUE = "year_net_value"
LOG_SUMMARY_REPORT = "summary_report"
LOG_EACH_STOCK_PROFIT = "each_stock_profit"

LOG_DIVIEND_DIVIEND = "diviend_diviend"
LOG_DIVIEND_TRANSFER = "diviend_transfer"
LOG_DIVIEND_QTY_COST = "diviend_qty_cost" 
LOG_DIVIEND_BUY = "diviend_buy"
LOG_DIVIEND_BUY_FAILED = "diviend_buy_failed"


g_log_switch = {
                LOG_ERROR : True,
                LOG_DATA : False,
                LOG_TRADE : True,
                LOG_RECORD : True,
                LOG_POSITION_CHANGE : True,
                LOG_EACH_STOCK_PROFIT : True,
                LOG_DIVIEND_DIVIEND : True,
                LOG_DIVIEND_TRANSFER : True, 
                LOG_DIVIEND_QTY_COST : False,
                LOG_DIVIEND_BUY : True,
                LOG_DIVIEND_BUY_FAILED : False,
                }


g_report_switch = {
                   LOG_RECORD : True,
                   LOG_MONTH_NET_VALUE : True,
                   LOG_YEAR_NET_VALUE : True,
                   LOG_SUMMARY_REPORT: True,
                   }

def enum(**enums):
    return type('Enum', (), enums)
 