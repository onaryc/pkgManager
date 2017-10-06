#!/usr/bin/env python2

try:
    import os
    from os import listdir
    from os.path import isfile, join, splitext
except ImportError:
    assert False, "import error in pkgManagerTools"
    
def listPkgFiles(baseDirectory = '.'):
    pkgFiles = []
    
    ## get all files, dir from baseDirectory
    listFiles = os.listdir(baseDirectory)
    for filename in listFiles:
        if isfile(join(baseDirectory, filename)):
            ## check the extension
            basename, extension = os.path.splitext(filename)
            
            if extension == '.pkg':
                pkgFiles.append(filename)

    return pkgFiles
