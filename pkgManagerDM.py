#!/usr/bin/env python2

class FWObject(object):
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
            res[varName] = value
            
        return res, 0, ''

class PkgFile(FWObject):
    ## type = game, update or DLC
    ## color :  0x00BBGGRR
    instanceVariables = [\
        {'name': 'titleID', 'display': 'Title ID','default': ''}, \
        {'name': 'titleType', 'display': 'Type','default': ''}, \
        {'name': 'titleName', 'display': 'Name','default': ''}, \
        {'name': 'titleRegion', 'display': 'Region','default': ''}, \
        {'name': 'filename', 'display': 'Filename', 'default': ''}, \
        {'name': 'titleFW', 'display': 'FW Version','default': ''}, \
        {'name': 'fileSize', 'display': 'Size','default': 0}, \
        {'name': 'downloadURL', 'display': 'URL','default': ''}, \
        {'name': 'zRIF', 'display': 'zRIF','default': ''}, \
        {'name': 'validity', 'default': ''}, \
        ]
        
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

class VitaFile(FWObject):
    # type = game, update or DLC
    instanceVariables = [\
        {'name': 'titleID', 'display': 'Title ID', 'default': ''}, \
        {'name': 'titleType', 'display': 'Type', 'default': ''}, \
        {'name': 'titleName', 'display': 'Name', 'default': ''}, \
        {'name': 'titleRegion', 'display': 'Region', 'default': ''}, \
        {'name': 'directorySize', 'display': 'Size', 'default': 0}, \
        {'name': 'directory', 'display': 'Directory', 'default': ''}, \
        ]
        
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        
