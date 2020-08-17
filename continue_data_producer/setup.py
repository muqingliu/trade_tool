from distutils.core import setup 
import py2exe 

setup(console=["continue_data_producer.py"],data_files=["system.ini","exchange.ini","main_contract.ini"]) 