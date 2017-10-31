#!/usr/bin/env python2
try:
    import FWTools
except ImportError, e:
    assert False, 'import error in pkgManagerDM : {0}'.format(e)
    
class FWObject(object):
    #instanceVariables = []
    
    def __init__(self, **kwargs):
        cls = self.__class__
        varsData = cls.GetClassVarsData()
        for varData in varsData:
            varName = varData['name']
            if varName in kwargs:
                self.Set(varName, kwargs[varName])
                #setattr(self, varName, kwargs[varName])
            else:
                varDefaultValue = varData['default']
                self.Set(varName, varDefaultValue)
                #setattr(self, varName, varDefaultValue)

    @classmethod
    def GetClassVarsData(cls):
        res = cls.instanceVariables

        return res

    @classmethod
    def GetClassVars(cls):
        res = []

        varsData = cls.GetClassVarsData()
        for varData in varsData:
            varName = varData['name']
            res.append(varName)

        return res

    def Get(self, varName):
        res = ''
        code = 0
        message = ''
        
        if varName in vars(self):
            res = getattr(self, varName)
        else:
            code = -1
            message = 'variable (' + varName + ') is not an instance variable of object ' + self
            
        return res, code, message

    def Set(self, varName, value):
        setattr(self, varName, value)

        return '', 0, ''

    #def Serialize(self):
        #res = []

        #cls = self.__class__
        #varsData = cls.GetClassVarsData()
        #for varData in varsData:
            #varName = varData['name']
            #value, code, message = self.Get(varName)
            #res.append(value)
            
        #return res, 0, ''
    def Serialize(self):
        res = {}

        cls = self.__class__
        varsData = cls.GetClassVarsData()
        for varData in varsData:
            varName = varData['name']
            value, code, message = self.Get(varName)

            if ('conversion' in varData) and (str(value) != ''):
                value = eval(varData['conversion'] +'('+str(value)+')')

            res[varName] = value
            
        return res, 0, ''

class PkgFile(FWObject):
    instanceVariables = [ \
        {'name': 'titleID', 'display': 'Title ID', 'default': ''}, \
        {'name': 'titleType', 'display': 'Type', 'default': ''}, \
        {'name': 'titleName', 'display': 'Name', 'default': ''}, \
        {'name': 'titleRegion', 'display': 'Region', 'default': ''}, \
        {'name': 'filename', 'display': 'Filename', 'default': ''}, \
        {'name': 'titleFW', 'display': 'FW Version', 'default': ''}, \
        {'name': 'fileSize', 'display': 'Size', 'default': 0, 'conversion': 'FWTools.ConvertBytes'}, \
        {'name': 'downloadURL', 'display': 'URL', 'default': ''}, \
        {'name': 'validity', 'default': ''}, \
        ]
        
    #def __init__(self, **kwargs):
        #super(self.__class__, self).__init__(**kwargs)
        
class GamePkgFile(PkgFile):
    instanceVariables = PkgFile.instanceVariables + [\
        {'name': 'zRIF', 'display': 'zRIF', 'position':8, 'default': ''}, \
        {'name': 'contentID', 'display': 'Content ID', 'position':9, 'default': ''}, \
        {'name': 'dlcs', 'default': []}, \
        {'name': 'update', 'default': ''}, \
        ]
        
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.Set('titleType', 'game')
        
class DLCPkgFile(PkgFile):
    instanceVariables = PkgFile.instanceVariables + [\
        {'name': 'zRIF', 'display': 'zRIF', 'position':8, 'default': ''}, \
        {'name': 'contentID', 'display': 'Content ID', 'position':9, 'default': ''}, \
        ]
        
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.Set('titleType', 'dlc')
        
class UpdatePkgFile(PkgFile):
    instanceVariables = PkgFile.instanceVariables + [\
        {'name': 'version', 'display': 'Version', 'default': ''}, \
        ]
        
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.Set('titleType', 'update')
        
class PSMPkgFile(PkgFile):
    instanceVariables = PkgFile.instanceVariables + [\
        {'name': 'zRIF', 'display': 'zRIF', 'position':8, 'default': ''}, \
        ]
        
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.Set('titleType', 'psm')
        
class VitaFile(FWObject):
    # type = game, update or DLC
    instanceVariables = [\
        {'name': 'titleID', 'display': 'Title ID', 'default': ''}, \
        {'name': 'titleType', 'display': 'Type', 'default': ''}, \
        {'name': 'titleName', 'display': 'Name', 'default': ''}, \
        {'name': 'titleRegion', 'display': 'Region', 'default': ''}, \
        {'name': 'directorySize', 'display': 'Size', 'default': 0, 'conversion': 'FWTools.ConvertBytes'}, \
        {'name': 'directory', 'display': 'Directory', 'default': ''}, \
        ]
        
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        
class DownloadFile(FWObject):
    # type = game, update or DLC
    instanceVariables = [\
        {'name': 'url', 'default': ''}, \
        {'name': 'filename', 'default': ''}, \
        {'name': 'basename', 'display': 'File Name', 'default': ''}, \
        {'name': 'totalSize', 'display': 'Total Size', 'default': 0, 'conversion': 'FWTools.ConvertBytes'}, \
        {'name': 'percent', 'display': 'Percent', 'default': 0}, \
        {'name': 'speed', 'display': 'Speed', 'default': 0, 'conversion': 'FWTools.ConvertBytes'} \
        ]
        
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        
