from distutils.core import setup 
import py2exe 

setup(console=["auto_test.py"],data_files=["system.ini"]) 