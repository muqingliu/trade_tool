from distutils.core import setup 
import py2exe 

setup(console=["main.py"],data_files=["7z.dll","7z.exe","sys.conf"]) 