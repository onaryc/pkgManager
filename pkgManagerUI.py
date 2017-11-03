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
        self.ID_RESET_DB = wx.NewId()
        self.ID_SAVE_DB = wx.NewId()
        self.ID_IMPORT_GAMES = wx.NewId()
        self.ID_IMPORT_DLCS = wx.NewId()
        self.ID_IMPORT_UPDATES = wx.NewId()
        self.ID_IMPORT_PSMS = wx.NewId()
        self.ID_IMPORT_PSXS = wx.NewId()
        self.ID_IMPORT_PSPS = wx.NewId()
        self.ID_IMPORT_PSPDLCS = wx.NewId()
        self.ID_IMPORT_PKGI = wx.NewId()
        
        fileMenu = wx.Menu()
        
        #fileMenu.AppendSeparator()
        menuExit = fileMenu.Append(wx.ID_EXIT,"E&xit"," Close Pkg Manager")

        ## database menu
        dbMenu = wx.Menu()
        menuResetDB = dbMenu.Append(self.ID_RESET_DB,"Reset"," Reset Database")
        menuSaveDB = dbMenu.Append(self.ID_SAVE_DB,"Save"," Save Database")
        dbMenu.AppendSeparator()
        menuImportGames = dbMenu.Append(self.ID_IMPORT_GAMES,"Import Vita Games"," Import Vita Games")
        menuImportDLCs = dbMenu.Append(self.ID_IMPORT_DLCS,"Import Vita DLCs"," Import Vita DLC")
        menuImportUpdates = dbMenu.Append(self.ID_IMPORT_UPDATES,"Import Vita Updates"," Import Vita Updates")
        dbMenu.AppendSeparator()
        menuImportPSMs = dbMenu.Append(self.ID_IMPORT_PSMS,"Import PSM Games"," Import PSM Games")
        dbMenu.AppendSeparator()
        menuImportPSXs = dbMenu.Append(self.ID_IMPORT_PSXS,"Import PSX Games"," Import PSX Games")
        dbMenu.AppendSeparator()
        menuImportPSPs = dbMenu.Append(self.ID_IMPORT_PSPS,"Import PSP Games"," Import PSP Games")
        menuImportPSPDLCs = dbMenu.Append(self.ID_IMPORT_PSPS,"Import PSP DLC"," Import PSP DLC")
        dbMenu.AppendSeparator()
        menuImportPKGI = dbMenu.Append(self.ID_IMPORT_PKGI,"Import PKGI"," Import PKGI file")

        # other menu
        otherMenu = wx.Menu()
        menuAbout = otherMenu.Append(wx.ID_ABOUT, "&About"," Information about Pkg Manager")
        
        # Creating the menubar.
        menuBar = wx.MenuBar()

        ## adding menu to the menu bar
        menuBar.Append(fileMenu,"&File")
        menuBar.Append(dbMenu,"Database")
        menuBar.Append(otherMenu,"&?")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnResetDB, menuResetDB)
        self.Bind(wx.EVT_MENU, self.OnSaveDB, menuSaveDB)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportGames)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportDLCs)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportUpdates)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportPSMs)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportPSXs)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportPSPs)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportPSPDLCs)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportPKGI)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        ## contruct the notebook
        self.notebook = wx.Notebook(self)

        self.panelPkg = PkgFilesView(self.notebook)
        self.panelVita = VitaFilesView(self.notebook)
        self.panelSettings = SettingsView(self.notebook)

        self.notebook.AddPage(self.panelPkg, "Pkg Files")
        self.notebook.AddPage(self.panelVita, "Vita Files")
        self.notebook.AddPage(self.panelSettings, "Settings")

        ## subscribe to api ctrl
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

    def OnResetDB(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to reset the pkg database?",
            "Confirm DB Reset", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            API.Send('ResetDB')
            
    def OnSaveDB(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to save the pkg database?",
            "Confirm DB Save", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            API.Send('SaveDB')
            
    def OnImport(self, event):
        itemId = event.GetId()
        dbTitle = ''
        dbExtension = ''
        importType = ''
        if itemId == self.ID_IMPORT_GAMES:
            importType = 'game'
            dbTitle = 'Select Vita Game File'
            dbExtension = 'Vita Game file (*.tsv)|*.tsv'
        elif itemId == self.ID_IMPORT_DLCS:
            importType = 'dlc'
            dbTitle = 'Select Vita DLC File'
            dbExtension = 'Vita DLC file (*.tsv)|*.tsv'
        elif itemId == self.ID_IMPORT_UPDATES:
            importType = 'update'
            dbTitle = 'Select Vita Update File'
            dbExtension = 'Vita Update file (*.tsv)|*.tsv'
        elif itemId == self.ID_IMPORT_PSMS:
            importType = 'psm'
            dbTitle = 'Select PSM Game File'
            dbExtension = 'PSM Game file (*.tsv)|*.tsv'
        elif itemId == self.ID_IMPORT_PSXS:
            importType = 'psx'
            dbTitle = 'Select Psx Game File'
            dbExtension = 'Psx Game file (*.tsv)|*.tsv'
        elif itemId == self.ID_IMPORT_PSPS:
            importType = 'psp'
            dbTitle = 'Select PSP Game File'
            dbExtension = 'PSP Game file (*.tsv)|*.tsv'
        elif itemId == self.ID_IMPORT_PSPDLCS:
            importType = 'pspdlc'
            dbTitle = 'Select PSP DLC File'
            dbExtension = 'PSP DLC file (*.tsv)|*.tsv'
        elif itemId == self.ID_IMPORT_PKGI:
            importType = 'pkgi'
            dbTitle = 'Select Pkgi File'
            dbExtension = 'Pkgi file (*.tsv)|*.tsv'
        
        if importType != '':
            openDlg = wx.FileDialog(self, dbTitle, "", "", dbExtension, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

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

class UIListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, CheckListCtrlMixin, ColumnSorterMixin):
    def __init__(self, parent, className, proportion=1, checkBox = True):
        #wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT)
        #wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT | wx.LC_AUTOARRANGE | wx.LC_SORT_ASCENDING)

        ListCtrlAutoWidthMixin.__init__(self)
        if checkBox == True:
            CheckListCtrlMixin.__init__(self)

        self.mapAttributesCol = {}
        self.mapColAttributes = {}
        
        ## for column sorting
        self.itemDataMap = dict()

        ## add the column based on the data model attributes
        attributes = API.Send('GetModelAttributes', className)
        for attribute in attributes:
            if 'display' in attribute:
                displayName = attribute['display']

                if 'position' in attribute:
                    colIndex = self.InsertColumn(attribute['position'], displayName)
                else:
                    colIndex = self.AppendColumn(displayName)

                self.mapAttributesCol[attribute['name']] = colIndex
                self.mapColAttributes[colIndex] = attribute['name']

        ## for column sorting
        ColumnSorterMixin.__init__(self, self.GetColumnCount())
        
        self.sizerFlags = wx.SizerFlags(proportion)
        self.sizerFlags.Expand()

        ## binds
        if checkBox == True:
            self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnShowPopup)
        #self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        
        self.ID_CONTEXTUAL_CHECKED = wx.NewId()
        self.ID_CONTEXTUAL_CHECK_ALL = wx.NewId()
        self.ID_CONTEXTUAL_UNCHECKED = wx.NewId()
        self.ID_CONTEXTUAL_UNCHECK_ALL = wx.NewId()

    def GetListCtrl(self):
        return self
        
    def RemoveValues(self):
        self.DeleteAllItems()
        self.itemDataMap = dict()
        
    def AddEntry(self, entry):
        ## get the text in col order
        tmp = []
        tmp2 = ()
        for i in range(self.GetColumnCount()):
            name = self.mapColAttributes[i]
            
            tmp.append(entry[name])
            tmp2 += (entry[name],)

        if tmp != []:
            #print 'tmp', tmp 
            rowIndex = self.Append(tmp)
            
            ## for sorting
            self.SetItemData(rowIndex, rowIndex)
            self.itemDataMap[rowIndex] = tmp2
            
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
                #if rowIndex % 2:
                color.MakeDisabled(200)
                #else:
                    #color.MakeDisabled(255)
                    
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

    #def ListCompareFunction(self, item1, item2):
        #print 'item1', item1
        #print 'item2', item2
        
    #def OnColClick(self, event):
        #itemId = event.GetId()
        #print 'OnColClick', event.GetColumn(), event.GetText()
        #self.SortItems(self.ListCompareFunction)

class checkListComboPopup(wx.ComboPopup):
    def __init__(self, choices):
        wx.ComboPopup.__init__(self)
        #self.checklist = wx.PreCheckListBox()
        self.checklist = wx.CheckListBox()
        self._value = -1

    def Init(self):
        self._value = -1

    def Create(self, parent):
        return self.checklist.Create(parent, 1, wx.Point(0,0), wx.DefaultSize)

    def GetControl(self):
        return self.checklist

    def SetStringValue(self, s):
        pass

    def GetStringValue(self):
        if (self._value >= 0):
            return self.checklist.GetItemText(self, self._value)
        else:
            return wx.EmptyString

    def OnMouseMove(self, event):
        pass

    def GetPreCheckList(self):
        return self.checklist

    def OnMouseClick(self, event):
        pass
        
class UIToolbarButton(wx.BitmapButton):
    def __init__(self, parent, image, command='', tooltip='', idB=-1):
        self.buttonImage = wx.Image(name = image)
        self.buttonBitmap =  self.buttonImage.ConvertToBitmap()
        
        wx.BitmapButton.__init__(self, parent, bitmap = self.buttonBitmap, id=idB)

        if command !='':
            self.Bind(wx.EVT_BUTTON, command)

        self.SetToolTip(tooltip)

class UIToolbarCheck(wx.CheckBox):
    def __init__(self, parent, label, command='', tooltip='', checked=False, idB=-1):
        wx.CheckBox.__init__(self, parent, id=idB, label=label)

        if command !='':
            self.Bind(wx.EVT_CHECKBOX, command)

        self.SetToolTip(tooltip)
        
        self.SetValue(checked)
        
class UIToolBar(wx.BoxSizer):
    def __init__(self, parent, description):
        wx.BoxSizer.__init__(self, orient = wx.HORIZONTAL)

        self.toolbarItemById = {}
        self.sizerFlags = wx.SizerFlags(0)
        self.sizerFlags.Align(wx.ALIGN_CENTER_VERTICAL)
        #itemFlags = wx.SizerFlags(0)
        
        for itemData in description:
            tbItem = -1

            ## get data
            label = ''
            if 'label' in itemData:
                label = itemData['label']
                    
            command = ''
            if 'command' in itemData:
                command = itemData['command']

            idItem = -1
            if 'id' in itemData:
                idItem = itemData['id']

            if 'tooltip' in itemData:
                tooltip = itemData['tooltip']

            ## create the UI toolbar item
            itemType = itemData['type']
            if itemType == 'button':
                image = itemData['image']
                tbItem = UIToolbarButton(parent, image, command, tooltip, idItem)
            elif itemType == 'check':
                checked = False
                if 'checked' in itemData:
                    checked = itemData['checked']
                tbItem = UIToolbarCheck(parent, label, command, tooltip, checked, idItem)
            elif itemType == 'separator':
                size = itemData['size']
                self.AddSpacer(size)
            elif itemType == 'progress':
                tbItem =  wx.Gauge(parent, idItem)
            elif itemType == 'checklist':
                choices = itemData['choices']
                tbItem =  checkListComboPopup(choices = choices)
                #tbItem =  wx.CheckListBox(parent, idItem, choices = choices)
                
            if tbItem != -1:
                if idItem != -1:
                    self.toolbarItemById[idItem] = tbItem 

                if 'state' in itemData:
                    state = itemData['state']
                    if state == 'disabled':
                        tbItem.Disable()
                
                self.Add(tbItem, self.sizerFlags)

    def GetSizerFlags(self):
        return self.sizerFlags

    def GetToolbarItemByID (self, idB):
        res = ''
        
        if idB in self.toolbarItemById:
            res = self.toolbarItemById[idB]

        return res
    
class PkgFilesView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        API.Subscribe('RefreshDownloadData', lambda args: self.RefreshDownloadData(*args))
        API.Subscribe('RefreshImportData', lambda args: self.RefreshImportData(*args))
        API.Subscribe('DownloadDone', lambda args: self.DownloadDone(*args))

        ## create the toolbar toolbar
        self.ID_START_BUTTON = wx.NewId()
        self.ID_PAUSE_BUTTON = wx.NewId()
        self.ID_STOP_BUTTON = wx.NewId()
        self.ID_CHECKLIST_PKG = wx.NewId()
        self.ID_CHECK_GAME = wx.NewId()
        self.ID_CHECK_DLC = wx.NewId()
        self.ID_CHECK_UPDATE = wx.NewId()
        self.ID_CHECK_PSM = wx.NewId()
        self.ID_CHECK_PSX = wx.NewId()
        self.ID_CHECK_PSP = wx.NewId()
        self.ID_CHECK_PSPDLC = wx.NewId()
        self.ID_PROGRESS = wx.NewId()

        #description = [ \
            #{'type': 'button', 'command': self.FillValues, 'image': 'resources/view-refresh.png', 'tooltip': 'Refresh Pkgs information'}, \
            #{'type': 'button', 'command': self.ClearPkgData, 'image': 'resources/edit-clear.png', 'tooltip': 'Clear Pkgs information'}, \
            #{'type': 'separator', 'size': 5}, \
            #{'type': 'check', 'command': '', 'label': 'Game', 'tooltip': 'Select Game', 'id':self.ID_CHECK_GAME, 'checked': True}, \
            #{'type': 'check', 'command': '', 'label': 'DLC', 'tooltip': 'Select DLC', 'id':self.ID_CHECK_DLC, 'checked': True}, \
            #{'type': 'check', 'command': '', 'label': 'Update', 'tooltip': 'Select Update', 'id':self.ID_CHECK_UPDATE, 'checked': True}, \
            #{'type': 'check', 'command': '', 'label': 'PSM', 'tooltip': 'Select PSM', 'id':self.ID_CHECK_PSM, 'checked': True}, \
            #{'type': 'check', 'command': '', 'label': 'PSX', 'tooltip': 'Select PSX', 'id':self.ID_CHECK_PSX, 'checked': True}, \
            #{'type': 'check', 'command': '', 'label': 'PSP', 'tooltip': 'Select PSP', 'id':self.ID_CHECK_PSP, 'checked': True}, \
            #{'type': 'check', 'command': '', 'label': 'PSPDLC', 'tooltip': 'Select PSP DLC', 'id':self.ID_CHECK_PSPDLC, 'checked': True}, \
           ##{'type': 'button', 'command': self.Rename, 'image': 'resources/edit-copy.png', 'tooltip': 'Rename selected Pkg files', 'state': 'disabled'}, \
            #{'type': 'button', 'command': self.StartDownload, 'image': 'resources/media-playback-start.png', 'tooltip': 'Download selected Pkg files', 'id':self.ID_START_BUTTON}, \
            #{'type': 'button', 'command': self.PauseDownload, 'image': 'resources/media-playback-pause.png', 'tooltip': 'Pause current downloads', 'id':self.ID_PAUSE_BUTTON}, \
            #{'type': 'button', 'command': self.StopDownload, 'image': 'resources/media-playback-stop.png', 'tooltip': 'Stop download operations', 'id':self.ID_STOP_BUTTON, 'state': 'disabled'}, \
            #{'type': 'separator', 'size': 5}, \
            #{'type': 'progress', 'id':self.ID_PROGRESS}, \
            #]
        description = [ \
            {'type': 'button', 'command': self.FillValues, 'image': 'resources/view-refresh.png', 'tooltip': 'Refresh Pkgs information'}, \
            {'type': 'button', 'command': self.ClearPkgData, 'image': 'resources/edit-clear.png', 'tooltip': 'Clear Pkgs information'}, \
            {'type': 'separator', 'size': 5}, \
            {'type': 'checklist', 'command': '', 'label': 'Game', 'tooltip': 'Select Game', 'id':self.ID_CHECKLIST_PKG, 'choices': ['Game', 'DLC', 'Update', 'PSM', 'PSX', 'PSP', 'PSP DLC']}, \
           #{'type': 'button', 'command': self.Rename, 'image': 'resources/edit-copy.png', 'tooltip': 'Rename selected Pkg files', 'state': 'disabled'}, \
            {'type': 'button', 'command': self.StartDownload, 'image': 'resources/media-playback-start.png', 'tooltip': 'Download selected Pkg files', 'id':self.ID_START_BUTTON}, \
            {'type': 'button', 'command': self.PauseDownload, 'image': 'resources/media-playback-pause.png', 'tooltip': 'Pause current downloads', 'id':self.ID_PAUSE_BUTTON}, \
            {'type': 'button', 'command': self.StopDownload, 'image': 'resources/media-playback-stop.png', 'tooltip': 'Stop download operations', 'id':self.ID_STOP_BUTTON, 'state': 'disabled'}, \
            {'type': 'separator', 'size': 5}, \
            {'type': 'progress', 'id':self.ID_PROGRESS}, \
            ]

        self.toolbar = UIToolBar(self, description)
                
        ## create the tree view
        #self.listPkg = UIListCtrl(self, 'GamePkgFile')
        self.listPkg = UIListCtrl(self, 'PkgFile')

        ## create the download view
        self.listDownload = UIListCtrl(self, 'DownloadFile', 0, False)
        
        ## main sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, self.toolbar.GetSizerFlags())
        mainSizer.Add(self.listPkg, self.listPkg.GetSizerFlags())
        mainSizer.Add(self.listDownload, self.listDownload.GetSizerFlags())

        self.SetSizerAndFit(mainSizer)

        #self.stopThreads = False
        #self.pauseThreads = False
        #self.downloadRefresh = Thread(target=self.RefreshDownloadThread, args=(lambda: self.pauseThreads, lambda: self.stopThreads))

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

        #gameChecked = self.toolbar.GetToolbarItemByID(self.ID_CHECK_GAME).GetValue()
        #dlcChecked = self.toolbar.GetToolbarItemByID(self.ID_CHECK_DLC).GetValue()
        #updateChecked = self.toolbar.GetToolbarItemByID(self.ID_CHECK_UPDATE).GetValue()
        #psmChecked = self.toolbar.GetToolbarItemByID(self.ID_CHECK_PSM).GetValue()
        #psxChecked = self.toolbar.GetToolbarItemByID(self.ID_CHECK_PSX).GetValue()
        #pspChecked = self.toolbar.GetToolbarItemByID(self.ID_CHECK_PSP).GetValue()
        #pspDlcChecked = self.toolbar.GetToolbarItemByID(self.ID_CHECK_PSPDLC).GetValue()
        gameChecked = True
        dlcChecked = True
        updateChecked = True
        psmChecked = True
        psxChecked = True
        pspChecked = True
        pspDlcChecked = True
        
        API.Send('RefreshPkgsData', gameChecked, dlcChecked, updateChecked, psmChecked, psxChecked, pspChecked, pspDlcChecked)
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
        pass
        #self.RefreshDownloadData()
        
    #def RefreshDownloadThread(self, pauseThread, stopThread):
        #print 'RefreshDownloadData'
        #while True:
            #if stopThread() == True:
                #break
                
            #if pauseThread() == False:
                #self.RefreshDownloadData()

                #time.sleep(1)
        
    def RefreshDownloadData(self, *args):
        #print 'RefreshDownloadData'
        res = ''
        code = 0
        message = ''

        self.ClearDownloadData()
        downloadsData = API.Send('GetDownloadData')
        for downloadData in downloadsData:        
            self.listDownload.AddEntry(downloadData)

        return res, code, message
        
    def RefreshImportData(self, *args):
        #print 'RefreshImportData'
        res = ''
        code = 0
        message = ''

        importPercent = args[0]
        print 'importPercent', importPercent
        self.toolbar.GetToolbarItemByID(self.ID_PROGRESS).SetValue(importPercent)

        return res, code, message
        
    def DownloadDone(self, *args):
        #print 'DownloadDone'
        res = ''
        code = 0
        message = ''

        startButton = self.toolbar.GetToolbarItemByID(self.ID_START_BUTTON)
        startButton.Enable()
        pauseButton = self.toolbar.GetToolbarItemByID(self.ID_PAUSE_BUTTON)
        pauseButton.Disable()
        stopButton = self.toolbar.GetToolbarItemByID(self.ID_STOP_BUTTON)
        stopButton.Disable()

        return res, code, message
                
    def StartDownload(self, event = ''):
        onGoingDownloads = API.Send('OnGoingDownloads')
        if onGoingDownloads == True:
            API.Send('ResumeDownload')
            #self.stopThreads = False
            #self.pauseThreads = False
            startButton = self.toolbar.GetToolbarItemByID(self.ID_START_BUTTON)
            startButton.Disable()
            pauseButton = self.toolbar.GetToolbarItemByID(self.ID_PAUSE_BUTTON)
            pauseButton.Enable()
            stopButton = self.toolbar.GetToolbarItemByID(self.ID_STOP_BUTTON)
            stopButton.Enable()                
        else:
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
                #self.stopThreads = False
                #self.pauseThreads = False
                #self.downloadRefresh.start()
                
                API.Send('StartDownload')

                ## manage toolbar button
                startButton = self.toolbar.GetToolbarItemByID(self.ID_START_BUTTON)
                startButton.Disable()
                pauseButton = self.toolbar.GetToolbarItemByID(self.ID_PAUSE_BUTTON)
                pauseButton.Enable()
                stopButton = self.toolbar.GetToolbarItemByID(self.ID_STOP_BUTTON)
                stopButton.Enable()

    
    def PauseDownload(self, event = ''):
        ## manage toolbar button
        startButton = self.toolbar.GetToolbarItemByID(self.ID_START_BUTTON)
        startButton.Enable()
        pauseButton = self.toolbar.GetToolbarItemByID(self.ID_PAUSE_BUTTON)
        pauseButton.Disable()
        stopButton = self.toolbar.GetToolbarItemByID(self.ID_STOP_BUTTON)
        stopButton.Enable()

        API.Send('PauseDownload')

        #self.pauseThreads = True
            
    def StopDownload(self, event = ''):
        ## manage toolbar button
        startButton = self.toolbar.GetToolbarItemByID(self.ID_START_BUTTON)
        startButton.Enable()
        pauseButton = self.toolbar.GetToolbarItemByID(self.ID_PAUSE_BUTTON)
        pauseButton.Disable()
        stopButton = self.toolbar.GetToolbarItemByID(self.ID_STOP_BUTTON)
        stopButton.Disable()

        API.Send('StopDownload')

        #self.stopThreads = True
        #self.downloadRefresh.join()
        self.ClearDownloadData()

        API.Send('CleanDownloadFiles')
            

class VitaFilesView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        ## create the toolbar toolbar
        description = [ \
            {'type': 'button', 'command': self.FillValues, 'image': 'resources/view-refresh.png', 'tooltip': 'Refresh local vita app information'}, \
            {'type': 'button', 'command': self.ClearValues, 'image': 'resources/edit-clear.png', 'tooltip': 'Clear local vita app information'} \
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

        self.pkgDBFile = wx.FilePickerCtrl(self, message = 'Select the database File')
        self.pkgDBFile.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSetDBFile)
        #self.pkgGameFile = wx.FilePickerCtrl(self, message = 'Select the game File')
        #self.pkgGameFile.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSetGameFile)
        #self.pkgDLCFile = wx.FilePickerCtrl(self, message = 'Select the DLC File')
        #self.pkgDLCFile.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSetDLCFile)
        #self.pkgUpdateFile = wx.FilePickerCtrl(self, message = 'Select the update File')
        #self.pkgUpdateFile.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSetUpdateFile)

        text1 = wx.StaticText(self, label = 'Pkg Directory') 
        text2 = wx.StaticText(self, label = 'Vita Directory')
        text3 = wx.StaticText(self, label = 'Database File')
        
        #text3 = wx.StaticText(self, label = 'Game File')
        #text4 = wx.StaticText(self, label = 'DLC File')
        #text5 = wx.StaticText(self, label = 'Update File')

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
        
        pkgDBFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        pkgDBFileSizer.Add(text3, textFlags)
        pkgDBFileSizer.Add(self.pkgDBFile, browserFlags)
        
        #pkgGameFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        #pkgGameFileSizer.Add(text3, textFlags)
        #pkgGameFileSizer.Add(self.pkgGameFile, browserFlags)
        
        #pkgDLCFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        #pkgDLCFileSizer.Add(text4, textFlags)
        #pkgDLCFileSizer.Add(self.pkgDLCFile, browserFlags)
        
        #pkgUpdateFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        #pkgUpdateFileSizer.Add(text5, textFlags)
        #pkgUpdateFileSizer.Add(self.pkgUpdateFile, browserFlags)
        
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
        mainSizer.Add(pkgDBFileSizer, mixFlags)
        #mainSizer.Add(pkgGameFileSizer, mixFlags)
        #mainSizer.Add(pkgDLCFileSizer, mixFlags)
        #mainSizer.Add(pkgUpdateFileSizer, mixFlags)
        mainSizer.Add(buttonSizer, 0, wx.LEFT, 0)

        self.SetSizerAndFit(mainSizer)
        
    def FillValues(self):
        pkgDirectory = API.Send('GetPkgDirectory')
        self.pkgDirectory.SetPath(pkgDirectory)

        vitaDirectory = API.Send('GetVitaDirectory')
        self.vitaDirectory.SetPath(vitaDirectory)

        dbFile = API.Send('GetDBFile')
        self.pkgDBFile.SetPath(dbFile)
        
        #gameFile = API.Send('GetGameFile')
        #self.pkgGameFile.SetPath(gameFile)
        
        #dlcFile = API.Send('GetDLCFile')
        #self.pkgDLCFile.SetPath(dlcFile)
        
        #updateFile = API.Send('GetUpdateFile')
        #self.pkgUpdateFile.SetPath(updateFile)
        
    def OnResetIni(self, event):
        pkgDirectory = API.Send('GetIniValue', 'pkgDirectory')
        self.pkgDirectory.SetPath(pkgDirectory)

        vitaDirectory = API.Send('GetIniValue', 'vitaDirectory')
        self.vitaDirectory.SetPath(vitaDirectory)

        dbFile = API.Send('GetIniValue', 'pkgDBFile')
        self.pkgDBFile.SetPath(dbFile)
        #gameFile = API.Send('GetIniValue', 'pkgGameFile')
        #self.pkgGameFile.SetPath(gameFile)
        
        #dlcFile = API.Send('GetIniValue', 'pkgDLCFile')
        #self.pkgDLCFile.SetPath(dlcFile)
        
        #updateFile = API.Send('GetIniValue', 'pkgUpdateFile')
        #self.pkgUpdateFile.SetPath(updateFile)
        
    def OnSaveIni(self, event):
        ## set the new values
        pkgDirectory = self.pkgDirectory.GetPath()
        API.Send('SetIniValue', 'pkgDirectory', pkgDirectory)
        
        pkgDBFile = self.pkgDBFile.GetPath()
        API.Send('SetIniValue', 'pkgDBFile', pkgDBFile)
        #pkgGameFile = self.pkgGameFile.GetPath()
        #API.Send('SetIniValue', 'pkgGameFile', pkgGameFile)
        
        #pkgDLCFile = self.pkgDLCFile.GetPath()
        #API.Send('SetIniValue', 'pkgDLCFile', pkgDLCFile)
        
        #pkgUpdateFile = self.pkgUpdateFile.GetPath()
        #API.Send('SetIniValue', 'pkgUpdateFile', pkgUpdateFile)
        
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
        
    def OnSetDBFile(self, event):
        pkgDBFile = self.pkgDBFile.GetPath()
        API.Send('SetDBFile', pkgDBFile)
    #def OnSetGameFile(self, event):
        #pkgGameFile = self.pkgGameFile.GetPath()
        #API.Send('SetGameFile', pkgGameFile)
        
    #def OnSetDLCFile(self, event):
        #pkgDLCFile = self.pkgDLCFile.GetPath()
        #API.Send('SetDLCFile', pkgDLCFile)
    
    #def OnSetUpdateFile(self, event):
        #pkgUpdateFile = self.pkgUpdateFile.GetPath()
        #API.Send('SetUpdateFile', pkgUpdateFile)
