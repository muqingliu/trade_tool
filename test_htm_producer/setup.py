from distutils.core import setup 
import py2exe 

setup(console=["main_test_parser_atr.py"],data_files=["common_echart.js","system.ini","echarts.js"]) 