#!/usr/bin/env python2

try:
    #import win32com.client as com
    
    import os
    from os import listdir
    from os.path import isfile, isdir, join, splitext, getsize, exists

    #~ import wget
    from threading import Thread
    from Queue import Queue
except ImportError, e:
    assert False, 'import error in FWTools : {0}'.format(e)
    
def GetListFiles(ext, baseDirectory = '.'):
    resFiles = []
    
    ## get all files, dir from baseDirectory
    listFiles = os.listdir(baseDirectory)
    for filename in listFiles:
        if isfile(join(baseDirectory, filename)):
            ## check the extension
            basename, extension = splitext(filename)
            
            if extension == ext:
                resFiles.append(filename)

    return resFiles

def GetFileSize(filename):
    res = 0
    
    if (filename != None) or (filename != ''):
        if (exists(filename) == True) and (isfile(filename) == True):
            res = getsize(filename)
            res = ConvertBytes(res)
            
    return res

def GetDirSize(directory):
    res = 0
    
    if (directory != None) or (directory != ''):
        if (exists(directory) == True) and (isdir(directory) == True):
            for root, dirs, files in os.walk(directory):
                for file in files:
                    #try:
                        res = res + getsize(join(root, file))
                    #except:
                        #print("error with file:  " + join(root, file))
                        
    return res
    
#def GetDirSizeWin(directory):
    #res = 0
    
    #if (directory != None) or (directory != ''):
        #if (exists(directory) == True) and (isdir(directory) == True):
            #fso = com.Dispatch("Scripting.FileSystemObject")
            #folder = fso.GetFolder(directory)
            #res = ConvertBytes(folder.Size)

    #return res

def ConvertBytes(number):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if number < 1024.0:
            return "%3.1f %s" % (number, x)
        number /= 1024.0

    return number

class Downloader(Thread):
    def __init__(self, urls):
        Thread.__init__(self)
        self.queue = Queue()

        queue.put((url, filename))

    def run(self):
        while True:
            download_url, save_as = queue.get()
            # sentinal
            if not download_url:
                return
            try:
                urllib.urlretrieve(download_url, filename=save_as)
            except Exception, e:
                logging.warn("error downloading %s: %s" % (download_url, e))
