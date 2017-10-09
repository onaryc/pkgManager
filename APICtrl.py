#!/usr/bin/env python2

try:
    import ast
    import socket
    from threading import Thread
except ImportError:
    assert False, "import error in APICtrl"

sockServer = ''
errorServer = False
sockClient = ''
errorClient = False
apis = {}

def Init(host, port):
    global sockServer, sockClient 
    global errorServer, errorClient
    global listenThread

    sockServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    ## init server
    try:
        print 'host', host
        print 'port', port
        sockServer.bind((host, port))
        print 'server socket bind ok'
        
        listenThread = Listen(sockServer)
        listenThread.start()
    except socket.error as e:
        ## TODO manage error
        print 'server socket bind failed ({0}): {1}'.format(e.errno, e.strerror)
        errorServer = True
    
    ## init client
    try:
        sockClient.settimeout(5)
        sockClient.connect((host, port))
        sockClient.settimeout(None)
        print 'client connection on {} ok\n'.format(port)
        #~ print 'init sockClient', sockClient
    except socket.error:
        ## TODO manage error
        print 'client socket connection failed'
        errorClient = True
        
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
    
    #~ print 'send sockClient', sockClient
    if (errorServer != True) and (errorClient != True):
        try:
            print 'client sending api', api
            
            ## encrypting the message : dict to str
            message = {'api': api, 'args':args}
            message = str(message)
            sockClient.settimeout(1)
            sockClient.send(message)
            sockClient.settimeout(None)
            
            ## receiving the result
            try:
                resSock = sockClient.recv(8192)
            except socket.error as e:
                print 'connection socket recv failed ({0}): {1}'.format(e.errno, e.strerror)
                resSock = ''
                
            
            ## decrypt the result : str to dict
            try:
                resSock = ast.literal_eval(resSock)
                
                res = resSock['res']
                #~ resType = resSock['resType']
                code = resSock['code']
                message = resSock['message']
                
                print 'client recieving api res', res
            except:
                ## TODO manage error
                print 'error in decrypting api result', resSock
        except socket.error:
            print 'client sending failed'

    return res
        
class Listen(Thread):
    def __init__(self, socket):
        Thread.__init__(self)
        self.socket = socket

    def run(self):
        self.socket.listen(2)
        connection, address = self.socket.accept()
        print 'Server {} connected'.format( address )
            
        while True:
            try:
                resConnection = connection.recv(1024)
            except socket.error as e:
                 ## TODO manage error
                print 'connection socket recv failed ({0}): {1}'.format(e.errno, e.strerror)
                break
        
            print 'server recieving', resConnection
            
            ## decrypt the result : str to dict
            if resConnection != '':
                res = ast.literal_eval(resConnection)
                api = res['api']
                args = res['args']
                
                ## test the existence of the api
                if api in apis:
                    res, code, message = apis[api](args)
                    resType = ''
                
                    #~ print 'api res', res
                    ## TODO manage the error
                else:
                    res = ''
                    resType = 'string'
                    code = -1
                    message = 'api unknown'
            else:
                res = ''
                resType = 'string'
                code = -1
                message = 'missing api'

            ## encrypt the result : dict to str
            res = {'res': res, 'resType': resType, 'code': code, 'message': message}
            res = str(res)
            print 'server sending', res
            
            connection.send(res)
