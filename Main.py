import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from MainWindow import *
import MultiBrowser


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.frame.hide()
        self.frame_NewTask.hide()
        self.frame_BrowserAction.hide()
        self.lineEdit_IP.setInputMask("000.000.000.000:00000;")
        self.tableWidget_Proxy.setColumnCount(6)
        self.tableWidget_Proxy.setHorizontalHeaderLabels([' ', 'IP', 'Username', 'Password', 'Status', 'Ping'])
        self.tableWidget_Profile.setColumnCount(3)
        self.tableWidget_Profile.setHorizontalHeaderLabels(['Name', 'Email', 'Actions'])
        self.tableWidget_Task.setColumnCount(7)
        self.tableWidget_Task.setHorizontalHeaderLabels([' ', 'Store', 'Product', 'Size', 'Proxy', 'Profile', 'Status'])

        with open("Proxies.txt", 'r') as p:
            self.proxies = p.readlines()
        self.tableWidget_Proxy.setRowCount(len(self.proxies))
        for i in range(len(self.proxies)):
            proxy = self.proxies[i].rstrip("\n")
            if "|" in proxy:
                ip = proxy.split("|")[0]
                username = proxy.split("|")[1].split(":")[0]
                password = proxy.split("|")[1].split(":")[1]
            else:
                ip = proxy
                username = ""
                password = ""
            item_checked = QTableWidgetItem()
            item_checked.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item_checked.setCheckState(Qt.Unchecked)
            item_ip = QTableWidgetItem(ip)
            item_username = QTableWidgetItem(username)
            item_password = QTableWidgetItem(password)
            self.tableWidget_Proxy.setItem(i, 0, item_checked)
            self.tableWidget_Proxy.setItem(i, 1, item_ip)
            self.tableWidget_Proxy.setItem(i, 2, item_username)
            self.tableWidget_Proxy.setItem(i, 3, item_password)
        p.close()

        global tasks

        self.pushButton_Add_Proxy.clicked.connect(self.single_proxy_add)
        self.pushButton_Delete_Proxy.clicked.connect(self.delete_proxy)
        self.pushButton_NewTask.clicked.connect(self.frame_NewTask.show)
        self.pushButton_Cancel_BrowserTask.clicked.connect(self.frame_NewTask.hide)
        self.pushButton_NewProfile.clicked.connect(self.frame.show)
        self.pushButton_Cancel_Profile.clicked.connect(self.frame.hide)
        self.checkBox_All_Proxies.clicked['bool'].connect(self.select_all_proxies)
        self.pushButton_Add_BrowserTask.clicked.connect(self.add_browser_task)
        self.checkBox_All_Tasks.clicked['bool'].connect(self.select_all_tasks)
        self.pushButton_Delete_Task.clicked.connect(self.delete_task)
        self.pushButton_Start_Tasks.clicked.connect(self.start_task)
        self.pushButton_Stop_Tasks.clicked.connect(self.stop_task)
        #self.pushButton_Delete_Task.clicked.connect(self.open_browser)
        self.pushButton_Browser_Refresh.clicked.connect(self.browser_refresh)
        self.pushButton_Browser_Back.clicked.connect(self.browser_back)
        self.pushButton_Browser_Forward.clicked.connect(self.browser_forward)
        self.pushButton_Goto_NewUrl.clicked.connect(self.goto_new_url)

        self.proxy_list_update()

    def single_proxy_add(self):
        row = self.tableWidget_Proxy.rowCount()
        self.tableWidget_Proxy.setRowCount(row + 1)
        ip = self.lineEdit_IP.text()
        username = self.lineEdit_Username.text()
        password = self.lineEdit_Password.text()
        item_checked = QTableWidgetItem()
        item_checked.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item_checked.setCheckState(Qt.Unchecked)
        item_ip = QTableWidgetItem(ip)
        item_username = QTableWidgetItem(username)
        item_password = QTableWidgetItem(password)
        self.tableWidget_Proxy.setItem(row, 0, item_checked)
        self.tableWidget_Proxy.setItem(row, 1, item_ip)
        self.tableWidget_Proxy.setItem(row, 2, item_username)
        self.tableWidget_Proxy.setItem(row, 3, item_password)
        if username == "" and password == "":
            proxy = ip+"\n"
        else:
            proxy = "{}|{}:{}\n".format(ip, username, password)
        self.proxies.append(proxy)
        with open("Proxies.txt", 'a') as p:
            p.write(proxy)
        p.close()
        self.proxy_list_update()

    def select_all_proxies(self, checked):
        if checked:
            checked_status = Qt.Checked
        else:
            checked_status = Qt.Unchecked
        for i in range(self.tableWidget_Proxy.rowCount()):
            self.tableWidget_Proxy.item(i, 0).setCheckState(checked_status)

    def delete_proxy(self):
        for i in range(self.tableWidget_Proxy.rowCount()-1, -1, -1):
            if self.tableWidget_Proxy.item(i, 0).checkState() == Qt.Checked:
                self.tableWidget_Proxy.removeRow(i)
                del self.proxies[i]
        with open("Proxies.txt", 'w') as p:
            p.writelines(self.proxies)
        p.close()
        self.proxy_list_update()

    def test_proxy(self):
        for i in range(self.tableWidget_Proxy.rowCount()):
            if self.tableWidget_Proxy.item(i, 0).checkState() == Qt.Checked:
                proxy = self.proxies[i]
        pass

    def proxy_list_update(self):
        proxies = []
        for proxy in self.proxies:
            proxies.append(proxy.rstrip("\n"))
        self.comboBox_BrowserProxy.clear()
        self.comboBox_BrowserProxy.addItem("Host")
        self.comboBox_BrowserProxy.addItems(proxies)
        pass

    def profile_add(self):
        row = self.tableWidget_Proxy.rowCount()
        self.tableWidget_Proxy.setRowCount(row + 1)

    def add_browser_task(self):
        proxy = self.comboBox_BrowserProxy.currentText()
        url = self.lineEdit_BrowserUrl.text()
        num = self.spinBox_BrowserNum.value()
        for i in range(num):
            task = {"mode": "browser", "url": url, "proxy": proxy, "status": "stopped"}
            tasks.append(task)
            row = self.tableWidget_Task.rowCount()
            self.tableWidget_Task.setRowCount(row + 1)
            item_checked = QTableWidgetItem()
            item_checked.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item_checked.setCheckState(Qt.Unchecked)
            item_store = QTableWidgetItem(url)
            item_proxy = QTableWidgetItem(proxy)
            self.tableWidget_Task.setItem(row, 0, item_checked)
            self.tableWidget_Task.setItem(row, 1, item_store)
            self.tableWidget_Task.setItem(row, 4, item_proxy)
        pass

    def select_all_tasks(self, checked):
        if checked:
            checked_status = Qt.Checked
        else:
            checked_status = Qt.Unchecked
        for i in range(self.tableWidget_Task.rowCount()):
            self.tableWidget_Task.item(i, 0).setCheckState(checked_status)

    def delete_task(self):
        for i in range(self.tableWidget_Task.rowCount()-1, -1, -1):
            if (self.tableWidget_Task.item(i, 0).checkState() == Qt.Checked) and (tasks[i]["status"] == "stopped"):
                self.tableWidget_Task.removeRow(i)
                del tasks[i]

    def start_task(self):
        for i in range(self.tableWidget_Task.rowCount()):
            if self.tableWidget_Task.item(i, 0).checkState() == Qt.Checked:
                if tasks[i]["mode"] == "browser":
                    url = tasks[i]["url"]
                    proxy = self.comboBox_BrowserProxy.currentText()
                    tasks[i]["Thread"] = MultiBrowser.BrowserThread(url, proxy, i)
                    tasks[i]["Thread"].browser_status_change.connect(self.task_status_change)
                    tasks[i]["Thread"].start()
                    if self.frame_BrowserAction.isHidden():
                        self.frame_BrowserAction.show()
                pass
        self.frame_NewTask.hide()

    def stop_task(self):
        for i in range(self.tableWidget_Task.rowCount()):
            if (self.tableWidget_Task.item(i, 0).checkState() == Qt.Checked) and (tasks[i]["status"] == "running"):
                if tasks[i]["mode"] == "browser":
                    tasks[i]["Thread"].browser.quit()
                    del tasks[i]["Thread"]
                    self.task_status_change(i, "stopped")
                    pass

    def browser_refresh(self):
        for i in range(self.tableWidget_Task.rowCount()):
            if self.tableWidget_Task.item(i, 0).checkState() == Qt.Checked:
                if tasks[i]["mode"] == "browser":
                    tasks[i]["Thread"].action = "refresh"
                    tasks[i]["Thread"].start()

    def browser_back(self):
        for i in range(self.tableWidget_Task.rowCount()):
            if self.tableWidget_Task.item(i, 0).checkState() == Qt.Checked:
                if tasks[i]["mode"] == "browser":
                    tasks[i]["Thread"].action = "back"
                    tasks[i]["Thread"].start()

    def browser_forward(self):
        for i in range(self.tableWidget_Task.rowCount()):
            if self.tableWidget_Task.item(i, 0).checkState() == Qt.Checked:
                if tasks[i]["mode"] == "browser":
                    tasks[i]["Thread"].action = "forward"
                    tasks[i]["Thread"].start()

    def browser_set_position(self):
        num = 0
        for i in range(self.tableWidget_Task.rowCount()):
            if (self.tableWidget_Task.item(i, 0).checkState() == Qt.Checked) and (tasks[i]["status"] == "running") and (tasks[i]["mode"] == "browser"):
                num += 1

    def goto_new_url(self):
        url = self.lineEdit_NewUrl.text()
        for i in range(self.tableWidget_Task.rowCount()):
            if self.tableWidget_Task.item(i, 0).checkState() == Qt.Checked:
                if tasks[i]["mode"] == "browser":
                    tasks[i]["Thread"].action = "get"
                    tasks[i]["Thread"].url = url
                    tasks[i]["Thread"].start()

    def task_status_change(self, serial_number, task_status):
        item_status = QTableWidgetItem(task_status)
        self.tableWidget_Task.setItem(serial_number, 6, item_status)
        tasks[serial_number]["status"] = task_status


class MonitorThread(QThread):

    browser_status_change = pyqtSignal(int, str)

    def __init__(self):
        super(MonitorThread, self).__init__()
        global tasks

    def run(self):
        while True:
            for i in range(len(tasks)):
                task = tasks[i]
                if (task["mode"] == "browser") and (task["status"] == "running"):
                    try:
                        task["Thread"].browser.current_url
                    except:
                        try:
                            del task["Thread"]
                        finally:
                            task["status"] = "stopped"
                            self.browser_status_change.emit(i, "stopped")
                        #print(str(i)+"stopped")


if __name__ == "__main__":
    tasks = []
    monitor = MonitorThread()
    monitor.start()
    app = QApplication(sys.argv)
    ui = MainWindow()
    monitor.browser_status_change.connect(ui.task_status_change)
    ui.show()
    sys.exit(app.exec())
