#!/usr/bin/env python2

try:
    import APICtrl as API
    
    #from blessings import Terminal
    from colorama import init, Fore, Back, Style
except ImportError:
    assert False, "import error in MessageTools"

init()

logFile = ''
#ui = ''
debug = True
#term = Terminal()

def Init(pLogFile = '', pDebug = True):
    global logFile, debug

    logFile = pLogFile
    debug = pDebug

#def SetUI(pUi):
    #global ui

    #print 'ui 1', ui

    #ui = pUi

def SetDebug(pDebug):
    global debug
    
    debug = pDebug

def GetTextColor(code, ground):
    color = ground.WHITE
    
    if code == 0:
        color = ground.GREEN
    elif code == -1:
        color = ground.RED
    elif code == -2:
        color = ground.YELLOW

    return color

def DPrint(message, code = 0):
    global debug

    if debug == True:
        color = GetTextColor(code, Back)
        print color + 'Debug : ' + message + Style.RESET_ALL
        
def Print(message, code):
    global ui
    
    if message != '':
        color = GetTextColor(code, Fore)
        print color + message + Style.RESET_ALL

def LogMessage(message, code):
    global logFile

def ManageMessage(code, message):
    ## print the message
    Print(message, code)

    ## log the message
    LogMessage(message, code)

    ## send the message to the ui
    #API.Send('SendUIMessage', message, code)
