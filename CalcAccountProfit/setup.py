from distutils.core import setup 
import py2exe 

setup(console=["main.py"],
	data_files=["system.ini","exchange.ini", "contract_mul.ini", "contract_mar.ini"]) 