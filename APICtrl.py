#!/usr/bin/env python2

try:
    import ast
    import socket
    from threading import Thread
    from MessageTools import Print, DPrint, ManageMessage
except ImportError, e:
    assert False, 'import error in APICtrl : {0}'.format(e)

sockServer = ''
errorServer = False
sockClient = ''
errorClient = False
apis = {}

def Init(host, port):
    global sockServer, sockClient 
    global errorServer, errorClient
    global listenThread
    global debugOutput

    sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    DPrint('Api Init Start')
    
    ## init server
    try:
        sockServer.bind((host, port))
        DPrint('server socket bind ok')
        #print 'server socket bind ok'
        
        listenThread = Listen(sockServer)
        listenThread.start()
    except socket.error as e:
        DPrint('server socket bind failed ({0}): {1}'.format(e.errno, e.strerror), -1)
        errorServer = True
    
    ## init client
    try:
        sockClient.settimeout(5)
        sockClient.connect((host, port))
        sockClient.settimeout(None)
        DPrint('client connection on {} ok\n'.format(port))
    except socket.error:
        DPrint('client socket connection failed', -1)
        errorClient = True

    DPrint('Api Init End')
        
def Stop():
    global sockServer, sockClient
    global listenThread
    
    sockServer.close()
    sockClient.close()
    
def Subscribe(name, command):
    apis[name] = command

def Send(api, *args):
    global sockClient, errorServer, errorClient
    res = ''

    DPrint('Api Send Start')
    
    if (errorServer != True) and (errorClient != True):
        try:
            DPrint('client sending api ' + api)
            
            ## encrypting the message : dict to str
            message = {'api': api, 'args':args}
            message = str(message)

            ## send the api message
            sockClient.settimeout(1)
            sockClient.send(message)
            sockClient.settimeout(None)
            
            ## receiving the result
            try:
                ## receiving the header of the message : size for now
                size = sockClient.recv(1024)
                size = ast.literal_eval(size)
                DPrint('client recv header size ' + str(size))
                
                ## recieving the message itself
                resSock = ''
                remainingSize = size
                while remainingSize > 0:
                    tmpSock = sockClient.recv(1024)
                    tmpSize = len(tmpSock)

                    resSock += tmpSock
                    remainingSize -= tmpSize
            except socket.error as e:
                DPrint('connection socket recv failed ({0}): {1}'.format(e.errno, e.strerror), -1)
                resSock = ''
                
            
            ## decrypt the result : str to dict
            try:
                resSock = ast.literal_eval(resSock)
                
                res = resSock['res']
                code = resSock['code']
                message = resSock['message']

                #DPrint(0, 'client recieving api res ' + res)
                DPrint('client recieving api res')
            except:
                ## TODO manage error
                DPrint('error in decrypting api result ' + resSock, -1)
        except socket.error as e:
            DPrint('client sending failed ({0}): {1}'.format(e.errno, e.strerror), -1)

    DPrint('Api Send End')

    return res
        
class Listen(Thread):
    def __init__(self, socket):
        Thread.__init__(self)
        self.socket = socket

    def run(self):
        self.socket.listen(2)
        connection, address = self.socket.accept()
        DPrint('Server {} connected'.format(address))
            
        while True:
            DPrint('Api Server Wait for message')
            
            try:
                resConnection = connection.recv(1024)
            except socket.error as e:
                DPrint('connection socket recv failed ({0}): {1}'.format(e.errno, e.strerror), -1)
                break

            DPrint('Api server recieving ' + resConnection)

            #print 'resConnection', resConnection
            ## decrypt the result : str to dict
            if resConnection != '':
                try:
                    res = ast.literal_eval(resConnection)
                    api = res['api']
                    args = res['args']
                except:
                    res = ''
                    code = -1
                    message = 'unable to decrypt the content'
                    
                ## test the existence of the api
                if api in apis:
                    res, code, message = apis[api](args)
                else:
                    res = ''
                    code = -1
                    message = 'api unknown'
            else:
                res = ''
                code = -1
                message = 'missing api'

            ## manage the message : terminal, log, ...
            ManageMessage(code, message)
                    
            ## encrypt the result : dict to str
            res = {'res': res, 'code': code, 'message': message}
            #print 'res', res
            resSize = len(str(res))

            #print 'resSize', resSize
            
            ## send the header of the message : size for now
            DPrint('Api server send header ' + str(resSize))
            connection.send(str(resSize))

            ## send the body of the message
            if resSize > 0:
                DPrint('Api server responding ')
                connection.send(str(res))
