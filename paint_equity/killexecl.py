from wmi import WMI

def terminateProcess(processName):
    for i in WMI().Win32_Process(caption=processName):
        i.Terminate()


