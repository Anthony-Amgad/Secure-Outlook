from PyQt5 import QtWidgets, uic, QtGui
import sys
from Inbox import MP
import win32com.client as client


class MUi(QtWidgets.QMainWindow):

    outlook_app = None

    def openInbox(self):
        self.ui = MP(self.outlook_app, self.outlook_app.Session.Accounts[self.accCom.currentIndex()])
        self.close()

    def __init__(self):

        self.outlook_app = client.Dispatch("Outlook.Application")

        super(MUi,self).__init__()
        uic.loadUi('res/ui/MainWindow.ui',self)

        for acc in self.outlook_app.Session.Accounts:
            self.accCom.addItem(str(acc))

        self.accCom.setCurrentIndex(0)

        self.setWindowIcon(QtGui.QIcon('res/img.png'))

        self.openAccbtn.clicked.connect(self.openInbox)

        self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MUi()
    app.exec_()