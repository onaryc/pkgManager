#!/usr/bin/env python2

try:
    from os.path import exists, isdir, isfile

    from lxml import etree
    
    import APICtrl as API
    import pkgManagerTools
    from pkgManagerDM import PkgFile, VitaFile
except ImportError:
    assert False, "import error in pkgManagerCtrl"

class Controllers():
    def __init__(self, iniFile):
        iniCtrl = IniCtrl(iniFile)

        messageCtrl = MessageCtrl(ui = 'stdout') ## message displaid on the stdout

        res, code, message = iniCtrl.ParseIni()
        #~ messageCtrl.ManageMessage(code, message)
        
        #~ API.Send('ParseIni')

        pkgDirectory, code, message = iniCtrl.GetValue('pkgDirectory')
        pkgDownloadFile, code, message = iniCtrl.GetValue('pkgDownloadFile')
        vitaDirectory, code, message = iniCtrl.GetValue('vitaDirectory')

        pkgCtrl = PkgCtrl(pkgDirectory, pkgDownloadFile, self)
        vitaCtrl = VitaCtrl(vitaDirectory)
        
class PkgCtrl():
    def __init__(self, directory, downloadFile, controllers):
        self.directory = directory
        self.downloadFile = downloadFile

        API.Subscribe('GetLocalPkgsData', lambda args: self.GetLocalPkgsData(*args))
        API.Subscribe('GetPkgDirectory', lambda args: self.GetDirectory(*args))
        API.Subscribe('GetDownloadFile', lambda args: self.GetDownloadFile(*args))

    def GetDirectory(self, *args):
        return self.directory, 0, ''
        
    def GetDownloadFile(self, *args):
        return self.downloadFile, 0, ''

    def GetLocalPkgsData(self, *args):
        pkgs = []
        code = 0
        message = ''
        
        ## test if the specified pkg directory is a directory and exists
        if (self.directory != None) or (self.directory != ''):
            if (exists(self.directory) == True) and (isdir(self.directory) == True):
                pkgFiles = pkgManagerTools.listPkgFiles(self.directory)

                for pkgFile in pkgFiles:
                    pkgFile = PkgFile(filename = pkgFile)
                    pkgs.append(pkgFile.serialize())

            else:
                code = -1
                message = self.directory + ' is not a directory or does not exist'
        else:
            code = -1
            message = 'Pkg directory is empty'
            
        return pkgs, code, message
        #~ return pkgs, 'list', code, message

class VitaCtrl():
    def __init__(self, directory):
        self.directory = directory

        API.Subscribe('GetVitaDirectory', lambda args: self.GetDirectory(args))
        API.Subscribe('GetLocalVitaData', lambda args: self.GetLocalVitaData(args))
        
    #def SetDirectory(self,directory):
        #self.directory = directory

    def GetDirectory(self, *args):
        return self.directory, 0, ''

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
                print 'key', key, 'value', value

            fd = open(self.inifile, 'w')
            
            fd.write(etree.tostring(root, pretty_print=True))
            
            fd.close()

            code = 0
            message = 'Ini Serialized successfully'
        else:
            code = -1
            message = 'Ini file does not exists or is not a file'

        return '', code, message
        

class MessageCtrl():
    def __init__(self, logFile = '', ui = ''):
        self.logFile = logFile
        self.ui = ui

    def SetUI(self, ui):
        self.ui = ui
        
    def ManageMessage(self, code, message):
        if message != '':
            if self.ui != '':
                if self.ui == 'stdout':
                    print 'code', code, 'message', message
                else:
                    self.ui.Print(code, message)
