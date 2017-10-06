#!/usr/bin/env python2
try:
    import pkgManagerTools
    from pkgManagerDM import PkgFile, VitaFile
except ImportError:
    assert False, "import error in pkgManagerCtrl"
    
class PkgCtrl():
    def __init__(self, pkgDirectory):
        self.pkgDirectory = pkgDirectory

    def SetDirectory(self,pkgDirectory):
        self.pkgDirectory = pkgDirectory

    def GetLocalPkgsData(self):
        pkgFiles = pkgManagerTools.listPkgFiles(self.pkgDirectory)

        pkgs = []
        for pkgFile in pkgFiles:
            pkgFile = PkgFile(filename = pkgFile)
            pkgs.append(pkgFile.serialize())

        return pkgs
    
        
