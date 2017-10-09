#!/usr/bin/env python2

try:
    import APICtrl as API
    from pkgManagerUI import UI
    from pkgManagerCtrl import Controllers
except ImportError:
    assert False, "import error in main"

#~ host = 'localhost'
host = '127.0.0.1'
port = 1234

## start the communication layer
API.Init(host, port)

## start the controllers
controllers = Controllers('pkgManager.ini')

## start the ui
ui = UI()
ui.Start()
