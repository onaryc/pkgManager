#!/usr/bin/env python2

try:
    import APICtrl as API
    from pkgManagerUI import UI
    from pkgManagerCtrl import Controllers
    import MessageTools
except ImportError:
    assert False, "import error in main"

#~ host = 'localhost'
host = '127.0.0.1'
port = 1234

MessageTools.Init(pDebug = False)

## start the communication layer
API.Init(host, port)

## start the controllers
controllers = Controllers('pkgManager.ini')

## start the ui
ui = UI()
print 'ui 0', ui
#MessageTools.SetUI(ui)
ui.Start()


