#!/usr/bin/env python2

try:
    import os
    from os.path import exists, isdir, isfile, join

    import urllib
    
    #from Queue import Queue
    #from multiprocessing import Lock, Process, Queue
    from multiprocessing import Process
    
    from lxml import etree
    
    import APICtrl as API
    import FWTools
    import pkgTools
    from pkgManagerDM import PkgFile, VitaFile
    from MessageTools import Print, DPrint, ManageMessage 
except ImportError, e:
    assert False, 'import error in pkgManagerCtrl : {0}'.format(e)
    
class Controllers():
    def __init__(self, iniFile):
        API.Subscribe('StopControllers', lambda args: self.Stop(*args))
        
        self.iniCtrl = IniCtrl(iniFile)

        #self.messageCtrl = MessageCtrl(ui = 'stdout') ## message displaid on the stdout

        res, code, message = self.iniCtrl.ParseIni()
        #~ messageCtrl.ManageMessage(code, message)
        
        #~ API.Send('ParseIni')

        pkgDirectory, code, message = self.iniCtrl.GetValue('pkgDirectory')
        pkgGameFile, code, message = self.iniCtrl.GetValue('pkgGameFile')
        pkgDLCFile, code, message = self.iniCtrl.GetValue('pkgDLCFile')
        pkgUpdateFile, code, message = self.iniCtrl.GetValue('pkgUpdateFile')
        vitaDirectory, code, message = self.iniCtrl.GetValue('vitaDirectory')
        nbDownloadQueues, code, message = self.iniCtrl.GetValue('nbDownloadQueues')

        self.pkgCtrl = PkgCtrl(pkgDirectory, pkgGameFile, pkgDLCFile, pkgUpdateFile)
        self.vitaCtrl = VitaCtrl(vitaDirectory)
        self.DownloadCtrl = DownloadCtrl(nbDownloadQueues)
        
    def Stop(self, *args):
        res = ''
        code = 0
        message = ''
        
        self.iniCtrl.Stop()
        self.pkgCtrl.Stop()
        self.vitaCtrl.Stop()
        self.DownloadCtrl.Stop()
        
        return res, code, message
        
class DataCtrl():
    def __init__(self):
        API.Subscribe('GetModelAttributes', lambda args: self.GetModelAttributes(*args))

    def GetModelAttributes(self, *args):
        res = ''
        code = 0
        message = ''
        
        className = args[0]

        if className == 'PkgFile':
            res = PkgFile.GetClassVarsData()
        elif className == 'VitaFile':
            res = VitaFile.GetClassVarsData()
        else:
            code = -1
            message = className + ' class does not exist'
            
        return res, code, message
        
class PkgCtrl(DataCtrl):
    def __init__(self, directory, gameFile, dlcFile, updateFile):
        DataCtrl.__init__(self)
        
        self.directory = directory
        self.gameFile = gameFile
        self.dlcFile = dlcFile
        self.updateFile = updateFile
        
        self.pkgs = []
        #self.renamePkg = 'bin\\renamePkg.exe'
        self.renamePkg = 'renamePkg.exe'
 
        API.Subscribe('RefreshPkgsData', lambda args: self.RefreshPkgsData(*args))
        API.Subscribe('GetPkgsData', lambda args: self.GetPkgsData(*args))

        API.Subscribe('RenamePkgFile', lambda args: self.RenamePkgFile(*args))
        
        #API.Subscribe('DownloadPkg', lambda args: self.DownloadPkg(*args))
        
        API.Subscribe('GetPkgDirectory', lambda args: self.GetDirectory(*args))
        API.Subscribe('SetPkgDirectory', lambda args: self.SetDirectory(*args))

        API.Subscribe('GetGameFile', lambda args: self.GetGameFile(*args))
        API.Subscribe('SetGameFile', lambda args: self.SetGameFile(*args))

    def GetDirectory(self, *args):
        return self.directory, 0, ''
        
    def SetDirectory(self, *args):
        res = ''
        
        #if (args[0] != None) or (args[0] != ''):
            #if (exists(args[0]) == True) and (isdir(args[0]) == True):
        self.directory = args[0]
            #else:
                #code = -1
                #message = args[0] + ' is not a directory or does not exist'
        #else:
            #code = -1
            #message = args[0] + ' is not a directory or does not exist'
            
        return res, 0, ''
        
    def GetGameFile(self, *args):
        return self.gameFile, 0, ''
    
    def SetGameFile(self, *args):
        self.gameFile = args[0]
        
        return '', 0, ''
        
    def GetDLCFile(self, *args):
        return self.dlcFile, 0, ''
    
    def SetDLCFile(self, *args):
        self.dlcFile = args[0]
        
        return '', 0, ''
        
    def GetUpdateFile(self, *args):
        return self.updateFile, 0, ''
    
    def SetUpdateFile(self, *args):
        self.updateFile = args[0]
        
        return '', 0, ''

    def RefreshPkgsData(self, *args):
        code = 0
        message = ''
        
        ## test if the specified pkg directory is a directory and exists
        if (self.directory != None) or (self.directory != ''):
            if (exists(self.directory) == True) and (isdir(self.directory) == True):
                self.pkgs = []

                pkgFiles = FWTools.GetListFiles('.pkg', self.directory)
                for pkgFile in pkgFiles:
                    ## gather all information for pkg
                    size = FWTools.GetFileSize(join(self.directory, pkgFile))

                    ## TODO : get the validity of the pkg : local, local and not a pkg, distant pkg (when nopaystation data will be integrated)
                    validity = 'local'
                    #validity = 'localError'
                    #validity = 'distant'
                    
                    ## TODO : call to a sfo parser in pkg to get all needed info
                    pkgFile = PkgFile(filename = pkgFile, fileSize = size, validity = validity, downloadURL = 'http://zeus.dl.playstation.net/cdn/EP0850/PCSB00779_00/EP0850-PCSB00779_00-AXIOMVERGE000000_bg_1_de788236d479ef1856369b4fc5870b918f2150f8.pkg')
                    self.pkgs.append(pkgFile)
                
                if (self.gameFile != None) or (self.gameFile != ''):
                    if (exists(self.gameFile) == True) and (isfile(self.gameFile) == True):
                        fd = open(self.gameFile, 'r')
            
                        fd.write(etree.tostring(root, pretty_print=True))
                        
                        fd.close()
            else:
                code = -1
                message = self.directory + ' is not a directory or does not exist'
        else:
            code = -1
            message = 'Pkg directory is empty'
            
        return '', code, message

    def GetPkgsData(self, *args):
        pkgData = []
        code = 0
        message = ''

        for pkg in self.pkgs:
            res, code, message = pkg.Serialize()
            pkgData.append(res)

        return pkgData, code, message

    def RenamePkgFile(self, *args):
        res = ''
        code = 0
        message = ''
        
        if (self.directory != None) or (self.directory != ''):
            if (exists(self.directory) == True) and (isdir(self.directory) == True):
                pkgFile = args[0]
                pkgFile = join(self.directory, pkgFile)

                currentDir = os.getcwd()
                os.chdir('./bin/')
                #cmd = join(os.getcwd(), self.renamePkg)
                cmd = self.renamePkg
                renameCmd = [cmd]

                renameCmd.append(pkgFile)
                #print 'pwd', os.getcwd()
                
                try:
                    subprocess.call(renameCmd)
                except :
                    code = -1
                    message = 'Error in renamePkg execution ' + str(renameCmd)
                    
                os.chdir(currentDir) 
            else:
                code = -1
                message = 'The pkg directory is not a directory or does not exist'
        else:
            code = -1
            message = 'The pkg directory is empty'

        return res, code, message

    #def LoadGame(self, *args):
        #pass

    #def LoadDLC(self, *args):
        #pass
        
    #def LoadUpdate(self, *args):
        #pass
        
    def Stop(self):
        pass
        
class VitaCtrl():
    def __init__(self, directory):
        self.directory = directory

        API.Subscribe('GetVitaDirectory', lambda args: self.GetDirectory(*args))
        API.Subscribe('SetVitaDirectory', lambda args: self.SetDirectory(*args))
        API.Subscribe('GetLocalVitaData', lambda args: self.GetLocalVitaData(*args))
        
    #def SetDirectory(self,directory):
        #self.directory = directory

    def GetDirectory(self, *args):
        return self.directory, 0, ''
        
    def SetDirectory(self, *args):
        self.directory = args[0]
        
        return '', 0, ''

    def GetLocalVitaData(self, *args):
        vitaApps = []
        message = ''
        
        if (exists(self.directory) == True) and (isdir(self.directory) == True):
            ## list all app/dlc/update
            vitaApps = []
        else:
            code = -1
            message = self.directory + ' is not a directory or does not exist'

        return vitaApps, code, message
    
    def Stop(self):
        pass
        
class IniCtrl():
    def __init__(self, inifile):
        self.inifile = inifile
        self.values = {}
        
        API.Subscribe('ParseIni', lambda args: self.ParseIni(*args))
        API.Subscribe('GetIniValue', lambda args: self.GetValue(*args))
        API.Subscribe('SetIniValue', lambda args: self.SetValues(*args))
        API.Subscribe('SerializeIni', lambda args: self.SerializeIni(*args))

    def ResetValues(self):
        self.values = {}

    def SetValues(self, *args):
        key = args[0]
        value = args[1]

        self.values[key] = value

        return '', 0, ''

    def GetValue(self, *args):
        key = args[0]
        if key in self.values:
            res = self.values[key]
            code = 0
            message = ''
        else:
            res = ''
            code = -1
            message = key + ' value does not exist'

        return res, code, message

    def ParseIni(self, *args):
        code = 0
        message = ''
        
        if (exists(self.inifile) == True) and (isfile(self.inifile) == True):
            tree = etree.parse(self.inifile)
            root = tree.getroot()

            self.ResetValues()
            for child in list(root):
                self.SetValues(child.tag, child.text)
                #print 'child.tag', child.tag, child.text
            
            #for value in tree.xpath("/ini"):
                #print 'value', value
                #print 'list(value)', list(value)
                #print(user.get("data-id"))

            code = 0
            message = 'Ini parsed successfully'
        else:
            code = 0
            message = 'Ini file does not exists or is not a file'

        return '', code, message
        
    def SerializeIni(self, *args):
        code = 0
        message = ''
        
        if (exists(self.inifile) == True) and (isfile(self.inifile) == True):
            root = etree.Element('ini')
            for key, value in self.values.items():
                sub = etree.SubElement(root, key)
                sub.text = value

            fd = open(self.inifile, 'w')
            
            fd.write(etree.tostring(root, pretty_print=True))
            
            fd.close()

            code = 0
            message = 'Ini Serialized successfully'
        else:
            code = -1
            message = 'Ini file does not exists or is not a file'

        return '', code, message
    
    def Stop(self):
        pass
        
class DownloadCtrl():
    def __init__(self, nbDownloadQueues):
        #self.nbDownloadQueues = nbDownloadQueues
        #self.downloadQueues = []
        #for i in range(self.nbDownloadQueues):
            #dQueue = Queue()
            #self.downloadQueues.append(dQueue)

        self.directory = ''
        self.processes = []
        
        self.onGoingDownload = False
            
        API.Subscribe('SetDownloadDirectory', lambda args: self.SetDownloadDirectory(*args))
        API.Subscribe('SetDownloadUrls', lambda args: self.SetDownloadUrls(*args))
        API.Subscribe('StartDownload', lambda args: self.StartDownload(*args))
        API.Subscribe('StopDownload', lambda args: self.StopDownload(*args))

    def SetDownloadDirectory(self, *args):
        res = ''
        code = 0
        message = ''

        directory = args[0]
        #~ print 'download directory', directory 

        if (directory != None) or (directory != ''):
            if (exists(directory) == True) and (isdir(directory) == True):
                self.directory = directory
            else:
                code = -1
                message = 'The download directory is not a directory or does not exist'
        else:
            code = -1
            message = 'The download directory is empty'
            
        return res, code, message
        
    def SetDownloadUrls(self, *args):
        res = ''
        code = 0
        message = ''
        
        urlData = args[0]

        process = Process(target=self.DownloadProcess, args=(urlData,))
        self.processes.append(process)

        return res, code, message

    def StartDownload(self, *args):
        print 'StartDownload', args
        res = ''
        code = 0
        message = ''

        if self.directory != '':
            if self.onGoingDownload == False:
                self.onGoingDownload = True
                for process in self.processes:
                    process.start()
                    
                #for process in self.processes:
                    #process.join()
            else:
                code = -1
                message = 'Files are already being downloaded'
        else:
            code = -1
            message = 'The download directory is empty'
            
        return res, code, message

    def StopDownload(self, *args):
        res = ''
        code = 0
        message = ''
        
        if self.onGoingDownload == True:
            for process in self.processes:
                process.terminate()
                process.join()

        ## reinit the process list
        self.processes = []
        self.onGoingDownload = False
        
        ## TODO : clean the not finisher downloaded file?
        
        return res, code, message
        
    def DownloadProcess(self, urlData):
        res = ''
        code = 0
        message = ''
        
        for url, destination in urlData:
            try:
                destination = '.'.join((destination, 'part'))
                filename = join(self.directory, destination)
                downloadFile = urllib.URLopener()
                downloadFile.retrieve(url, filename, self.ProgressCallback)
                    
                #urllib.urlretrieve(url, filename=destination)
            except Exception, e:
                DPrint('error downloading {0}: {1}'.format(url, e), -1)
                
    def ProgressCallback(self, blocks, block_size, total_size):
        #blocks->data downloaded so far (first argument of your callback)
        #block_size -> size of each block
        #total-size -> size of the file
        print 'downloaded ', blocks/float(total_size), '%'

    def Stop(self):
        self.StopDownload('')
