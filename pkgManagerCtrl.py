#!/usr/bin/env python2
# -*- coding: utf-8 -*-*

try:
    import os
    from os.path import exists, isdir, isfile, join, getsize

    import sys
    import time
    import timeit
    
    import urllib2
    
    #from Queue import Queue
    from threading import Thread, current_thread, Event
    import Queue
    
    from lxml import etree
    
    import APICtrl as API
    import FWTools
    import pkgTools
    #from pkgManagerDM import GamePkgFile, DLCPkgFile, UpdatePkgFile, VitaFile, DownloadFile
    from pkgManagerDM import PkgFile, VitaFile, DownloadFile
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
        pkgDBFile, code, message = self.iniCtrl.GetValue('pkgDBFile')
        vitaDirectory, code, message = self.iniCtrl.GetValue('vitaDirectory')
        nbDownloadQueues, code, message = self.iniCtrl.GetValue('nbDownloadQueues')

        self.pkgCtrl = PkgCtrl(pkgDirectory, pkgDBFile)
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

        #if className == 'GamePkgFile':
            #res = GamePkgFile.GetClassVarsData()
        #elif className == 'VitaFile':
            #res = VitaFile.GetClassVarsData()
        #elif className == 'DownloadFile':
            #res = DownloadFile.GetClassVarsData()
        #else:
            #code = -1
            #message = className + ' class does not exist'
        if className == 'PkgFile':
            res = PkgFile.GetClassVarsData()
        elif className == 'VitaFile':
            res = VitaFile.GetClassVarsData()
        elif className == 'DownloadFile':
            res = DownloadFile.GetClassVarsData()
        else:
            code = -1
            message = className + ' class does not exist'
            
        return res, code, message
        
class PkgCtrl(DataCtrl):
    def __init__(self, directory, dbFile):
        DataCtrl.__init__(self)
        
        self.directory = directory
        self.dbFile = dbFile
        #self.database = etree.fromstring('<vitaDB></vitaDB>')
        #print 'self.database init', self.database
        #self.database = etree.Element('vitaDB')
        self.database = ''
        
        self.pkgs = []
        #self.renamePkg = 'bin\\renamePkg.exe'
        self.renamePkg = 'renamePkg.exe'
        self.currentImportPercent = 0
 
        API.Subscribe('RefreshPkgsData', lambda args: self.RefreshPkgsData(*args))
        API.Subscribe('GetPkgsData', lambda args: self.GetPkgsData(*args))
        API.Subscribe('ImportNPS', lambda args: self.ImportNPS(*args))
        API.Subscribe('ResetDB', lambda args: self.ResetDB(*args))
        API.Subscribe('LoadDB', lambda args: self.LoadDB(*args))
        API.Subscribe('SaveDB', lambda args: self.SaveDB(*args))

        API.Subscribe('RenamePkgFile', lambda args: self.RenamePkgFile(*args))
        
        #API.Subscribe('DownloadPkg', lambda args: self.DownloadPkg(*args))
        
        API.Subscribe('GetPkgDirectory', lambda args: self.GetDirectory(*args))
        API.Subscribe('SetPkgDirectory', lambda args: self.SetDirectory(*args))

        API.Subscribe('GetDBFile', lambda args: self.GetDBFile(*args))
        API.Subscribe('SetDBFile', lambda args: self.SetDBFile(*args))

        self.LoadDB()

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
        
    def GetDBFile(self, *args):
        return self.dbFile, 0, ''
    
    def SetDBFile(self, *args):
        self.dbFile = args[0]
        
        return '', 0, ''
        
    def CreateDB(self):
        res = ''
        code = 0
        message = ''
        
        if (self.dbFile != None) and (self.dbFile != ''):
            rootItem = etree.Element('vitaDB')

            # serialize the xml
            fd = open(self.dbFile, 'w')
            
            fd.write(etree.tostring(rootItem, pretty_print=True))
            
            fd.close()
            
            self.database = etree.parse(self.dbFile)
            #print 'self.database', self.database, etree.Element('vitaDB')
        else:
            code = -1
            message = 'Database filename is empty'
            
        return res, code, message
        
    def ResetDB(self, *args):
        res = ''
        code = 0
        message = ''
        
        if (self.dbFile != None) and (self.dbFile != ''):
            #rootItem = self.database.getroot()
            for vitaPkg in self.database.xpath("/vitaDB/vitaPkg"):
            #for vitaPkg in rootItem:
                self.RemoveDB(vitaPkg)
        else:
            code = -1
            message = 'Database filename is empty'
            
        return res, code, message
        
    def LoadDB(self, *args):
        print 'Load DB'
        res = ''
        code = 0
        message = ''
        
        if (self.dbFile != None) or (self.dbFile != ''):
            if (exists(self.dbFile) == True) and (isfile(self.dbFile) == True):
                try: ## if the xml file is malformed
                    self.database = etree.parse(self.dbFile)
                    print 'self.database', self.database
                except:
                    pass
            else:
                code = -1
                message = 'Database file does not exists or is not a file'
        else:
            code = -1
            message = 'No database file'
            
        if self.database == '':
            self.CreateDB()
        
        return res, code, message
        
    def SaveDB(self, *args):
        res = ''
        code = 0
        message = ''
        
        if (self.dbFile != None) or (self.dbFile != ''):
            if (exists(self.dbFile) == True) and (isfile(self.dbFile) == True):
                rootItem = self.database.getroot()
                fd = open(self.dbFile, 'w')
        
                fd.write(etree.tostring(rootItem, pretty_print=True))
        
                fd.close()
            else:
                code = 0
                message = 'Database file does not exists or is not a file'
        else:
            code = -1
            message = 'No database file'
        
        return res, code, message

    def SearchDB(self, name, value):
        search = self.database.xpath("/vitaDB/vitaPkg[@"+name+"='"+value+"']")

        return search
        
    def RemoveDB(self, item):
        #self.database.getroot().remove(item)
        item.getparent().remove(item)
        
    #def SearchID(self, titleId, xmlTree):
        #search = xmlTree.xpath("/vitaDB/vitaPkg[@id='"+titleId+"']")

        #return search
        
    #def SearchRegion(self, region, xmlTree):
        #search = xmlTree.xpath("/vitaDB/vitaPkg[titleRegion='"+region+"']")

        #return search
        
    #def SearchType(self, stype, xmlTree):
        #search = xmlTree.xpath("/vitaDB/vitaPkg[@type='"+stype+"']")

        #return search

    def RefreshPkgsData(self, *args):
        code = 0
        message = ''

        getGame = args[0]
        getDlc = args[1]
        getUpdate = args[2]
        getPSM = args[3]
        getPSX = args[4]
        getPSP = args[5]
        getPSPDLC = args[6]
        if self.database != '':
            self.pkgs = []
            for vitaPkg in self.database.xpath("/vitaDB/vitaPkg"):
                contentID = ''
                titleID = ''
                titleType = ''
                titleName = ''
                titleRegion = ''
                filename = ''
                titleFW = ''
                fileSize = ''
                downloadURL = ''
                zRIF = ''
                version = ''
                validity = ''
                
                #print 'attributes', vitaPkg.attrib
                if 'contentId' in vitaPkg.attrib:
                    contentID = vitaPkg.attrib['contentId']

                if 'titleId' in vitaPkg.attrib:
                    titleID = vitaPkg.attrib['titleId']

                if 'type' in vitaPkg.attrib:
                    titleType = vitaPkg.attrib['type']

                if 'titleName' in vitaPkg.attrib:
                    titleName = vitaPkg.attrib['titleName']

                if 'titleRegion' in vitaPkg.attrib:
                    titleRegion = vitaPkg.attrib['titleRegion']

                if 'filename' in vitaPkg.attrib:
                    filename = vitaPkg.attrib['filename']
                    
                if 'titleFW' in vitaPkg.attrib:
                    titleFW = vitaPkg.attrib['titleFW']

                if 'fileSize' in vitaPkg.attrib:
                    fileSize = vitaPkg.attrib['fileSize']

                if 'downloadURL' in vitaPkg.attrib:                    
                    downloadURL = vitaPkg.attrib['downloadURL']

                if 'zRIF' in vitaPkg.attrib:
                    zRIF = vitaPkg.attrib['zRIF']

                if 'version' in vitaPkg.attrib:
                    version = vitaPkg.attrib['version']

                validity = 'distant'

                pkgFile = PkgFile(contentID = contentID, titleID = titleID, titleType = titleType, titleName = titleName, titleRegion = titleRegion, filename = filename, fileSize = fileSize, downloadURL = downloadURL , zRIF = zRIF, version = version, validity = validity)
                self.pkgs.append(pkgFile)
                #if titleType == 'dlc':
                    #gamePkgFile = self.SearchDB('titleID', titleID)
                    #if gamePkgFile != []:
                        #dlcs = gamePkgFile[0].Get('dlcs')
                        #dlcs += pkgFile
                        #gamePkgFile[0].Set('dlcs', dlcs)
                #elif titleType == 'update':
                    #gamePkgFile = self.SearchDB('titleID', titleID)
                    #gamePkgFile[0].Set('update', pkgFile)

                    
            ## test if the specified pkg directory is a directory and exists
            #if (self.directory != None) or (self.directory != ''):
                #if (exists(self.directory) == True) and (isdir(self.directory) == True):
                    #self.pkgs = []

                    #pkgFiles = FWTools.GetListFiles('.pkg', self.directory)
                    #for pkgFile in pkgFiles:
                        ### gather all information for pkg
                        #size = FWTools.GetFileSize(join(self.directory, pkgFile))

                        ### TODO : get the validity of the pkg : local, local and not a pkg, distant pkg (when nopaystation data will be integrated)
                        #validity = 'local'
                        ##validity = 'localError'
                        ##validity = 'distant'
                        ##validity = 'distantNoUrl'
                        
                        ### TODO : call to a sfo parser in pkg to get all needed info
                        #pkgFile = PkgFile(filename = pkgFile, fileSize = size, validity = validity, downloadURL = 'http://zeus.dl.playstation.net/cdn/EP0850/PCSB00779_00/EP0850-PCSB00779_00-AXIOMVERGE000000_bg_1_de788236d479ef1856369b4fc5870b918f2150f8.pkg')
                        #self.pkgs.append(pkgFile)
                #else:
                    #code = -1
                    #message = self.directory + ' is not a directory or does not exist'
            #else:
                #code = -1
                #message = 'Pkg directory is empty'
            
        return '', code, message

    def ImportNPS(self, *args):
        print 'ImportNPS'
        res = ''
        code = 0
        message = ''
        
        filename = args[0]
        appType = args[1]
        
        if (filename != None) and (filename != ''):
            if (exists(filename) == True) and (isfile(filename) == True):
                self.pauseRefreshImport = False
                self.stopRefreshImport = False
                self.refreshImportThread = Thread(target=self.RefreshImportThread, args=(lambda: self.pauseRefreshImport,lambda: self.stopRefreshImport, 0.25))
                self.refreshImportThread.start()
                thread = Thread(target=self.ImportThread, args=(filename,appType,))
                thread.start()
            else:
                code = -1
                message = filename + ' is not a file or does not exist'
        else:
            code = -1
            message = 'Filename is empty'
            
        return res, code, message

    def RefreshImportThread(self, pauseThread, stopThread, refreshRate):
        while True:
            if stopThread() == True:
                break

            if pauseThread() == False:
                API.Send('RefreshImportData', self.currentImportPercent)

                time.sleep(refreshRate)
                
    def ImportThread(self, filename, importType):
        if self.database != '':
            rootItem = self.database.getroot()

            self.currentImportPercent = 0
            
            with open(filename, 'r') as f:
                header = True

                importFileSize = getsize(filename)
                byteRead = 0
                for line in f:
                    ## compute the current percent imported
                    byteRead += len(line) + 1 # +1 to take into account the RC
                    self.currentImportPercent = int(byteRead * 100 / importFileSize)

                    ## do not read the header
                    if header == True:
                        header = False
                    else:
                        ## get file data
                        data = line.split('\t')

                        titleIdIndex = -1
                        regionIndex = -1
                        nameIndex = -1
                        urlIndex = -1
                        licenseIndex = -1
                        fwIndex = -1
                        sizeIndex = -1
                        contentIdIndex = -1
                        versionIndex = -1
                        if importType == 'game':
                            titleIdIndex = 0
                            regionIndex = 1
                            nameIndex = 2
                            urlIndex = 3
                            licenseIndex = 4
                            contentIdIndex = 5
                        elif importType == 'dlc':
                            titleIdIndex = 0
                            regionIndex = 1
                            nameIndex = 2
                            urlIndex = 3
                            licenseIndex = 4
                            contentIdIndex = 5
                        elif importType == 'update':
                            titleIdIndex = 0
                            regionIndex = 1
                            nameIndex = 2
                            versionIndex = 3
                            urlIndex = 4
                            fwIndex = 5
                            sizeIndex = 6
                        elif importType == 'psm':
                            titleIdIndex = 0
                            regionIndex = 1
                            nameIndex = 2
                            urlIndex = 3
                            licenseIndex = 4
                        elif importType == 'psx':
                            titleIdIndex = 0
                            regionIndex = 1
                            nameIndex = 2
                            urlIndex = 3
                            contentIdIndex = 4
                        elif importType == 'psp':
                            titleIdIndex = 0
                            regionIndex = 1
                            nameIndex = 3
                            urlIndex = 4
                            contentIdIndex = 5
                        elif importType == 'pspdlc':
                            titleIdIndex = 0
                            regionIndex = 1
                            nameIndex = 2
                            urlIndex = 3
                            contentIdIndex = 4
                        #elif importType == 'pkgi':
            
                        ## search if the pkg already exists
                        if contentIdIndex != -1:
                            pkgItem = self.SearchDB('contentId', data[contentIdIndex])
                            if pkgItem != []:
                                pkgItem = pkgItem[0]
                                #self.RemoveDB(pkgItem)
                            else:
                                pkgItem = etree.SubElement(rootItem, 'vitaPkg')

                            ## get content id
                            pkgItem.set("contentId", data[contentIdIndex])
                        else:
                            pkgItem = etree.SubElement(rootItem, 'vitaPkg')

                        ## get titleID
                        if titleIdIndex != -1:
                            pkgItem.set("titleId", data[titleIdIndex][0:9])

                        ## get titleType
                        pkgItem.set("type", importType)

                        ## get titleRegion
                        if regionIndex != -1:
                            pkgItem.set("titleRegion", data[regionIndex])

                        ## get titleName
                        if nameIndex != -1:
                            titleName = data[nameIndex]
                            try: ## unicode pb
                                ## remove/replace (TODO) special char from title name
                                titleName = titleName.translate(None, '®™ö®’ü')
                                #titleName = titleName.translate('o', 'ö')

                                #propItem.text = titleName
                                pkgItem.set("titleName", titleName)
                            except:
                                #propItem.text = titleName = ''
                                pkgItem.set("titleName", '')

                        ## get downloadURL and filename
                        if urlIndex != -1:
                            downloadURL = data[urlIndex]
                            if downloadURL == 'MISSING':
                                downloadURL = ''
                                
                            pkgItem.set("downloadURL", downloadURL)

                        pkgItem.set("filename", '')

                        ## get zRIF
                        if licenseIndex != -1:
                            pkgItem.set("zRIF", data[licenseIndex])

                        ## get required firmware
                        if fwIndex != -1:
                            pkgItem.set('titleFW', data[fwIndex])
                        
                        ## get version
                        if versionIndex != -1:
                            pkgItem.set('version', data[versionIndex])

                        ## get fileSize
                        fileSize = ''
                        if sizeIndex != -1:
                            fileSize = data[sizeIndex]
                        else:
                            pass
                            #if downloadURL != '':
                                #try:
                                    #openedUrl = urllib2.urlopen(downloadURL)
                                    #urlInfo = openedUrl.info()
                                    #fileSize = int(urlInfo["Content-Length"])
                                #except:
                                    #fileSize = ''
                        pkgItem.set("fileSize", fileSize)

            ## stop the refresh thread and send the last refresh import to the UI
            self.stopRefreshImport = True
            API.Send('RefreshImportData', self.currentImportPercent)
            #self.SaveDB()
            
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
                if child.text == None:
                    value = ''
                else:
                    value =child.text

                self.SetValues(child.tag, value)
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

#class DownloadThread(Thread):
    #def __init__(self, downloadCtrl):
        #Thread.__init__(self)
        #self.downloadCtrl = downloadCtrl

    #def run(self):
        #for dFile in self.downloadCtrl.downloadFiles:
            #url = dFile.Get('url')[0]
            ##print 'url', url 
            #try:
                ### open the distant url
                #openedUrl = urllib2.urlopen(url)
                #totalSize = dFile.Get('totalSize')[0]

                ### open the local file
                #filename = dFile.Get('filename')[0]
                #filenamePart = '.'.join((filename, 'part'))
                #fd = open(filenamePart, 'wb')
                
                ### download the file
                #blockSize = 8192 #100000 # urllib.urlretrieve uses 8192
                #count = 0
                #before = timeit.default_timer()
                #percent = 0
                #while True:
                    ### read a chunk of the distant file
                    #chunk = openedUrl.read(blockSize)
                    #if not chunk:
                        #break

                    #fd.write(chunk)

                    #if count % 10:
                        ### compute the percentage
                        #if totalSize > 0:
                            #percent = int(count * blockSize * 100 / totalSize)
                            #if percent > 100:
                                #percent = 100

                        #dFile.Set('percent', percent)
                        
                        ### compute the speed
                        #now = timeit.default_timer()
                        #deltaTime = now - before
                        #before = now

                        #if deltaTime > 0:
                            #speed = blockSize / deltaTime

                        #dFile.Set('speed', speed)

                        ##API.SetCtrl(apiCtrl)
                        ##API.Send('RefreshDownloadData')

                    #count += 1
                    
                    ### debug
                    ##res = 'filename ' + filename + ' ' + str(percent) + '% ' + str(FWTools.ConvertBytes(speed))
                    ##sys.stdout.write('\r' + res)

                    
                #fd.flush()
                #fd.close()

                #if percent == 100:
                    #os.rename(filenamePart, filename)
            #except Exception, e:
                #DPrint('error downloading {0}: {1}'.format(url, e), -1)
                
class DownloadCtrl():
    def __init__(self, nbDownloadQueues):
        #self.nbDownloadQueues = nbDownloadQueues
        #self.downloadQueues = []
        #for i in range(self.nbDownloadQueues):
            #dQueue = Queue()
            #self.downloadQueues.append(dQueue)

        self.directory = ''
        #self.processes = []
        self.threads = []
        self.stopThreads = False
        self.pauseThreads = False
        self.refreshUIThread = ''
        self.downloadFiles = []
        
        self.onGoingDownload = False
            
        API.Subscribe('SetDownloadDirectory', lambda args: self.SetDownloadDirectory(*args))
        API.Subscribe('SetDownloadData', lambda args: self.SetDownloadData(*args))
        API.Subscribe('StartDownload', lambda args: self.StartDownload(*args))
        API.Subscribe('PauseDownload', lambda args: self.PauseDownload(*args))
        API.Subscribe('ResumeDownload', lambda args: self.ResumeDownload(*args))
        API.Subscribe('StopDownload', lambda args: self.StopDownload(*args))
        API.Subscribe('CleanDownloadFiles', lambda args: self.CleanFiles(*args))
        API.Subscribe('GetDownloadData', lambda args: self.GetDownloadData(*args))
        API.Subscribe('OnGoingDownloads', lambda args: self.OnGoingDownloads(*args))
        #API.Subscribe('ClearDownloadData', lambda args: self.ClearDownloadData(*args))

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
        
    def OnGoingDownloads(self, *args):
        res = ''
        code = 0
        message = ''

        res = self.onGoingDownload
            
        return res, code, message
        
    def SetDownloadData(self, *args):
        res = ''
        code = 0
        message = ''
        
        urlData = args[0]
        #print 'urlData', urlData

        self.downloadFiles = []
        for url, destination in urlData:
            filename = join(self.directory, destination)
            #filenamePart = '.'.join((filename, 'part'))

            openedUrl = urllib2.urlopen(url)
            urlInfo = openedUrl.info()
            totalSize = int(urlInfo["Content-Length"])
                
            dFile = DownloadFile(url=url, filename=filename, basename=destination, totalSize=totalSize)

            self.downloadFiles.append(dFile)

        thread = Thread(target=self.DownloadThread, args=(lambda: self.pauseThreads,lambda: self.stopThreads))
        self.threads.append(thread)
        
        return res, code, message

    def StartDownload(self, *args):
        #print 'StartDownload', args
        res = ''
        code = 0
        message = ''

        if self.directory != '':
            if self.onGoingDownload == False:
                self.onGoingDownload = True
                for thread in self.threads:
                    #thread.daemon = True
                    self.stopThreads = False
                    self.pauseThreads = False
                    thread.start()

                self.refreshUIThread = Thread(target=self.RefreshThread, args=(lambda: self.pauseThreads,lambda: self.stopThreads))
                self.refreshUIThread.start()
            else:
                code = -1
                message = 'Files are already being downloaded'
        else:
            code = -1
            message = 'The download directory is empty'
            
        return res, code, message

    def PauseDownload(self, *args):
        res = ''
        code = 0
        message = ''
        
        if self.onGoingDownload == True:
            self.pauseThreads = True
        
        return res, code, message
        
    def ResumeDownload(self, *args):
        res = ''
        code = 0
        message = ''
        
        if self.onGoingDownload == True:
            self.pauseThreads = False
        
        return res, code, message

    def StopDownload(self, *args):
        res = ''
        code = 0
        message = ''

        #API.Send('DownloadStop')
        
        if self.onGoingDownload == True:
            self.stopThreads = True
            for thread in self.threads:
                thread.join()

            self.refreshUIThread.join()
                
        ## reinit the thread list
        self.threads = []
        self.onGoingDownload = False
        
        return res, code, message

    def DownloadThread(self, pauseThread, stopThread, speedUpdate = 10):
        terminate = False
        for dFile in self.downloadFiles:
            url = dFile.Get('url')[0]
            #print 'url', url 
            try:
                ## open the distant url
                openedUrl = urllib2.urlopen(url)
                totalSize = dFile.Get('totalSize')[0]

                ## open the local file
                filename = dFile.Get('filename')[0]
                filenamePart = '.'.join((filename, 'part'))
                fd = open(filenamePart, 'wb')
                
                ## download the file
                blockSize = 8192 #100000 # urllib.urlretrieve uses 8192
                count = 0
                before = timeit.default_timer()
                percent = 0
                update = speedUpdate
                while True:
                    if stopThread() == True:
                        #print 'stop'
                        terminate = True
                        break

                    if pauseThread() == False:
                        ## read a chunk of the distant file
                        chunk = openedUrl.read(blockSize)
                        count += 1
                        if not chunk:
                            break

                        fd.write(chunk)

                        ## compute the percentage
                        if totalSize > 0:
                            percent = int(count * blockSize * 100 / totalSize)
                            if percent > 100:
                                percent = 100

                        dFile.Set('percent', percent)

                        ## compute the speed
                        ## in order to compute the speed more presizely 
                        update -= 1
                        if update == 0:
                            update = speedUpdate
                            
                            now = timeit.default_timer()
                            print 
                            deltaTime = now - before
                            before = now

                            if deltaTime > 0:
                                speed = blockSize / deltaTime

                            dFile.Set('speed', speed)
                        
                        ## debug
                        #res = 'filename ' + filename + ' ' + str(percent) + ' % ' + str(FWTools.ConvertBytes(speed))
                        #sys.stdout.write('\r' + res)

                fd.flush()
                fd.close()
                
                if percent == 100:
                    try:
                        if (exists(filename) == True) and (isfile(filename) == True):
                            os.remove(filename)

                        os.rename(filenamePart, filename)
                    except Exception, e:
                        DPrint('error renaming {0} in {1}: {2}'.format(filenamePart, filename, e), -1)
                
                    API.Send('DownloadDone')

                if stopEvent.is_set() == True:
                    break
            except Exception, e:
                DPrint('error downloading {0}: {1}'.format(url, e), -1)
                
    def RefreshThread(self, pauseThread, stopThread):
        while True:
            if stopThread() == True:
                break

            if pauseThread() == False:
                API.Send('RefreshDownloadData')

                time.sleep(1)

    def CleanFiles(self, *args):
        res = ''
        code = 0
        message = ''
        
        partFiles = FWTools.GetListFiles('.part', self.directory)

        for partFile in partFiles:
            filename = join(self.directory, partFile)
            os.remove(filename)

        return res, code, message
        
    def GetDownloadData(self, *args):
        downloadData = []
        code = 0
        message = ''

        for dFile in self.downloadFiles:
            res, code, message = dFile.Serialize()
            downloadData.append(res)

        return downloadData, code, message
        
    #def ClearDownloadData(self, *args):
        #res = ''
        #code = 0
        #message = ''

        ### todo garbage collect the previous dfile instance?
        #self.downloadFiles = []

        #return res, code, message

    def Stop(self):
        self.StopDownload('')
