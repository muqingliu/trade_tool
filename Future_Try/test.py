import sys
reload(sys)
sys.setdefaultencoding('utf8')
from pyecharts import Line

attr = ['周一', '周二', '周三', '周四', '周五', '周六', '周日', ]
line = Line("折线图示例")
line.add("最高气温", attr, [11, 11, 15, 13, 12, 13, 10], mark_point=["max", "min"], mark_line=["average"])
line.add("最低气温", ['周一', '周二', '周三', '周四', '周五', '周六', '周日', ], [1, -2, 2, 5, 3, 2, 0], mark_point=["max", "min"],
         mark_line=["average"], yaxis_formatter="°C")
line.show_config()
line.render()
