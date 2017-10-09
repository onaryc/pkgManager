#!/usr/bin/env python2

class PkgFile():
    instanceVariables = [\
        {'name': 'filename', 'default':''}, \
        {'name': 'titleID', 'default':''}, \
        {'name': 'titleName', 'default':''}, \
        {'name': 'titleRegion', 'default':''}, \
        ]
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

    def serialize(self):
        return [self.titleID, self.titleType, self.titleName, self.titleRegion, self.filename, self.titleFW, self.fileSize, self.downloadURL, self.zRIF]

class VitaFile():
    def __init__(self):
        self.titleID = ''
        self.titleName = ''
        self.titleRegion = ''
        self.titleType = ''
        self.fileSize = 0
        self.directory = ''

        
