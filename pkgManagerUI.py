#!/usr/bin/env python2
try:
    ## python module
    import os

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

class UI(wx.Frame):
    def __init__(self, title = 'Pkg Manager', size=(800,400)):
        self.app = wx.App(False)
        
        wx.Frame.__init__(self, None, title=title, size=size)
        
        self.statusBar = self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        fileMenu = wx.Menu()
        menuExit = fileMenu.Append(wx.ID_EXIT,"E&xit"," Close Pkg Manager")

        ## edit menu
        #editMenu = wx.Menu()
        #menuConfiguration = editMenu.Append(ID_MENU_SETTINGS,"Settings"," Settings")

        ## tools menu
        toolsMenu = wx.Menu()
        menuToolsRename = toolsMenu.Append(ID_MENU_RENAME_ALL,"Rename All"," rename all pkg")
        menuToolsDownload = toolsMenu.Append(ID_MENU_DOWNLOAD_ALL,"Download All"," download all pkg")

        # other menu
        otherMenu = wx.Menu()
        menuAbout = otherMenu.Append(wx.ID_ABOUT, "&About"," Information about Pkg Manager")
        
        # Creating the menubar.
        menuBar = wx.MenuBar()

        ## adding menu to the menu bar
        menuBar.Append(fileMenu,"&File")
        menuBar.Append(toolsMenu,"&Tools")
        #menuBar.Append(editMenu,"&Edit")
        menuBar.Append(otherMenu,"&?")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events.
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
        
        self.Show(True)

        ## a disgraceful black background color is displayed on panel toolbar, it disapears when panel are selected
        self.notebook.ChangeSelection(1)
        self.notebook.ChangeSelection(0)

    def Start(self):
        self.panelPkg.FillValues()
        self.panelVita.FillValues()
        self.panelSettings.FillValues()
        
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

    def SendUIMessage(self, *args):
        message = args[0]
        code = args[1]
        
        self.statusBar.SetStatusText(message, 0) 

class UIListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin, CheckListCtrlMixin):
    def __init__(self, parent, className):
        #wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT)

        ListCtrlAutoWidthMixin.__init__(self)
        CheckListCtrlMixin.__init__(self)
        #self.EnableAlternateRowColours(True)
        #self.AppendColumn('')

        self.mapAttributesCol = {}
        self.mapColAttributes = {}
        ## add the column based on the data model attributes
        attributes = API.Send('GetModelAttributes', className)
        for attribute in attributes:
            if 'display' in attribute:
                displayName = attribute['display']
            #else:
                #displayName = attribute['name']

                colIndex = self.AppendColumn(displayName)                
                self.mapAttributesCol[attribute['name']] = colIndex
                self.mapColAttributes[colIndex] = attribute['name']

        self.sizerFlags = wx.SizerFlags(1)
        self.sizerFlags.Expand()

        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnShowPopup)

        self.ID_CONTEXTUAL_CHECKED = wx.NewId()
        self.ID_CONTEXTUAL_UNCHECKED = wx.NewId()
        
        
    def RemoveValues(self):
        self.DeleteAllItems()
        
    def AddEntry(self, entry):
        ## get the text in col order
        tmp = []
        for i in range(self.GetColumnCount()):
            name = self.mapColAttributes[i]
            tmp.append(entry[name])

        rowIndex = self.Append(tmp)

        if 'validity' in entry:
            validity = entry['validity']

            if validity == 'local':
                color = wx.Colour('green')
            elif validity == 'localError':
                color = wx.Colour('red')
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

        item = self.popupmenu.Append(self.ID_CONTEXTUAL_UNCHECKED, 'Unchecked')
        self.Bind(wx.EVT_MENU, self.OnSelectPop, item)

        self.PopupMenu(self.popupmenu, event.GetPoint())
        self.popupmenu.Destroy()

    def OnSelectPop(self, event):
        checked = True
        itemId = event.GetId()
        if itemId == self.ID_CONTEXTUAL_CHECKED: # checked the selection
            checked = True
        elif itemId == self.ID_CONTEXTUAL_UNCHECKED: # uncheck the selection
            checked = False
        else:
            return
        #item = self.popupmenu.FindItemById(itemId)
        #text = item.GetText()
        selectedEntries = self.GetSelectedEntries()
        for selectedEntry in selectedEntries:
            self.CheckItem(selectedEntry, checked)

class UIToolbarButton(wx.BitmapButton):
    def __init__(self, parent, command, image, tooltip):
        print 'image', image
        self.buttonImage = wx.Image(name = image)
        self.buttonBitmap =  self.buttonImage.ConvertToBitmap()
        
        wx.BitmapButton.__init__(self, parent, bitmap = self.buttonBitmap)

        self.Bind(wx.EVT_BUTTON, command)
        self.SetToolTip(tooltip)
        
class UIToolBar(wx.BoxSizer):
    def __init__(self, parent, description):
        wx.BoxSizer.__init__(self, orient = wx.HORIZONTAL)
        
        buttonFlags = wx.SizerFlags(0)
        for buttonData in description:
            command = buttonData['command']
            image = buttonData['image']
            tooltip = buttonData['tooltip']
            
            tbButton = UIToolbarButton(parent, command, image, tooltip)
            self.Add(tbButton, buttonFlags)
            
        self.sizerFlags = wx.SizerFlags(0)
        
    def GetSizerFlags(self):
        return self.sizerFlags

class PkgFilesView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        ## create the toolbar toolbar
        #~ description = [ \
            #~ {'command': self.FillValues, 'image': 'resources/view-refresh.png', 'tooltip': 'Refresh local Pkgs information'}, \
            #~ {'command': self.ClearValues, 'image': 'resources/edit-clear.png', 'tooltip': 'Clear local Pkgs information'}, \
            #~ {'command': self.Rename, 'image': 'resources/edit-copy.png', 'tooltip': 'Clear local Pkgs information'} \
            #~ ]
        description = [ \
            {'command': self.FillValues, 'image': 'resources/view-refresh.png', 'tooltip': 'Refresh local Pkgs information'}, \
            {'command': self.ClearValues, 'image': 'resources/edit-clear.png', 'tooltip': 'Clear local Pkgs information'}, \
            {'command': self.Rename, 'image': 'resources/edit-clear.png', 'tooltip': 'Rename selected Pkg files'}, \
            {'command': self.DownloadPkg, 'image': 'resources/edit-clear.png', 'tooltip': 'Download selected Pkg files'} \
            ]

        self.toolbar = UIToolBar(self, description)
                
        ## create the tree view
        self.listCtrl = UIListCtrl(self, 'PkgFile')
        
        ## main sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.toolbar, self.toolbar.GetSizerFlags())
        mainSizer.Add(self.listCtrl, self.listCtrl.GetSizerFlags())

        self.SetSizerAndFit(mainSizer)

    def Rename(self, event = ''):
        checkedEntries = self.listCtrl.GetCheckEntries()
        for checkedEntry in checkedEntries:
            filename = self.listCtrl.GetEntryText(checkedEntry, 'filename')
            API.Send('RenamePkgFile', filename)
        
        
    def ClearValues(self, event = ''):
        self.listCtrl.RemoveValues()
        
    def FillValues(self, event = ''):
        self.ClearValues()
        
        API.Send('RefreshPkgsData')
        pkgsData = API.Send('GetPkgsData')

        for pkgData in pkgsData:                
            self.listCtrl.AddEntry(pkgData)

    def DownloadPkg(self, event = ''):
        checkedEntries = self.listCtrl.GetCheckEntries()
        for checkedEntry in checkedEntries:
            filename = self.listCtrl.GetEntryText(checkedEntry, 'filename')
            downloadURL = self.listCtrl.GetEntryText(checkedEntry, 'downloadURL')
            if downloadURL != "":
                API.Send('DownloadPkg', downloadURL, filename)
        
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
        self.pkgDownloadFile = wx.FilePickerCtrl(self, message = 'Select the download Pkg File')
        self.pkgDownloadFile.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSetDownloadFile)

        text1 = wx.StaticText(self, label = 'Pkg Directory') 
        text2 = wx.StaticText(self, label = 'Vita Directory') 
        text3 = wx.StaticText(self, label = 'Pkg Download File')

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
        
        pkgDownloadFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        pkgDownloadFileSizer.Add(text3, textFlags)
        pkgDownloadFileSizer.Add(self.pkgDownloadFile, browserFlags)
        
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
        mainSizer.Add(pkgDownloadFileSizer, mixFlags)
        mainSizer.Add(buttonSizer, 0, wx.LEFT, 0)

        self.SetSizerAndFit(mainSizer)
        
    def FillValues(self):
        pkgDirectory = API.Send('GetPkgDirectory')
        self.pkgDirectory.SetPath(pkgDirectory)

        vitaDirectory = API.Send('GetVitaDirectory')
        self.vitaDirectory.SetPath(vitaDirectory)

        downloadFile = API.Send('GetDownloadFile')
        self.pkgDownloadFile.SetPath(downloadFile)
        
    def OnResetIni(self, event):
        pkgDirectory = API.Send('GetIniValue', 'pkgDirectory')
        self.pkgDirectory.SetPath(pkgDirectory)

        vitaDirectory = API.Send('GetIniValue', 'vitaDirectory')
        self.vitaDirectory.SetPath(vitaDirectory)

        downloadFile = API.Send('GetIniValue', 'pkgDownloadFile')
        self.pkgDownloadFile.SetPath(downloadFile)
        
    def OnSaveIni(self, event):
        ## set the new values
        pkgDirectory = self.pkgDirectory.GetPath()
        API.Send('SetIniValue', 'pkgDirectory', pkgDirectory)
        
        pkgDownloadFile = self.pkgDownloadFile.GetPath()
        API.Send('SetIniValue', 'pkgDownloadFile', pkgDownloadFile)
        
        vitaDirectory = self.vitaDirectory.GetPath()
        API.Send('SetIniValue', 'vitaDirectory', vitaDirectory)
        
        ## serialize the ini values
        API.Send('SerializeIni')

    def OnReset(self, event):
        self.FillIniValues()
        
    def OnSetPkgDir(self, event):
        pkgDirectory = self.pkgDirectory.GetPath()
        API.Send('SetPkgDirectory', pkgDirectory)
        #API.Send('SetIniValue', 'pkgDirectory', pkgDirectory)
        
    def OnSetVitaDir(self, event):
        vitaDirectory = self.vitaDirectory.GetPath()
        API.Send('SetVitaDirectory', vitaDirectory)
        #API.Send('SetIniValue', 'vitaDirectory', vitaDirectory)
        
    def OnSetDownloadFile(self, event):
        pkgDownloadFile = self.pkgDownloadFile.GetPath()
        API.Send('SetDownloadFile', pkgDownloadFile)
        #API.Send('SetIniValue', 'pkgDownloadFile', pkgDownloadFile)
