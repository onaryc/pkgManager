#!/usr/bin/env python2
try:
    ## python module
    import os

    ## wx python module
    import wx
    from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin
    import wx.lib.newevent

    ## custom module
    from pkgManagerCtrl import PkgCtrl, VitaCtrl, IniCtrl, MessageCtrl
    #import pkgManagerCtrl
except ImportError:
    assert False, "import error in pkgManagerUI"

ID_MENU_SETTINGS = wx.NewId()
ID_MENU_RENAME_ALL = wx.NewId()
ID_MENU_DOWNLOAD_ALL = wx.NewId()

ID_BUTTON_SAVE_INI = wx.NewId()
ID_BUTTON_RESET_INI = wx.NewId()

#SendMessage, EVT_SEND_MESSAGE = wx.lib.newevent.NewEvent()

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,400))
        
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

        self.notebook = wx.Notebook(self)

        self.panelPkg = PkgFiles(self.notebook)
        self.panelVita = VitaFiles(self.notebook)
        self.panelSettings = AppSettings(self.notebook)

        self.notebook.AddPage(self.panelPkg, "Pkg Files")
        self.notebook.AddPage(self.panelVita, "Vita Files")
        self.notebook.AddPage(self.panelSettings, "Settings")

        ## for testing purpose shall be call with a button
        self.panelPkg.PopulateInfo()
        
        self.Show(True)

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Pkg Manager 0.1", "About Pkg Manager", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnExit(self,e):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
            #self.Close(True)

    def Print(self, code, message):
        print 'Print', code, message
        self.statusBar.SetStatusText(message, 0) 

class UIView(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, size=(-1, -1), style=wx.LC_REPORT|wx.LC_SINGLE_SEL)

        ListCtrlAutoWidthMixin.__init__(self)

    def AddEntry(self, entry):
        self.Append(entry)

class PkgView(UIView):
    def __init__(self, parent):
        UIView.__init__(self, parent)

        self.AppendColumn('Title ID')
        self.AppendColumn('Type') # game, update or DLC
        self.AppendColumn('Name')
        self.AppendColumn('Region')
        self.AppendColumn('Filename')
        self.AppendColumn('FW Version')
        self.AppendColumn('Url')
        self.AppendColumn('zRIF')

class VitaView(UIView):
    def __init__(self, parent):
        UIView.__init__(self, parent)

        self.AppendColumn('Title ID')
        self.AppendColumn('Type')
        self.AppendColumn('Name')
        self.AppendColumn('Region')
        self.AppendColumn('Directory')
        
class PkgFiles(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.listCtrl = PkgView(self)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(
                self.listCtrl,
                1,           # make vertically stretchable
                wx.EXPAND |  wx.ALL, # make horizontally stretchable and make border all around
                0)

        self.SetSizerAndFit(mainSizer)

    def PopulateInfo(self):
        pkgsData, code, message = pkgCtrl.GetLocalPkgsData()

        messageCtrl.ManageMessage(code, message)

        for pkgData in pkgsData:
            self.listCtrl.AddEntry(entry)
        
class VitaFiles(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.listCtrl = VitaView(self)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(
                self.listCtrl,
                1,           # make vertically stretchable
                wx.EXPAND |  wx.ALL, # make horizontally stretchable and make border all around
                0)

        self.SetSizerAndFit(mainSizer)
        
class AppSettings(wx.Panel):
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
        browserFlags.Align(wx.ALIGN_RIGHT).Expand().Border(wx.ALL, 0)
        
        mixFlags = wx.SizerFlags(0)
        mixFlags.Expand().Border(wx.ALL, 0)

        pkgDirectorySizer = wx.BoxSizer(wx.HORIZONTAL)
        pkgDirectorySizer.Add(text1, textFlags)
        pkgDirectorySizer.Add(self.pkgDirectory, browserFlags)
        
        vitaDirectorySizer = wx.BoxSizer(wx.HORIZONTAL)
        vitaDirectorySizer.Add(text2, textFlags)
        vitaDirectorySizer.Add(self.vitaDirectory, browserFlags)
        
        pkgDownloadFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        pkgDownloadFileSizer.Add(text3, textFlags)
        pkgDownloadFileSizer.Add(self.pkgDownloadFile, browserFlags)
        
        ## init the values from the ctrl
        self.InitValues()
        
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

    def InitValues(self):
        pkgDirectory = pkgCtrl.GetDirectory()
        self.pkgDirectory.SetPath(pkgDirectory)

        vitaDirectory = vitaCtrl.GetDirectory()
        self.vitaDirectory.SetPath(vitaDirectory)

        downloadFile = pkgCtrl.GetDownloadFile()
        self.pkgDownloadFile.SetPath(downloadFile)
        
    def OnSaveIni(self, event):
        ## set the new values
        pkgDirectory = self.pkgDirectory.GetPath()
        iniCtrl.SetValues('pkgDirectory', pkgDirectory)
        
        pkgDownloadFile = self.pkgDownloadFile.GetPath()
        iniCtrl.SetValues('pkgDownloadFile', pkgDownloadFile)
        
        vitaDirectory = self.vitaDirectory.GetPath()
        iniCtrl.SetValues('vitaDirectory', vitaDirectory)
        
        ## serialize the ini values
        code, message = iniCtrl.SerializeIni()
        messageCtrl.ManageMessage(code, message)

    def OnReset(self, event):
        self.InitValues()
        
## initialize the controllers
messageCtrl = MessageCtrl(ui = 'stdout') ## message displaid on the stdout

iniCtrl = IniCtrl('pkgManager.ini')
code, message = iniCtrl.ParseIni()
messageCtrl.ManageMessage(code, message)

pkgCtrl = PkgCtrl(iniCtrl.GetValue('pkgDirectory'), iniCtrl.GetValue('pkgDownloadFile'))
vitaCtrl = VitaCtrl(iniCtrl.GetValue('vitaDirectory'))

## initialize the UI
app = wx.App(False)

mainFrame = MainFrame(None, title="Pkg Manager")
messageCtrl.SetUI(mainFrame) ## message shall be displaid through the ui now

#mainFrame.Show()

app.MainLoop()

