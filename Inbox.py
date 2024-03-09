import base64
import json
import os
from PyQt5 import QtWidgets, uic, QtGui
import sys
from KM import KM
from Compose import Compose
from AES import aes_decrypt_message
from RSA import rsa_privdecrypt_data, verify_signature

class MP(QtWidgets.QMainWindow):

    outlook_app = None
    KM = None

    def openAttach(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__))+"\\res\\recAttach\\", self.attCom.currentText())
        os.startfile(path)

    def showRegEmail(self, email):
        self.dateLabel.setText(email.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S"))
        self.fromLabel.setText(email.SenderEmailAddress)
        recistr = ""
        for reci in email.Recipients:
            recistr+=f"{reci}; "
        self.toLabel.setText(recistr)
        self.subjectLabel.setText(email.Subject)

        if email.Attachments.Count > 0:
            self.attCom.clear()
            self.attCom.setEnabled(True)
            self.openAttbtn.setEnabled(True)
        
            files = os.listdir("res/recAttach/")
            for file in files:
                file_path = os.path.join("res/recAttach/", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)            
            for attachment in email.Attachments:
                # Save attachment to local storage
                self.attCom.addItem(attachment.FileName)
                save_path = os.path.join(os.path.dirname(os.path.abspath(__file__))+"\\res\\recAttach\\", attachment.FileName)
                attachment.SaveAsFile(save_path)
            self.attCom.setCurrentIndex(0)
        else:
            self.attCom.clear()
            self.attCom.setEnabled(False)
            self.openAttbtn.setEnabled(False)


        self.textBrowser.setText(email.Body)

    def showEncEmail(self, email, DemailMap):
        self.dateLabel.setText(email.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S"))
        self.fromLabel.setText(email.SenderEmailAddress)
        recistr = ""
        for reci in email.Recipients:
            recistr+=f"{reci}; "
        self.toLabel.setText(recistr)
        self.subjectLabel.setText(DemailMap['subject'])

        if email.Attachments.Count > 0:
            self.attCom.clear()
            self.attCom.setEnabled(True)
            self.openAttbtn.setEnabled(True)
        
            files = os.listdir("res/recAttach/")
            for file in files:
                file_path = os.path.join("res/recAttach/", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)    

            for attachment in email.Attachments:
                # Save attachment to local storage
                save_path = os.path.join(os.path.dirname(os.path.abspath(__file__))+"\\res\\recAttach\\", attachment.FileName)
                attachment.SaveAsFile(save_path)

            encattachs = os.listdir("res/recAttach/")
            for attach in encattachs:
                attachment = os.path.abspath("res/recAttach/"+attach)
                fnenc = DemailMap["attachments"][attach.removesuffix(".bin")]
                filename = aes_decrypt_message(base64.b64decode(fnenc),DemailMap["AESK"],DemailMap["AESS"]).decode('utf-8')
                with open(attachment, 'rb') as inp, open(f'res/recAttach/{filename}', 'wb') as out:
                    encrypted = inp.read()
                    decrypted_attach = aes_decrypt_message(base64.b64decode(encrypted),DemailMap["AESK"],DemailMap["AESS"])
                    out.write(decrypted_attach)
                inp.close()
                out.close()
                self.attCom.addItem(filename)
            self.attCom.setCurrentIndex(0)
        else:
            self.attCom.clear()
            self.attCom.setEnabled(False)
            self.openAttbtn.setEnabled(False)

        self.textBrowser.setText(DemailMap["body"])

    def regEmailCard(self, email):
        itemN = QtWidgets.QListWidgetItem() 
        widget = QtWidgets.QWidget()
        widgetSubject = QtWidgets.QLabel(email.Subject)
        widgetSender = QtWidgets.QLabel(f"{email.SenderName} ({email.SenderEmailAddress})")
        widgetSender.setStyleSheet("""font: 75 8pt;""")
        widgetSubject.setStyleSheet("""font: 75 9pt;""")
        widgetLayout = QtWidgets.QVBoxLayout()
        widgetLayout.addWidget(widgetSubject)
        widgetLayout.addWidget(widgetSender)
        widgetLayout.addStretch()
        widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        widget.setLayout(widgetLayout)  
        widget.setStyleSheet("""background-color: yellow;""")
        itemN.setSizeHint(widget.sizeHint())
        widget.mouseReleaseEvent = lambda event:self.showRegEmail(email)
        return itemN, widget
    
    def encEmailCard(self, email):
        itemN = QtWidgets.QListWidgetItem() 
        widget = QtWidgets.QWidget()
        widgetSender =  QtWidgets.QLabel(f"{email.SenderName} ({email.SenderEmailAddress})")
        widgetSender.setStyleSheet("""font: 75 8pt;""")
        color = 'pink'
        mouseReleaseEvent = None

        try:
            DemailMap = {"semail":email.SenderEmailAddress}
            EemailMap = json.loads(email.Body)
            AESK = rsa_privdecrypt_data(EemailMap["AESK"].encode('latin-1'), self.KM.privateKey)
            AESS = rsa_privdecrypt_data(EemailMap["AESS"].encode('latin-1'), self.KM.privateKey)
            Subject = aes_decrypt_message(base64.b64decode(EemailMap["subject"]), AESK, AESS).decode('utf-8')
            body_Map = json.loads(aes_decrypt_message(base64.b64decode(EemailMap["body"]), AESK, AESS).decode('utf-8'))
            pubk = self.KM.mdb.getKey(email.SenderEmailAddress)
            if (pubk != None) and verify_signature(body_Map['body'],body_Map['signature'].encode('latin-1'), pubk):
                color = 'rgb(144, 238, 144)'

            DemailMap.update({"AESK":AESK,"AESS":AESS,"subject":Subject,"body":body_Map['body'],"attachments":EemailMap["attachments"]})
            widgetSubject =  QtWidgets.QLabel(Subject)
            mouseReleaseEvent = lambda event:self.showEncEmail(email,DemailMap)
        
        except:
            widgetSubject =  QtWidgets.QLabel("Key of this email is lost")
            color = 'red'
        
        widgetSubject.setStyleSheet("""font: 75 9pt;""")
        widgetLayout = QtWidgets.QVBoxLayout()
        widgetLayout.addWidget(widgetSubject)
        widgetLayout.addWidget(widgetSender)
        widgetLayout.addStretch()
        widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        widget.setLayout(widgetLayout)  
        widget.setStyleSheet(f"""background-color: {color};""")
        itemN.setSizeHint(widget.sizeHint())
        widget.mouseReleaseEvent = mouseReleaseEvent
        return itemN, widget

    
    
    def getEmails(self):
        namespace = self.outlook_app.GetNamespace("MAPI")
        inbox = namespace.GetDefaultFolder(6) # 6 represents olFolderInbox constant
        self.listWidget.clear()
        items = inbox.Items
        items.Sort("[ReceivedTime]", True)
        for i, item in enumerate(items):
            if(i<50):
                if item.Subject == "Encrypted T15 CSE451":
                    itemN, widget = self.encEmailCard(item)
                    self.listWidget.addItem(itemN)
                    self.listWidget.setItemWidget(itemN, widget)
                else:
                    itemN, widget = self.regEmailCard(item)
                    self.listWidget.addItem(itemN)
                    self.listWidget.setItemWidget(itemN, widget)
            # print(item.ReceivedTime)

    def openCompose(self):
        self.ui = Compose(self.KM, self.outlook_app)

    
    def __init__(self, oa, acc):

        self.KM = KM()
        self.outlook_app = oa

        self.KM.setPublicKey(acc)
         
        super(MP,self).__init__()
        uic.loadUi('res/ui/Inbox.ui',self)

        self.setWindowIcon(QtGui.QIcon('res/img.png'))
        
        self.getEmails()

        self.refreshbtn.clicked.connect(self.getEmails)
        self.openAttbtn.clicked.connect(self.openAttach)
        self.composebtn.clicked.connect(self.openCompose)
        
        self.show()

        #This is for finding functions using auto complete as they cannot be found with the item loaded in the .ui
        # self.x = QtWidgets.QComboBox(self.centralwidget)
        # self.x.currentIndex


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MP()
    app.exec_()