#!/usr/bin/env python2
try:
    import os
    import wx
    from pkgManagerCtrl import PkgCtrl
    
    from wx.lib.mixins.listctrl import ColumnSorterMixin, ListCtrlAutoWidthMixin
except ImportError:
    assert False, "import error in pkgManagerUI"
    
class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(800,400))
        
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        # Setting up the menu.
        fileMenu = wx.Menu()
        menuExit = fileMenu.Append(wx.ID_EXIT,"E&xit"," Close Pkg Manager")

        ## edit menu
        editMenu = wx.Menu()
        menuConfiguration = editMenu.Append(0,"Settings"," Settings")

        ## tools menu
        toolsMenu = wx.Menu()
        menuTools = toolsMenu.Append(1,"Rename All"," rename all pkg")
        menuTools = toolsMenu.Append(2,"Download All"," download all pkg")


        # other menu
        otherMenu = wx.Menu()
        menuAbout = otherMenu.Append(wx.ID_ABOUT, "&About"," Information about Pkg Manager")
        
        # Creating the menubar.
        menuBar = wx.MenuBar()

        ## adding menu to the menu bar
        menuBar.Append(fileMenu,"&File")
        menuBar.Append(menuTools,"&Tools")
        menuBar.Append(editMenu,"&Edit")
        menuBar.Append(otherMenu,"&?")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Show(True)

    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Pkg Manager 0.1", "About Pkg Manager", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.

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
        self.AppendColumn('Type')
        self.AppendColumn('Name')
        self.AppendColumn('Region')
        self.AppendColumn('Filename')
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
                wx.EXPAND |  # make horizontally stretchable
                wx.ALL,      # and make border all around
                0)

        self.SetSizerAndFit(mainSizer)

    def AddPkg(self, entry):
        self.listCtrl.AddEntry(entry)

    def PopulateInfo(self):
        pkgsData = pkgCtrl.GetLocalPkgsData()

        for pkgData in pkgsData:
            self.AddPkg(pkgData)
        
class VitaFiles(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.listCtrl = VitaView(self)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(
                self.listCtrl,
                1,           # make vertically stretchable
                wx.EXPAND |  # make horizontally stretchable
                wx.ALL,      # and make border all around
                0)

        self.SetSizerAndFit(mainSizer)

    def AddFile(self, entry):
        self.listCtrl.AddEntry(entry)
        
## initialize the controllers
pkgCtrl = PkgCtrl('E:\psvita (nonpdrm)\gamePkg')

app = wx.App(False)

mainFrame = MainFrame(None, title="Pkg Manager")
nb = wx.Notebook(mainFrame)

panelPkg = PkgFiles(nb)
panelVita = VitaFiles(nb)

nb.AddPage(panelPkg, "Pkg Files")
nb.AddPage(panelVita, "Vita Files")

mainFrame.Show()

#panelPkg.AddPkg(['PCBS00000', 'Game', 'truc', 'EU', 'zeus',  '012413412314'])
panelPkg.PopulateInfo()

app.MainLoop()

