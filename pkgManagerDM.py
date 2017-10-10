#!/usr/bin/env python2

class ObjectFile():
    #def GetClassVars(self):
        #className = type(self).__name__
        
        #return GetClassVars(className)

    #def GetClassVars(className):
        #return vars(className)

    @classmethod
    def GetClassVars(cls):
        return vars(cls)

    #def Serialize(self):
        #return vars(self)

class PkgFile(ObjectFile):
    #instanceVariables = [\
        #{'name': 'filename', 'default':''}, \
        #{'name': 'titleID', 'default':''}, \
        #{'name': 'titleName', 'default':''}, \
        #{'name': 'titleRegion', 'default':''}, \
        #{'name': 'titleType', 'default':''}, \
        #{'name': 'titleFW', 'default':''}, \
        #{'name': 'fileSize', 'default':0}, \
        #{'name': 'downloadURL', 'default':''}, \
        #{'name': 'zRIF', 'default':''}, \
        #]
    filename = ''
    titleID = ''
    def __init__(self, filename='', titleID='', titleName='', titleRegion='', titleType='', titleFW='', downloadURL='', zRIF=''):
        self.filename = filename
        self.titleID = titleID
        self.titleName = titleName
        self.titleRegion = titleRegion # EU, USA or Japan/Jpn
        self.titleType = titleType # game, update or DLC
        self.titleFW = titleFW
        self.fileSize = 0
        self.downloadURL = downloadURL
        self.zRIF = zRIF

    def Serialize(self):
        return [self.titleID, self.titleType, self.titleName, self.titleRegion, self.filename, self.titleFW, self.fileSize, self.downloadURL, self.zRIF]

    #def Serialize(self):
        #return vars(self)

class VitaFile(ObjectFile):
    def __init__(self):
        self.titleID = ''
        self.titleName = ''
        self.titleRegion = ''
        self.titleType = ''
        self.fileSize = 0
        self.directory = ''

        
