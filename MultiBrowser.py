from selenium import webdriver
from PyQt5.QtCore import QThread, pyqtSignal
import zipfile
import json


class BrowserThread(QThread):

    browser_status_change = pyqtSignal(int, str)

    def __init__(self, url, proxy, serial_number):
        super(BrowserThread, self).__init__()
        self.action = "get"
        self.serial_number = serial_number
        self.url = url
        self.option = webdriver.ChromeOptions()
        self.option.add_experimental_option("detach", True)
        self.option.add_experimental_option('excludeSwitches', ['enable-automation'])
        if proxy != "Host":
            self.set_proxy(proxy)
        self.browser = webdriver.Chrome(options=self.option)

    def run(self):
        if self.action == "get":
            self.browser.get(self.url)
            self.browser_status_change.emit(self.serial_number, "running")
        elif self.action == "refresh":
            self.browser.refresh()
        elif self.action == "back":
            self.browser.back()
        elif self.action == "forward":
            self.browser.forward()

    def set_proxy(self, proxy):
        if "|" in proxy:
            ip = proxy.split(":")[0]
            port = proxy.split(":")[1].split("|")[0]
            username = proxy.split("|")[1].split(":")[0]
            password = proxy.split("|")[1].split(":")[1]
            manifest_json = """
            {
                "version": "1.0.0",
                "manifest_version": 2,
                "name": "Chrome Proxy",
                "permissions": [
                    "proxy",
                    "tabs",
                    "unlimitedStorage",
                    "storage",
                    "<all_urls>",
                    "webRequest",
                    "webRequestBlocking"
                ],
                "background": {
                    "scripts": ["background.js"]
                }
            }
            """

            background_js = """
            var config = {
                    mode: "fixed_servers",
                    rules: {
                      singleProxy: {
                        scheme: "http",
                        host: "%(ip)s",
                        port: %(port)s
                      }
                    }
                };

            chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

            function callbackFn(details) {
                return {
                    authCredentials: {
                      username: "%(username)s",
                      password: "%(password)s"
                    }
                }
            }

            chrome.webRequest.onAuthRequired.addListener(
                        callbackFn,
                        {urls: ["<all_urls>"]},
                        ['blocking']
            )
            """
            plugin_file = 'proxy_with_username{}.zip'.format(self.serial_number)
            with zipfile.ZipFile(plugin_file, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js",
                            background_js % {'ip': ip, 'port': port, 'username': username, 'password': password})
            plugin_file = 'proxy_with_username{}.zip'.format(self.serial_number)
            self.option.add_extension(plugin_file)
        else:
            self.option.add_argument('--proxy-server=http://' + proxy)


if __name__ == "__main__":
    import sys
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    import time
    app = QApplication(sys.argv)
    url = "http://www.ip138.com/"
    proxy = "Host"
    browser = BrowserThread(url=url, proxy=proxy, serial_number=1)
    browser.start()
    sys.exit(app.exec())
