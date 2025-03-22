from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
import os
import sys
import json
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)
        
        back_btn = QAction("Back", self)
        back_btn.setStatusTip("Go Back to Last Page")
        back_btn.triggered.connect(self.navigate_back)
        navtb.addAction(back_btn)
        
        next_btn = QAction("Forward", self)
        next_btn.setStatusTip("Forward to next Page")
        next_btn.triggered.connect(self.navigate_forward)
        navtb.addAction(next_btn)

        reload_btn = QAction("Reload", self)
        reload_btn.setStatusTip("Refresh Page")
        reload_btn.triggered.connect(lambda:self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction("Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)

        navtb.addAction(home_btn)
        navtb.addSeparator()
        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction("Stop", self)
        stop_btn.setStatusTip("Stop loading")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        history_btn = QAction("History", self)
        history_btn.setStatusTip("View History")
        history_btn.triggered.connect(self.show_history)
        navtb.addAction(history_btn)

        self.load_history()
        self.add_new_tab(QUrl('https://www.google.com'), 'Homepage')
        self.show()
        self.setWindowTitle("Lawrence Connected")

        # Connect close event to save history
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.destroyed.connect(self.save_history)

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl('https://www.google.com')
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))
        browser.urlChanged.connect(self.update_history)

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_url(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        text = self.urlbar.text()
        if not text.startswith(('http://', 'https://')):
            
            # Assume it's a search query
            query = text.replace(' ', '+')
            url = f"https://www.google.com/search?q={query}"
            
        elif not text.endswith(('.com', '.net', '.org', '.gov', '.co', '.uk', '.edu')):
            query = text.replace(' ', '+')
            url = f"https://www.google.com/search?q={query}"
        else:
            url = text
        q = QUrl(url)
        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(len(q.toString()))

    def update_history(self, q):
        url_str = q.toString()
        if self.history_index != -1:
            # Clear forward history if a new page is loaded
            self.history = self.history[:self.history_index + 1]
        if not self.history or self.history[-1]['url'] != url_str:
            title = self.tabs.currentWidget().page().title()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.history.append({'url': url_str, 'title': title, 'time': timestamp})
            self.history_index += 1

    def update_url(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.update_urlbar(q, browser)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = browser.page().title()
        if title:
            self.setWindowTitle(f"{title} - Lawrence Connected")
        else:
            self.setWindowTitle("Lawrence Connected")

    def navigate_back(self):
        self.tabs.currentWidget().back()
        self.update_history_index(-1)

    def navigate_forward(self):
        self.tabs.currentWidget().forward()
        self.update_history_index(1)

    def update_history_index(self, step):
        self.history_index += step
        if 0 <= self.history_index < len(self.history):
            self.tabs.currentWidget().setUrl(QUrl(self.history[self.history_index]['url']))

    def show_history(self):
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("History")
        layout = QVBoxLayout()

        history_list = QListWidget()
        for item in self.history:
            timestamp = item['time']
            title = item['title']
            url = item['url']
            display_text = f"{timestamp} - {title} ({url})"
            history_list.addItem(display_text)
        history_list.itemClicked.connect(self.history_item_clicked)
        layout.addWidget(history_list)

        history_dialog.setLayout(layout)
        history_dialog.exec_()

    def history_item_clicked(self, item):
        display_text = item.text()
        url = display_text.split('(', 1)[1].rstrip(')')
        self.tabs.currentWidget().setUrl(QUrl(url))
        self.history_index = next(i for i, h in enumerate(self.history) if h['url'] == url)

    def load_history(self):
        history_file = 'history.json'
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                self.history = json.load(f)
        else:
            self.history = []
        self.history_index = -1

    def save_history(self):
        history_file = 'history.json'
        with open(history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("Lawrence Connected")
    window = MainWindow()
    app.exec_()
