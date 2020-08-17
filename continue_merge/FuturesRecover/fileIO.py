import os
import time
import config.config as config


#filename,sourcelist,recoveredlist,InstrumentsName
#nmode 0:增量 1：全
def filewrite(InstrumentsName,DocName,nlist,nmode):
    # DocName = ("source","recover")
    # lsitName = (sourcelist,recoveredlist)
    _path=os.getcwd()+"\\"+config.CON_DOCNAME+"\\"+DocName
    if not os.path.exists(_path):
        os.makedirs(_path)

    filename=InstrumentsName+"L0.txt"

    if nmode :
        file_object = open(_path+'/'+filename,'w')
    else:
        file_object = open(_path+'/'+filename,'a')

    for idx in nlist:
        _nTime=str(idx['Time'])
        _nTime="20"+_nTime[0:2]+"/"+_nTime[2:4]+"/"+_nTime[4:6]+"-"+_nTime[6:8]+":"+_nTime[8:10]
        _tmpstr=_nTime+"\t"+str(round(idx['OpenPrice'],3))+"\t"+str(round(idx['ClosePrice'],3))+"\t"+str(round(idx['HighestPrice'],3))+"\t"+str(round(idx['LowestPrice'],3))+"\t"+str(idx['Volume'])
        file_object.writelines(_tmpstr)
        file_object.writelines('\n')
    file_object.close()

