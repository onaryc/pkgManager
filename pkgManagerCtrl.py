#!/usr/bin/env python2


try:
    from os.path import exists, isdir, isfile

    from lxml import etree
    
    import pkgManagerTools
    from pkgManagerDM import PkgFile, VitaFile
except ImportError:
    assert False, "import error in pkgManagerCtrl"
    
class PkgCtrl():
    def __init__(self, directory, downloadFile):
        self.directory = directory
        self.downloadFile = downloadFile

    #def SetDirectory(self,directory):
        #self.directory = directory

    def GetDirectory(self):
        return self.directory
        
    def GetDownloadFile(self):
        return self.downloadFile

    def GetLocalPkgsData(self):
        pkgs = []
        code = 0
        message = ''
        
        ## test if the specified pkg directory is a directory and exists
        if (exists(self.directory) == True) and (isdir(self.directory) == True):
            pkgFiles = pkgManagerTools.listPkgFiles(self.directory)

            for pkgFile in pkgFiles:
                pkgFile = PkgFile(filename = pkgFile)
                pkgs.append(pkgFile.serialize())

        else:
            code = -1
            message = self.directory + ' is not a directory or does not exist'
            
        return pkgs, code, message

class VitaCtrl():
    def __init__(self, directory):
        self.directory = directory

    #def SetDirectory(self,directory):
        #self.directory = directory

    def GetDirectory(self):
        return self.directory

    def GetLocalVitaData(self):
        vitaApps = []
        message = ''
        
        if (exists(self.directory) == True) and (isdir(self.directory) == True):
            ## list all app/dlc/update
            vitaApps = []
        else:
            message = self.directory + ' is not a directory or does not exist'

        return vitaApps, message

class IniCtrl():
    def __init__(self, inifile):
        self.inifile = inifile
        self.values = {}

    def ResetValues(self):
        self.values = {}

    def SetValues(self, key, value):
        self.values[key] = value

    def GetValue(self, key):
        return self.values[key]

    def ParseIni(self):
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

        return code, message
        
    def SerializeIni(self):
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

        return code, message
        

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
        
