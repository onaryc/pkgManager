#!/usr/bin/env python2
# -*- coding: utf-8 -*-*

try:
    ## python module
    import os
    #from multiprocessing import Process
    from threading import Thread
    import time

    ## wx python module
    import wx
    from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin, CheckListCtrlMixin
    import wx.lib.newevent
    
    import APICtrl as API
    from MessageTools import DPrint
except ImportError, e:
    assert False, 'import error in pkgManagerUI : {0}'.format(e)

ID_MENU_SETTINGS = wx.NewId()
ID_MENU_RENAME_ALL = wx.NewId()
ID_MENU_DOWNLOAD_ALL = wx.NewId()

ID_BUTTON_SAVE_INI = wx.NewId()
ID_BUTTON_RESET_INI = wx.NewId()
ID_BUTTON_REFRESH_PKG = wx.NewId()

#SendMessage, EVT_SEND_MESSAGE = wx.lib.newevent.NewEvent()

class UpdateUI(Thread):
    def __init__(self, ui):
        Thread.__init__(self)
        self.ui = ui

    def run(self):
        while True:
            self.ui.Refresh()
            
            ## update only each second
            time.sleep(1)
                
class UI(wx.Frame):
    def __init__(self, title = 'Pkg Manager', size=(800,400)):
        self.app = wx.App(False)
        
        wx.Frame.__init__(self, None, title=title, size=size)
        
        self.locale = wx.Locale(wx.LANGUAGE_ENGLISH)
         
        self.statusBar = self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu
        ## file menu
        self.ID_FILE_IMPORT_GAMES = wx.NewId()
        self.ID_FILE_IMPORT_DLCS = wx.NewId()
        self.ID_FILE_IMPORT_UPDATES = wx.NewId()
        
        fileMenu = wx.Menu()
        fileMenu.Append(self.ID_FILE_IMPORT_GAMES,"Import Games"," Import Games")
        fileMenu.Append(self.ID_FILE_IMPORT_DLCS,"Import DLCs"," Import DLC")
        fileMenu.Append(self.ID_FILE_IMPORT_UPDATES,"Import Updates"," Import Updates")
        fileMenu.AppendSeparator()
        menuExit = fileMenu.Append(wx.ID_EXIT,"E&xit"," Close Pkg Manager")

        ## edit menu
        #editMenu = wx.Menu()
        #menuConfiguration = editMenu.Append(ID_MENU_SETTINGS,"Settings"," Settings")

        ## tools menu
        #toolsMenu = wx.Menu()
        #menuToolsRename = toolsMenu.Append(ID_MENU_RENAME_ALL,"Rename All"," rename all pkg")
        #menuToolsDownload = toolsMenu.Append(ID_MENU_DOWNLOAD_ALL,"Download All"," download all pkg")

        # other menu
        otherMenu = wx.Menu()
        menuAbout = otherMenu.Append(wx.ID_ABOUT, "&About"," Information about Pkg Manager")
        
        # Creating the menubar.
        menuBar = wx.MenuBar()

        ## adding menu to the menu bar
        menuBar.Append(fileMenu,"&File")
        #menuBar.Append(toolsMenu,"&Tools")
        #menuBar.Append(editMenu,"&Edit")
        menuBar.Append(otherMenu,"&?")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnImport)
        self.Bind(wx.EVT_MENU, self.OnImport)
        self.Bind(wx.EVT_MENU, self.OnImport)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        self.Bind(wx.EVT_CLOSE, self.OnExit)


        self.notebook = wx.Notebook(self)

        self.panelPkg = PkgFilesView(self.notebook)
        self.panelVita = VitaFilesView(self.notebook)
        self.panelSettings = SettingsView(self.notebook)

        self.notebook.AddPage(self.panelPkg, "Pkg Files")
        self.notebook.AddPage(self.panelVita, "Vita Files")
        self.notebook.AddPage(self.panelSettings, "Settings")
        
        API.Subscribe('SendUIMessage', lambda args: self.SendUIMessage(*args))

        self.updateUI = UpdateUI(self)
        
        self.Show(True)

        ## a disgraceful black background color is displayed on panel toolbar, it disapears when panel are selected
        self.notebook.ChangeSelection(1)
        self.notebook.ChangeSelection(0)

    def Start(self):
        self.panelPkg.FillValues()
        self.panelVita.FillValues()
        self.panelSettings.FillValues()

        #self.updateUI.start()
            
        self.app.MainLoop()
        
    def Stop(self):
        API.Stop()
        self.Destroy()

    def OnAbout(self, event):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Pkg Manager 0.1", "About Pkg Manager", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnExit(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Stop()

    def OnImport(self, event):
        itemId = event.GetId()
        importType = ''
        if itemId == self.ID_FILE_IMPORT_GAMES:
            importType = 'game'
        elif itemId == self.ID_FILE_IMPORT_DLCS:
            importType = 'dlc'
        elif itemId == self.ID_FILE_IMPORT_UPDATES:
            importType = 'update'

        if importType != '':
            openDlg = wx.FileDialog(self, "Select NPS file", "", "", "NPS file (*.tsv)|*.tsv", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

            openDlg.ShowModal()
            filename = openDlg.GetPath()
            openDlg.Destroy()
        
            API.Send('ImportNPS', filename, importType)
            
    def Refresh(self):
        self.panelPkg.Refresh()
        
    def SendUIMessage(self, *args):
        message = args[0]
        code = args[1]
        
        self.statusBar.SetStatusText(message, 0) 

class UIListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, CheckListCtrlMixin):
    def __init__(self, parent, className, proportion=1, checkBox = True):
        #wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT)

        ListCtrlAutoWidthMixin.__init__(self)
        if checkBox == True:
            CheckListCtrlMixin.__init__(self)

        self.mapAttributesCol = {}
        self.mapColAttributes = {}

        ## add the column based on the data model attributes
        attributes = API.Send('GetModelAttributes', className)
        for attribute in attributes:
            if 'display' in attribute:
                displayName = attribute['display']

                colIndex = self.AppendColumn(displayName)                
                self.mapAttributesCol[attribute['name']] = colIndex
                self.mapColAttributes[colIndex] = attribute['name']

        self.sizerFlags = wx.SizerFlags(proportion)
        self.sizerFlags.Expand()

        if checkBox == True:
            self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnShowPopup)

        self.ID_CONTEXTUAL_CHECKED = wx.NewId()
        self.ID_CONTEXTUAL_CHECK_ALL = wx.NewId()
        self.ID_CONTEXTUAL_UNCHECKED = wx.NewId()
        self.ID_CONTEXTUAL_UNCHECK_ALL = wx.NewId()
        
        
    def RemoveValues(self):
        self.DeleteAllItems()
        
    def AddEntry(self, entry):
        ## get the text in col order
        tmp = []
        for i in range(self.GetColumnCount()):
            name = self.mapColAttributes[i]
            
            tmp.append(entry[name])

        if tmp != []:
            #print 'tmp', tmp 
            rowIndex = self.Append(tmp)
                
            if 'validity' in entry:
                validity = entry['validity']

                if validity == 'local':
                    color = wx.Colour('green')
                elif validity == 'localError':
                    color = wx.Colour('red')
                elif validity == 'distantNoUrl':
                    color = wx.Colour('orange')
                elif validity == 'distant':
                    color = wx.Colour('yellow')
                else:
                    color = wx.Colour('white')
        
                ## alternate color
                if rowIndex % 2:
                    color.MakeDisabled(200)
                else:
                    color.MakeDisabled(255)
                    
                self.SetItemBackgroundColour(rowIndex, color)


    def __getSelectedEntries(self, entry, entries = []):
        res = entries

        
    def GetSelectedEntries(self):
        res = []

        # start at -1 to get the first selected item
        currentId = -1
        while True:
            nextId = self.GetNextSelected(currentId)
            if nextId == -1:
                break

            res.append(nextId)
            currentId = nextId

        return res
        
    def GetCheckEntries(self):
        res = []

        num = self.GetItemCount()
        for i in range(num):
            if self.IsChecked(i):
                #self.log.AppendText(self.list.GetItemText(i) + '\n')
                res.append(i)

        return res

    def GetEntryText(self, entry, colId):
        if colId in self.mapAttributesCol:
            col = self.mapAttributesCol[colId]
        else:
            col = 0
            
        return self.GetItemText(entry,col)
        
    def GetSizerFlags(self):
        return self.sizerFlags

    def OnShowPopup(self, event):
        self.popupmenu = wx.Menu()
        #for text in "Add Delete Edit".split():
        item = self.popupmenu.Append(self.ID_CONTEXTUAL_CHECKED, 'Checked')
        self.Bind(wx.EVT_MENU, self.OnSelectPop, item)
        
        item = self.popupmenu.Append(self.ID_CONTEXTUAL_CHECK_ALL, 'Check All')
        self.Bind(wx.EVT_MENU, self.OnSelectPop, item)

        item = self.popupmenu.Append(self.ID_CONTEXTUAL_UNCHECKED, 'Unchecked')
        self.Bind(wx.EVT_MENU, self.OnSelectPop, item)
        
        item = self.popupmenu.Append(self.ID_CONTEXTUAL_UNCHECK_ALL, 'Uncheck All')
        self.Bind(wx.EVT_MENU, self.OnSelectPop, item)

        self.PopupMenu(self.popupmenu, event.GetPoint())
        self.popupmenu.Destroy()

    def OnSelectPop(self, event):
        checked = True
        itemId = event.GetId()
        if itemId == self.ID_CONTEXTUAL_CHECKED: # checked the selection
            checked = True
            selectedEntries = self.GetSelectedEntries()
        elif itemId == self.ID_CONTEXTUAL_UNCHECKED: # uncheck the selection
            checked = False
            selectedEntries = self.GetSelectedEntries()
        elif itemId == self.ID_CONTEXTUAL_CHECK_ALL: # uncheck the selection
            checked = True
            selectedEntries = range(self.GetItemCount())
        elif itemId == self.ID_CONTEXTUAL_UNCHECK_ALL: # uncheck the selection
            checked = False
            selectedEntries = range(self.GetItemCount())
        else:
            return
        #item = self.popupmenu.FindItemById(itemId)
        #text = item.GetText()
        
        #selectedEntries = self.GetSelectedEntries()
        for selectedEntry in selectedEntries:
            self.CheckItem(selectedEntry, checked)

class UIToolbarButton(wx.BitmapButton):
    def __init__(self, parent, command, image, tooltip, idB = -1):
        self.buttonImage = wx.Image(name = image)
        self.buttonBitmap =  self.buttonImage.ConvertToBitmap()
        
        wx.BitmapButton.__init__(self, parent, bitmap = self.buttonBitmap, id=idB)

        self.Bind(wx.EVT_BUTTON, command)
        self.SetToolTip(tooltip)
        
class UIToolBar(wx.BoxSizer):
    def __init__(self, parent, description):
        wx.BoxSizer.__init__(self, orient = wx.HORIZONTAL)

        self.buttonById = {}
        buttonFlags = wx.SizerFlags(0)
        for buttonData in description:
            command = buttonData['command']
            image = buttonData['image']
            tooltip = buttonData['tooltip']
            if 'id' in buttonData:
                idB = buttonData['id']
            else:
                idB = -1
                
            tbButton = UIToolbarButton(parent, command, image, tooltip, idB)

            if idB != -1:
                self.buttonById[idB] = tbButton 

            if 'state' in buttonData:
                state = buttonData['state']
                if state == 'disabled':
                    tbButton.Disable()
                
            self.Add(tbButton, buttonFlags)
            
        self.sizerFlags = wx.SizerFlags(0)
        
    def GetSizerFlags(self):
        return self.sizerFlags

    def GetButtonByID (self, idB):
        res = ''
        
        if idB in self.buttonById:
            res = self.buttonById[idB]

        return res

#def DummyProc():
    #while True:
        #print 'dummy'
        #time.sleep(1)
    
class PkgFilesView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        API.Subscribe('RefreshDownloadData', lambda args: self.RefreshDownloadData(*args))
        API.Subscribe('DownloadDone', lambda args: self.DownloadDone(*args))

        ## create the toolbar toolbar
        self.ID_START_BUTTON = wx.NewId()
        self.ID_STOP_BUTTON = wx.NewId()
            
        description = [ \
            {'command': self.FillValues, 'image': 'resources/view-refresh.png', 'tooltip': 'Refresh local Pkgs information'}, \
            {'command': self.ClearPkgData, 'image': 'resources/edit-clear.png', 'tooltip': 'Clear local Pkgs information'}, \
            {'command': self.Rename, 'image': 'resources/edit-copy.png', 'tooltip': 'Rename selected Pkg files', 'state': 'disabled'}, \
            {'command': self.StartDownload, 'image': 'resources/go-bottom.png', 'tooltip': 'Download selected Pkg files', 'id':self.ID_START_BUTTON}, \
            {'command': self.StopDownload, 'image': 'resources/process-stop.png', 'tooltip': 'Stop download operations', 'id':self.ID_STOP_BUTTON, 'state': 'disabled'} \
            ]

        self.toolbar = UIToolBar(self, description)
                
        ## create the tree view
        self.listPkg = UIListCtrl(self, 'PkgFile')

        ## create the download view
        self.listDownload = UIListCtrl(self, 'DownloadFile', 0, False)
        
        ## main sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, self.toolbar.GetSizerFlags())
        mainSizer.Add(self.listPkg, self.listPkg.GetSizerFlags())
        mainSizer.Add(self.listDownload, self.listDownload.GetSizerFlags())

        self.SetSizerAndFit(mainSizer)

        #self.downloadRefresh = Process(target=self.RefreshDownloadData)
        #self.downloadRefresh = Process(target=DummyProc)
        #self.downloadRefresh = Process(target=self.RefreshDownloadProcess)

    def Rename(self, event = ''):
        checkedEntries = self.listPkg.GetCheckEntries()
        for checkedEntry in checkedEntries:
            filename = self.listPkg.GetEntryText(checkedEntry, 'filename')
            API.Send('RenamePkgFile', filename)
        
        
    def ClearPkgData(self, event = ''):
        self.listPkg.RemoveValues()

    def ClearDownloadData(self, event = ''):
        self.listDownload.RemoveValues()
        
    def FillValues(self, event = ''):
        self.ClearPkgData()
        self.ClearDownloadData()
        
        API.Send('RefreshPkgsData')
        pkgsData = API.Send('GetPkgsData')

        for pkgData in pkgsData:
            #print 'pkgData', pkgData
            self.listPkg.AddEntry(pkgData)

    #def RefreshDownloadProcess(self):
        #while True:
            #self.RefreshDownloadData()

            #timing = 1
            #if timing > 0:
                #time.sleep(timing)
    def Refresh(self):
        self.RefreshDownloadData()
        
    def RefreshDownloadData(self, *args):
        #print 'RefreshDownloadData'
        res = ''
        code = 0
        message = ''
        
        self.ClearDownloadData()
        downloadsData = API.Send('GetDownloadData')
        #print 'downloadsData', downloadsData
        for downloadData in downloadsData:        
            self.listDownload.AddEntry(downloadData)

        return res, code, message
        
    def DownloadDone(self, *args):
        print 'DownloadDone'
        res = ''
        code = 0
        message = ''

        startButton = self.toolbar.GetButtonByID(self.ID_START_BUTTON)
        startButton.Enable()
        stopButton = self.toolbar.GetButtonByID(self.ID_STOP_BUTTON)
        stopButton.Disable()

        return res, code, message
                
    def StartDownload(self, event = ''):
        checkedEntries = self.listPkg.GetCheckEntries()
        urlData = []
        for checkedEntry in checkedEntries:
            #filename = self.listCtrl.GetEntryText(checkedEntry, 'filename')
            downloadURL = self.listPkg.GetEntryText(checkedEntry, 'downloadURL')
            filename = downloadURL.split('/')[-1]

            urlData.append([downloadURL, filename])

        if urlData != []:
            pkgDirectory = API.Send('GetPkgDirectory')
            API.Send('SetDownloadDirectory', pkgDirectory)
            #API.Send('ClearDownloadData')
            API.Send('SetDownloadData', urlData)

            ## fill the download file list
            #self.RefreshDownloadData()
            #self.downloadRefresh.start()
            
            API.Send('StartDownload')

            ## manage toolbar button
            startButton = self.toolbar.GetButtonByID(self.ID_START_BUTTON)
            #startButton = event.GetEventObject()
            startButton.Disable()
            stopButton = self.toolbar.GetButtonByID(self.ID_STOP_BUTTON)
            stopButton.Enable()
            
    def StopDownload(self, event = ''):
        ## manage toolbar button
        startButton = self.toolbar.GetButtonByID(self.ID_START_BUTTON)
        startButton.Enable()
        stopButton = self.toolbar.GetButtonByID(self.ID_STOP_BUTTON)
        stopButton.Disable()

        API.Send('StopDownload')

        #if self.downloadRefresh.is_alive():
            #self.downloadRefresh.terminate()
            #self.downloadRefresh.join()

        API.Send('CleanDownloadFiles')
            

class VitaFilesView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ## create the toolbar toolbar
        description = [ \
            {'command': self.FillValues, 'image': 'resources/view-refresh.png', 'tooltip': 'Refresh local vita app information'}, \
            {'command': self.ClearValues, 'image': 'resources/edit-clear.png', 'tooltip': 'Clear local vita app information'} \
            ]

        self.toolbar = UIToolBar(self, description)
        
        ## create the tree view
        self.listCtrl = UIListCtrl(self, 'VitaFile')

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, self.toolbar.GetSizerFlags())
        mainSizer.Add(self.listCtrl, self.listCtrl.GetSizerFlags())

        self.SetSizerAndFit(mainSizer)
        
    def ClearValues(self, event = ''):
        self.listCtrl.RemoveValues()
        
    def FillValues(self):
        vitaData = API.Send('GetLocalVitaData')
        
        for data in vitaData:
            self.listCtrl.AddEntry(data)
        
class SettingsView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        ## file/directory browsers definition and sizer
        self.pkgDirectory = wx.DirPickerCtrl(self, style = wx.DIRP_DEFAULT_STYLE|wx.DIRP_DIR_MUST_EXIST, message = 'Select the Pkg Directory')
        self.pkgDirectory.Bind(wx.EVT_DIRPICKER_CHANGED, self.OnSetPkgDir)
        self.vitaDirectory = wx.DirPickerCtrl(self, style = wx.DIRP_DEFAULT_STYLE|wx.DIRP_DIR_MUST_EXIST, message = 'Select the vita Directory')
        self.vitaDirectory.Bind(wx.EVT_DIRPICKER_CHANGED, self.OnSetVitaDir)
        self.pkgGameFile = wx.FilePickerCtrl(self, message = 'Select the game File')
        self.pkgGameFile.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSetGameFile)
        self.pkgDLCFile = wx.FilePickerCtrl(self, message = 'Select the DLC File')
        self.pkgDLCFile.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSetDLCFile)
        self.pkgUpdateFile = wx.FilePickerCtrl(self, message = 'Select the update File')
        self.pkgUpdateFile.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSetUpdateFile)

        text1 = wx.StaticText(self, label = 'Pkg Directory') 
        text2 = wx.StaticText(self, label = 'Vita Directory') 
        text3 = wx.StaticText(self, label = 'Game File')
        text4 = wx.StaticText(self, label = 'DLC File')
        text5 = wx.StaticText(self, label = 'Update File')

        ## configure the sizers
        textFlags = wx.SizerFlags(0)
        textFlags.Border(wx.ALL, 3)
        
        browserFlags = wx.SizerFlags(1)
        #browserFlags.Align(wx.ALIGN_RIGHT).Expand().Border(wx.ALL, 0)
        browserFlags.Align(wx.ALIGN_RIGHT).Expand()
        
        mixFlags = wx.SizerFlags(0)
        #mixFlags.Expand().Border(wx.ALL, 0)
        mixFlags.Expand()

        pkgDirectorySizer = wx.BoxSizer(wx.HORIZONTAL)
        pkgDirectorySizer.Add(text1, textFlags)
        pkgDirectorySizer.Add(self.pkgDirectory, browserFlags)
        
        vitaDirectorySizer = wx.BoxSizer(wx.HORIZONTAL)
        vitaDirectorySizer.Add(text2, textFlags)
        vitaDirectorySizer.Add(self.vitaDirectory, browserFlags)
        
        pkgGameFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        pkgGameFileSizer.Add(text3, textFlags)
        pkgGameFileSizer.Add(self.pkgGameFile, browserFlags)
        
        pkgDLCFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        pkgDLCFileSizer.Add(text4, textFlags)
        pkgDLCFileSizer.Add(self.pkgDLCFile, browserFlags)
        
        pkgUpdateFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        pkgUpdateFileSizer.Add(text5, textFlags)
        pkgUpdateFileSizer.Add(self.pkgUpdateFile, browserFlags)
        
        ## save ini file button definition and sizer
        self.saveButton = wx.Button(self, id = ID_BUTTON_SAVE_INI, label='Save Ini')
        self.saveButton.Bind(wx.EVT_BUTTON, self.OnSaveIni)

        self.resetButton = wx.Button(self, id = ID_BUTTON_RESET_INI, label='Reset Ini Values')
        self.resetButton.Bind(wx.EVT_BUTTON, self.OnResetIni)

        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.saveButton, 0, wx.ALL, 5)
        buttonSizer.Add(self.resetButton, 0, wx.ALL, 5)

        ## add each sizer to the main sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(pkgDirectorySizer, mixFlags)
        mainSizer.Add(vitaDirectorySizer, mixFlags)
        mainSizer.Add(pkgGameFileSizer, mixFlags)
        mainSizer.Add(pkgDLCFileSizer, mixFlags)
        mainSizer.Add(pkgUpdateFileSizer, mixFlags)
        mainSizer.Add(buttonSizer, 0, wx.LEFT, 0)

        self.SetSizerAndFit(mainSizer)
        
    def FillValues(self):
        pkgDirectory = API.Send('GetPkgDirectory')
        self.pkgDirectory.SetPath(pkgDirectory)

        vitaDirectory = API.Send('GetVitaDirectory')
        self.vitaDirectory.SetPath(vitaDirectory)

        gameFile = API.Send('GetGameFile')
        self.pkgGameFile.SetPath(gameFile)
        
        dlcFile = API.Send('GetDLCFile')
        self.pkgDLCFile.SetPath(dlcFile)
        
        updateFile = API.Send('GetUpdateFile')
        self.pkgUpdateFile.SetPath(updateFile)
        
    def OnResetIni(self, event):
        pkgDirectory = API.Send('GetIniValue', 'pkgDirectory')
        self.pkgDirectory.SetPath(pkgDirectory)

        vitaDirectory = API.Send('GetIniValue', 'vitaDirectory')
        self.vitaDirectory.SetPath(vitaDirectory)

        gameFile = API.Send('GetIniValue', 'pkgGameFile')
        self.pkgGameFile.SetPath(gameFile)
        
        dlcFile = API.Send('GetIniValue', 'pkgDLCFile')
        self.pkgDLCFile.SetPath(dlcFile)
        
        updateFile = API.Send('GetIniValue', 'pkgUpdateFile')
        self.pkgUpdateFile.SetPath(updateFile)
        
    def OnSaveIni(self, event):
        ## set the new values
        pkgDirectory = self.pkgDirectory.GetPath()
        API.Send('SetIniValue', 'pkgDirectory', pkgDirectory)
        
        pkgGameFile = self.pkgGameFile.GetPath()
        API.Send('SetIniValue', 'pkgGameFile', pkgGameFile)
        
        pkgDLCFile = self.pkgDLCFile.GetPath()
        API.Send('SetIniValue', 'pkgDLCFile', pkgDLCFile)
        
        pkgUpdateFile = self.pkgUpdateFile.GetPath()
        API.Send('SetIniValue', 'pkgUpdateFile', pkgUpdateFile)
        
        vitaDirectory = self.vitaDirectory.GetPath()
        API.Send('SetIniValue', 'vitaDirectory', vitaDirectory)
        
        ## serialize the ini values
        API.Send('SerializeIni')

    def OnReset(self, event):
        self.FillIniValues()
        
    def OnSetPkgDir(self, event):
        pkgDirectory = self.pkgDirectory.GetPath()
        API.Send('SetPkgDirectory', pkgDirectory)
        
    def OnSetVitaDir(self, event):
        vitaDirectory = self.vitaDirectory.GetPath()
        API.Send('SetVitaDirectory', vitaDirectory)
        
    def OnSetGameFile(self, event):
        pkgGameFile = self.pkgGameFile.GetPath()
        API.Send('SetGameFile', pkgGameFile)
        
    def OnSetDLCFile(self, event):
        pkgDLCFile = self.pkgDLCFile.GetPath()
        API.Send('SetDLCFile', pkgDLCFile)
    
    def OnSetUpdateFile(self, event):
        pkgUpdateFile = self.pkgUpdateFile.GetPath()
        API.Send('SetUpdateFile', pkgUpdateFile)
