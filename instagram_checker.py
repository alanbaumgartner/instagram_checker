import sys, aiohttp, asyncio
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

__author__ = 'Alan Baumgartner'

class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('Login to Instagram')
        layout = QGridLayout()

        self.username_label = QLabel('Username')
        self.password_label = QLabel('Password')
        self.username_text = QLineEdit()
        self.password_text = QLineEdit()
        self.password_text.setEchoMode(2)

        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.password_label, 1, 0)
        layout.addWidget(self.username_text, 0, 1)
        layout.addWidget(self.password_text, 1, 1)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        layout.addWidget(self.buttons, 2, 0, 3, 0)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.setLayout(layout)
        self.setGeometry(400, 400, 200, 60)

    @staticmethod
    def getLoginInfo():
        dialog = Login()
        result = dialog.exec_()
        return (dialog.username_text.text(), dialog.password_text.text())

class Checker(QThread):

    #Signal Variables.
    update = pyqtSignal(object)
    pupdate = pyqtSignal(object)
    count = 0

    #Global Variables.
    LOGIN_URL = 'https://www.instagram.com/accounts/login/ajax/'
    URL = 'https://www.instagram.com/{}'

    def __init__(self, igname, igpass):
        super().__init__()
        self.igname = igname
        self.igpass = igpass

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.main())
        finally:
            loop.close()

    #Checks username availability.
    async def check_usernames(self, username, sem, session, lock):
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

    #Creates a task for each username and then runs each task.
    async def main(self):
        sem = asyncio.BoundedSemaphore(50)
        lock = asyncio.Lock()
        async with aiohttp.ClientSession() as session:
            #if loginbool 
            await self.login(self.igname, self.igpass, session)
            usernames = get_usernames()
            tasks = [self.check_usernames(username, sem, session, lock) for username in usernames]
            await asyncio.gather(*tasks)

    #Logs into Instagram.
    async def login(self, username, password, session):
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

class App(QMainWindow):
 
    def __init__(self):

        #Declares some constructor variables.
        super().__init__()
        self.title = 'Instagram Username Checker'
        self.left = 300
        self.top = 300
        self.width = 500
        self.height = 500
        self.initUI()

    def initUI(self):

        #Setup layout.
        wid = QWidget(self)
        self.setCentralWidget(wid)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        layout = QGridLayout()
        wid.setLayout(layout)
 
        #Create Widgets.
        menu_bar = self.menuBar()

        menu = menu_bar.addMenu("File")

        import_action = QAction("Import Usernames", self)
        import_action.triggered.connect(self.import_usernames)

        export_action = QAction("Export Usernames", self)
        export_action.triggered.connect(self.save_usernames)

        quit_action = QAction("Close", self)
        quit_action.triggered.connect(self.quit)

        menu.addAction(import_action)
        menu.addAction(export_action)
        menu.addAction(quit_action)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_clicked)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_clicked)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_clicked)

        self.input_text = QTextEdit()
        self.output_text = QTextEdit()

        input_label = QLabel('Usernames to Check')
        input_label.setAlignment(Qt.AlignCenter)

        output_label = QLabel('Available Usernames')
        output_label.setAlignment(Qt.AlignCenter)

        self.save_entry = QLineEdit('Textfile.txt')
        self.save_entry.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar()
 
        #Add widgets to the window.
        layout.addWidget(input_label, 0, 0)
        layout.addWidget(output_label, 0, 1)
        layout.addWidget(self.input_text, 1, 0)
        layout.addWidget(self.output_text, 1, 1)
        layout.addWidget(self.start_button, 2, 0)
        layout.addWidget(self.save_entry, 2, 1)
        layout.addWidget(self.stop_button, 3, 0)
        layout.addWidget(self.save_button, 3, 1)
        layout.addWidget(self.progress_bar, 4, 0, 5, 0)
		
    #When the start button is clicked, start the checker thread.
    def start_clicked(self):
        login = Login()
        igname, igpass = login.getLoginInfo()
        usernames = get_usernames()
        self.progress_bar.setMaximum(len(usernames))
        self.output_text.setText('')
        self.thread = Checker(igname, igpass)
        self.thread.update.connect(self.update_text)
        self.thread.pupdate.connect(self.update_progress)
        self.thread.start()

    # def start_thread(self, igname, igpass, loginbool):
    #     usernames = get_usernames()
    #     self.progress_bar.setMaximum(len(usernames))
    #     self.output_text.setText('')
    #     self.thread = Checker(self, igname, igpass, loginbool)
    #     self.thread.update.connect(self.update_text)
    #     self.thread.pupdate.connect(self.update_progress)
    #     self.thread.start()

    #When the stop button is clicked, terminate the checker thread.
    def stop_clicked(self):
        try:
            self.thread.terminate()
        except:
            pass

    #When the save button is clicked, call the save_usernames function.
    def save_clicked(self):
        self.save_usernames()
 
    #When the checker thread emits a signal, update the output textbox.
    def update_text(self, text):
        self.output_text.append(str(text))

    #When the checker thread emits a signal, update the progress bar.
    def update_progress(self, val):
        self.progress_bar.setValue(val)

    #Saves usernames from the output text.
    def save_usernames(self):
        proxies = self.output_text.toPlainText()
        proxies = proxies.strip()
        outputfile = self.save_entry.text()
        with open(outputfile, "a") as a:
            a.write(proxies)

    def import_usernames(self):
        try:
            text, ok = QInputDialog.getText(self, 'Import Usernames', 'Enter file name:')
            with open(text, "r") as f:
                out = f.read()
            if ok:
                self.input_text.setText(out)
        except:
            pass
        
    def quit(self):
        sys.exit()

if __name__ == '__main__':

    #Get usernames from the input textbox.
    def get_usernames():
        proxies = window.input_text.toPlainText()
        proxies = proxies.strip()
        proxies = proxies.split('\n')
        return proxies

    #Get Instagram username from the entry box.
    def get_igname():
        return window.name_entry.text()

    #Get Instagram password from the entry box.
    def get_igpass():
        return window.pass_entry.text()

    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())