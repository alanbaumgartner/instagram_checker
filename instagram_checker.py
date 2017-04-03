import sys, aiohttp, asyncio
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QTextEdit, QLabel, QLineEdit, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal, Qt

__author__ = 'Alan Baumgartner'

class Checker(QThread):

    update = pyqtSignal(object)
    pupdate = pyqtSignal(object)
    count = 0

    #Global constants
    LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    URL = 'https://www.instagram.com/{}'

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.main())
        finally:
            loop.close()

    async def check_usernames(self, username, sem, session, lock):
        #Checks username availability
        async with sem:
            try:
                async with session.get(self.URL.format(username)) as resp:
                    text = await resp.text()
                    if "Page Not Found" in text:
                        self.update.emit(username)
            except:
                pass

            finally:
                with await lock:
                    self.count += 1
                self.pupdate.emit(self.count)

    async def main(self):
        #Packs all usernames into a tasklist
        sem = asyncio.BoundedSemaphore(50)
        lock = asyncio.Lock()
        async with aiohttp.ClientSession() as session:
            igname = get_igname()
            igpass = get_igpass()
            await self.login(igname, igpass, session)
            usernames = get_usernames()
            tasks = [self.check_usernames(username, sem, session, lock) for username in usernames]
            await asyncio.gather(*tasks)

    async def login(self, username, password, session):
        #Logs into Instagram
        async with session.get(self.URL.format('')) as response:
            csrftoken = await response.text()

        csrftoken = csrftoken.split('csrf_token": "')[1].split('"')[0]

        async with session.post(
                self.LOGIN_URL,
                    headers={
                        'x-csrftoken': csrftoken, 'x-instagram-ajax':'1',
                        'x-requested-with': 'XMLHttpRequest',
                        'Origin': self.URL, 'Referer': self.URL
                        },
                    data={
                        'username':username, 'password':password
                    }
                ) as response:

                text = await response.json()
                if 'authenticated' in text:
                    pass
                else:
                    sys.exit(text)

class App(QWidget):
 
    def __init__(self):

        #Declare some shit
        super().__init__()
        self.title = 'Instagram Username Checker'
        self.left = 300
        self.top = 300
        self.width = 500
        self.height = 500
        self.initUI()

    def initUI(self):

        #Setup layout
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        layout = QGridLayout()
        self.setLayout(layout)
 
        #Create Widgets
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_clicked)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_clicked)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_clicked)

        self.input_text = QTextEdit()
        self.output_text = QTextEdit()

        self.input_label = QLabel('Usernames to Check')
        self.input_label.setAlignment(Qt.AlignCenter)

        self.output_label = QLabel('Available Usernames')
        self.output_label.setAlignment(Qt.AlignCenter)

        self.save_entry = QLineEdit('Textfile.txt')
        self.save_entry.setAlignment(Qt.AlignCenter)

        self.name_entry = QLineEdit('Username')
        self.name_entry.setAlignment(Qt.AlignCenter)

        self.pass_entry = QLineEdit('Password')
        self.pass_entry.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar()
 
        #Add widgets to gui
        layout.addWidget(self.input_label, 0, 0)
        layout.addWidget(self.output_label, 0, 1)
        layout.addWidget(self.input_text, 1, 0)
        layout.addWidget(self.output_text, 1, 1)
        layout.addWidget(self.name_entry, 2, 0)
        layout.addWidget(self.pass_entry, 2, 1)
        layout.addWidget(self.start_button, 3, 0)
        layout.addWidget(self.save_entry, 3, 1)
        layout.addWidget(self.stop_button, 4, 0)
        layout.addWidget(self.save_button, 4, 1)
        layout.addWidget(self.progress_bar, 5, 0, 6, 0)

    def start_clicked(self):
        usernames = get_usernames()
        self.progress_bar.setMaximum(len(usernames))
        self.output_text.setText('')
        self.thread = Checker(self)
        self.thread.update.connect(self.update_text)
        self.thread.pupdate.connect(self.update_progress)
        self.thread.start()

    def stop_clicked(self):
        try:
            self.thread.terminate()
        except:
            pass

    def save_clicked(self):
        self.save_usernames()
 
    def update_text(self, text):
        self.output_text.append(str(text))

    def update_progress(self, val):
        self.progress_bar.setValue(val)

    def save_usernames(self):
        proxies = self.output_text.toPlainText()
        proxies = proxies.strip()
        outputfile = self.save_entry.text()
        with open(outputfile, "a") as a:
            a.write(proxies)

if __name__ == '__main__':

    def get_usernames():
        proxies = window.input_text.toPlainText()
        proxies = proxies.strip()
        proxies = proxies.split('\n')
        return proxies

    def get_igname():
        return window.name_entry.text()

    def get_igpass():
        return window.pass_entry.text()

    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())