#!/usr/bin/env python2

try:
    import ast
    import socket
    from threading import Thread
    from MessageTools import Print, DPrint, ManageMessage
except ImportError, e:
    assert False, 'import error in APICtrl : {0}'.format(e)

apiCtrl = None

def GetCtrl():
    global apiCtrl
    
    return apiCtrl
    
def SetCtrl(apiCtrlInstance):
    global apiCtrl
    
    apiCtrl = apiCtrlInstance
    
def Init(host, port, aSocket=False):
    global apiCtrl

    apiCtrl = APICtrl(host, port, aSocket)
    
def Stop():
    global apiCtrl
    
def ListApis():
    global apiCtrl

    apiCtrl.ListApis()
     
def Subscribe(name, command):
    global apiCtrl

    apiCtrl.Subscribe(name, command)
    
def Send(api, *args):
    global apiCtrl

    res = apiCtrl.Send(api, *args)
    
    return res

class APICtrl():
    def __init__(self, host, port, aSocket=False):
        self.apis = {}
        self.host = host
        self.port = port
        self.activateSocket = aSocket
        
    def ListApis(self):
        print self.apis
     
    def Subscribe(self, name, command):
        self.apis[name] = command

    def Send(self, api, *args):
        res = ''

        DPrint('Api Send Start')
    
        if api in self.apis:
            res, code, message = self.apis[api](args)
        else:
            res = ''
            code = -1
            message = 'api unknown'

        ManageMessage(code, message)
                    
        DPrint('Api Send End')

        return res

