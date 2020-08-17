MAX_POSITION_NUMBER = 9999999999

LOG_DATA = "data_error"
LOG_TRADE = "trade_error"
LOG_RECORD = "trade_record"
LOG_POSITION_CHANGE = "position_change"
LOG_MONTH_NET_VALUE = "month_net_value"
LOG_YEAR_NET_VALUE = "year_net_value"
LOG_SUMMARY_REPORT = "summary_report"

g_log_switch = {
                LOG_DATA : False,
                LOG_TRADE : True,
                LOG_RECORD : True,
                LOG_POSITION_CHANGE : True
                }


g_report_switch = {
                   LOG_RECORD : True,
                   LOG_MONTH_NET_VALUE : True,
                   LOG_YEAR_NET_VALUE : True,
                   LOG_SUMMARY_REPORT: True,
                   }

def enum(**enums):
    return type('Enum', (), enums)
 