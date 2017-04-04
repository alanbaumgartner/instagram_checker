import sys, aiohttp, asyncio
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

__author__ = 'Alan Baumgartner'

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowTitle('Login to Instagram')
        layout = QGridLayout()

        self.username_label = QLabel('Username')
        self.password_label = QLabel('Password')
        self.username_text = QLineEdit()
        self.password_text = QLineEdit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        self.password_text.setEchoMode(2)

        layout.addWidget(self.username_label, 0, 0)
        layout.addWidget(self.password_label, 1, 0)
        layout.addWidget(self.username_text, 0, 1)
        layout.addWidget(self.password_text, 1, 1)

        layout.addWidget(buttons, 2, 0, 3, 0)

        self.setLayout(layout)
        self.setGeometry(400, 400, 200, 60)

    @staticmethod
    def getLoginInfo():
        dialog = LoginDialog()
        result = dialog.exec_()
        return dialog.username_text.text(), dialog.password_text.text(), result == QDialog.Accepted

class ImportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('Import usernames')
        layout = QGridLayout()

        self.file_label = QLabel('Filename')
        self.file_text = QLineEdit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(self.file_label, 0, 0)
        layout.addWidget(self.file_text, 0, 1)

        layout.addWidget(buttons, 1, 0, 2, 0)

        self.setLayout(layout)
        self.setGeometry(400, 400, 200, 60)

    @staticmethod
    def getFileInfo():
        dialog = ImportDialog()
        result = dialog.exec_()
        return dialog.file_text.text(), result == QDialog.Accepted

class ExportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle('Export usernames')
        layout = QGridLayout()

        self.file_label = QLabel('Filename')
        self.file_text = QLineEdit()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(self.file_label, 0, 0)
        layout.addWidget(self.file_text, 0, 1)

        layout.addWidget(buttons, 1, 0, 2, 0)

        self.setLayout(layout)
        self.setGeometry(400, 400, 200, 60)

    @staticmethod
    def getFileInfo():
        dialog = ExportDialog()
        result = dialog.exec_()
        return dialog.file_text.text(), result == QDialog.Accepted

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
        export_action.triggered.connect(self.export_usernames)

        quit_action = QAction("Close", self)
        quit_action.triggered.connect(self.quit)

        menu.addAction(import_action)
        menu.addAction(export_action)
        menu.addAction(quit_action)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_clicked)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_clicked)

        self.input_text = QTextEdit()
        self.output_text = QTextEdit()

        input_label = QLabel('Usernames to Check')
        input_label.setAlignment(Qt.AlignCenter)

        output_label = QLabel('Available Usernames')
        output_label.setAlignment(Qt.AlignCenter)

        self.progress_bar = QProgressBar()
 
        #Add widgets to the window.
        layout.addWidget(input_label, 0, 0)
        layout.addWidget(output_label, 0, 1)
        layout.addWidget(self.input_text, 1, 0)
        layout.addWidget(self.output_text, 1, 1)
        layout.addWidget(self.start_button, 2, 0)
        layout.addWidget(self.stop_button, 2, 1)
        layout.addWidget(self.progress_bar, 3, 0, 4, 0)
		
    #When the start button is clicked, start the checker thread.
    def start_clicked(self):
        login = LoginDialog()
        igname, igpass, result = login.getLoginInfo()
        if result:
            usernames = get_usernames()
            self.progress_bar.setMaximum(len(usernames))
            self.output_text.setText('')
            self.thread = Checker(igname, igpass)
            self.thread.update.connect(self.update_text)
            self.thread.pupdate.connect(self.update_progress)
            self.thread.start()
        else:
            pass

    #When the stop button is clicked, terminate the checker thread.
    def stop_clicked(self):
        try:
            self.thread.terminate()
        except:
            pass
 
    #When the checker thread emits a signal, update the output textbox.
    def update_text(self, text):
        self.output_text.append(str(text))

    #When the checker thread emits a signal, update the progress bar.
    def update_progress(self, val):
        self.progress_bar.setValue(val)

    #Saves usernames from the output text.
    def export_usernames(self):
        exportDialog = ExportDialog()
        filename, result = exportDialog.getFileInfo()
        if result:
            try:
                proxies = self.output_text.toPlainText()
                proxies = proxies.strip()
                with open(filename, "w") as a:
                    a.write(proxies)
            except:
                pass
        else:
            pass

    def import_usernames(self):
        importDialog = ImportDialog()
        filename, result = importDialog.getFileInfo()
        if result:
            try:
                with open(filename, "r") as f:
                    out = f.read()
                    self.input_text.setText(out)
            except:
                pass
        else:
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

    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())