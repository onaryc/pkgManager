#!/usr/bin/env python2
try:
    ## python module
    import os

    ## wx python module
    import wx
    from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin
    import wx.lib.newevent
    
    import APICtrl as API
    from MessageTools import DPrint
except ImportError:
    assert False, "import error in pkgManagerUI"

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
        editMenu = wx.Menu()
        menuConfiguration = editMenu.Append(ID_MENU_SETTINGS,"Settings"," Settings")

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
        menuBar.Append(editMenu,"&Edit")
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

class UIListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent, className):
        wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT|wx.LC_SINGLE_SEL)

        ListCtrlAutoWidthMixin.__init__(self)

        ## add the column based on the data model attributes
        attributes = API.Send('GetModelAttributes', className)
        for attribute in attributes:
            if 'display' in attribute:
                displayName = attribute['display']
            else:
                displayName = attribute['name']

            self.AppendColumn(displayName)

    def RemoveValues(self):
        self.DeleteAllItems()
        
    def AddEntry(self, entry):
        self.Append(entry)

class UIToolbarButton(wx.BitmapButton):
    def __init__(self, parent, command, image, tooltip):
        buttonImage = wx.Image(name = image)
        buttonBitmap =  buttonImage.ConvertToBitmap()
        
        wx.BitmapButton.__init__(self, parent, id = ID_BUTTON_REFRESH_PKG, bitmap = buttonBitmap)

        self.Bind(wx.EVT_BUTTON, command)
        self.SetToolTip(tooltip)

class PkgFilesView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        ## create the toolbar toolbar
        self.refreshButton = UIToolbarButton(self, self.FillValues, 'resources/view-refresh.png', 'Refresh local Pkgs information')
        self.clearButton = UIToolbarButton(self, self.ClearValues, 'resources/edit-clear.png', 'Clear local Pkgs information')

        # toolbar sizer
        buttonFlags = wx.SizerFlags(0)
        #buttonFlags.Expand()
        toolbarFlags = wx.SizerFlags(0)
        toolbarFlags.Expand()
        toolbarSizer = wx.BoxSizer(wx.HORIZONTAL)
        toolbarSizer.Add(self.refreshButton, buttonFlags)
        toolbarSizer.Add(self.clearButton, buttonFlags)
        
        ## create the tree view
        self.listCtrl = UIListCtrl(self, 'PkgFile')

        ## main sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(toolbarSizer, toolbarFlags)
        mainSizer.Add(
                self.listCtrl,
                1,           # make vertically stretchable
                wx.EXPAND |  wx.ALL, # make horizontally stretchable and make border all around
                0)

        self.SetSizerAndFit(mainSizer)

    def ClearValues(self, event = ''):
        self.listCtrl.RemoveValues()
        
    def FillValues(self, event = ''):
        self.ClearValues()
        
        pkgsData = API.Send('GetLocalPkgsData')
        
        for pkgData in pkgsData:
            self.listCtrl.AddEntry(pkgData)
        
class VitaFilesView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.listCtrl = UIListCtrl(self, 'VitaFile')

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(
                self.listCtrl,
                1,           # make vertically stretchable
                wx.EXPAND |  wx.ALL, # make horizontally stretchable and make border all around
                0)

        self.SetSizerAndFit(mainSizer)

    def FillValues(self):
        vitaData = API.Send('GetLocalVitaData')
        
        for data in vitaData:
            self.listCtrl.AddEntry(data)
        
class SettingsView(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        ## file/directory browsers definition and sizer
        self.pkgDirectory = wx.DirPickerCtrl(self, style = wx.DIRP_DEFAULT_STYLE|wx.DIRP_DIR_MUST_EXIST, message = 'Select the Pkg Directory')
        self.vitaDirectory = wx.DirPickerCtrl(self, style = wx.DIRP_DEFAULT_STYLE|wx.DIRP_DIR_MUST_EXIST, message = 'Select the vita Directory')
        self.pkgDownloadFile = wx.FilePickerCtrl(self, message = 'Select the download Pkg File')

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

        self.resetButton = wx.Button(self, id = ID_BUTTON_RESET_INI, label='Reset Values')
        self.resetButton.Bind(wx.EVT_BUTTON, self.OnReset)

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
        global ui

        pkgDirectory = API.Send('GetPkgDirectory')
        self.pkgDirectory.SetPath(pkgDirectory)

        vitaDirectory = API.Send('GetVitaDirectory')
        self.vitaDirectory.SetPath(vitaDirectory)

        downloadFile = API.Send('GetDownloadFile')
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
        self.InitValues()
