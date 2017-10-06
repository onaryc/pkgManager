#!/usr/bin/env python2

class PkgFile():
    def __init__(self, filename='', titleID='', titleName='', titleRegion='', titleType='', downloadURL='', zRIF=''):
        self.filename = filename
        self.titleID = titleID
        self.titleName = titleName
        self.titleRegion = titleRegion
        self.titleType = titleType
        self.downloadURL = downloadURL
        self.zRIF = zRIF

    def serialize(self):
        return [self.titleID, self.titleType, self.titleName, self.titleRegion, self.filename, self.downloadURL, self.zRIF]

class VitaFile():
    def __init__(self):
        self.titleID = ''
        self.titleName = ''
        self.titleRegion = ''
        self.titleType = ''
        self.directory = ''

        
