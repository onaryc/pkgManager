#!/usr/bin/env python2

try:
    import APICtrl as API
    #from APICtrl import APICtrl2, SetAPICtrlInstance
    #import APICtrl
    from pkgManagerUI import UI
    from pkgManagerCtrl import Controllers
    import MessageTools
except ImportError, e:
    assert False, 'import error in main : {0}'.format(e)

if __name__ == "__main__":
    #~ host = 'localhost'
    host = '127.0.0.1'
    port = 1234

    MessageTools.Init(pDebug = False)

    ## start the communication layer
    #API = APICtrl2(host, port, False)
    #SetAPICtrlInstance(API)
    API.Init(host, port, False)

    ## start the controllers
    controllers = Controllers('pkgManager.ini')

    ## start the ui
    ui = UI()
    
    ui.Start()


