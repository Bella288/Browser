from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import sys

class MainWindow(QMainWindow):
  def __init__(self, *args, **kwargs):
    super(MainWindow, self).__init__(*args, **kwargs)

    # creating a QWebEngineView
    self.browser = QWebEngineView()
    # set def browser url to google
    self.browser.setUrl(QUrl("https://google.com"))
    # add action for when url changed
    self.browser.urlChanged.connect(self.update_urlbar)
    # add action for when loading is finished
    self.browser.loadFinished.connect(self.update_title)
    # set this browser as central wid. or main window
    self.setCentralWidget(self.browser)
    # create stat. bar obj
    self.status = QtStatusBar()
    # add stat. bar to main win.
    self.setStatusBar(self.status)
    # add QToolBar for Nav.
    navtb = QToolBar("Navigation")
    #add this tool bar to main window
    self.addToolBar(navtb)
    # adding actions to the tool bar
    # creating a action for back
    back_btn = QAction("Back", self)
    # add stat. tip
    back_btn.setStatusTip("Back to previous page")
    # adding action to the back button
    # making browser go back
    back_btn.triggered.connect(self.browser.back)
    # add this action to tb
    navtb.addAction(back_btn)
    next_btn = QAction("Forward", self)
    next_btn.setStatusTip("Forward to next page")
    next_btn.triggered.connect(self.browser.forward)
    navtb.addAction(next_btn)
    reload_btn = QAction("Reload", self)
    reload_btn.setStatusTip("Reload Page")
    reload_btn.trigger.connect(self.browser.reload)
    navtb.addAction(reload_btn)
    navtb.addSeparator()
    self.urlbar = QLineEdit()
    self.urlbar.returnPressed.connect(self.navigate_to_url)
    navtb.addWidget(self.urlbar)
    stop_btn = QAction("Stop", self)
    stop_btn.setStatusTip("Stop loading")
    stop_btn.triggered.connect(self.browser.stop)
    navtb.addAction(stop_btn)
    self.show
  def update_title(self):
    title = self.browser.page().title()
    self.setWindowTitle("%s - Lawrence Connected" % title)
  def navigate_home(self):
    self.browser.setUrl(QUrl("https://google.com"))
  def navigate_to_url(self):
    q = QUrl(self.urlbar.text())
    if q.scheme() == "":
      q.setScheme("http")
    self.browser.setUrl(q)
  def update_urlbar(self, q):
    self.urlbar.setText(q.toString())
    self.urlbar.setCursorPosition(0)
app = QApplication(sys.argv)
app.setApplicationName("Lawrence Connected")
window = MainWindow()

app.exec_()
