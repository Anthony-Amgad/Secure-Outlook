import json
import os
import tkinter
from tkinter import filedialog
from PyQt5 import QtWidgets, uic, QtGui
from AES import aes_encrypt_message
from RSA import rsa_pubencrypt_data, sign_message

class Compose(QtWidgets.QMainWindow):

    KM = None
    outlook_app = None
    attachments = []
    root = None

    def send(self):

        body = self.textEdit.document().toPlainText()
        subject = self.subjectEdit.text()
        to = self.toEdit.text()

        AESK = os.urandom(32)
        AESS = os.urandom(16)

        encrypted_subject = aes_encrypt_message(subject.encode('utf-8'), AESK, AESS)
        
        topub = self.KM.mdb.getKey(to)

        if(topub == None):
            msg = QtWidgets.QMessageBox()
            msg.setWindowIcon(QtGui.QIcon('res/error.png'))
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('The Email Your trying to send to is not a member of this encryption system')
            msg.setWindowTitle("Error")
            msg.exec_()        

        else:
            encrypted_AESK = rsa_pubencrypt_data(AESK, topub)
            encrypted_AESS = rsa_pubencrypt_data(AESS, topub)

            sig = sign_message(body, self.KM.privateKey)

            body_map = {"body":body,"signature":sig.decode('latin-1')}

            encrypted_body = aes_encrypt_message(json.dumps(body_map).encode('utf-8'), AESK, AESS)

            mail_item = self.outlook_app.CreateItem(0) 
            mail_item.To = to
            mail_item.Subject = "Encrypted T15 CSE451"

            files = os.listdir("res/sendAttach/")
            for file in files:
                file_path = os.path.join("res/sendAttach/", file)
                if os.path.isfile(file_path):
                    os.remove(file_path)  

            attachment_map = {}
            for i, attach in enumerate(self.attachments):
                attachment = os.path.abspath(attach)
                if os.path.exists(attachment):
                    print(attachment)
                    encrypted_name = aes_encrypt_message(attachment.split("\\")[-1].encode('utf-8'),AESK,AESS)
                    with open(attachment, 'rb') as inp, open(f'res/sendAttach/{i}.bin', 'wb') as out:
                        original = inp.read()
                        encrypted_attach = aes_encrypt_message(original,AESK,AESS)
                        out.write(encrypted_attach.encode('utf-8'))
                    inp.close()
                    out.close()
                    attachment = os.path.join(os.path.dirname(os.path.abspath(__file__))+"\\res\\sendAttach\\", str(i)+".bin")
                    mail_item.Attachments.Add(attachment)
                    attachment_map.update({i:encrypted_name})

            mail_body = {"AESK":encrypted_AESK.decode('latin-1'),"AESS":encrypted_AESS.decode('latin-1'),
                        "subject":encrypted_subject,"body":encrypted_body, "attachments":attachment_map}
            
            mail_item.Body = json.dumps(mail_body)

            mail_item.Send()
            self.close()

    def reloadAtt(self):
        self.listWidget.clear()
        for filepath in self.attachments:
            itemN, widget = self.attCard(filepath)
            self.listWidget.addItem(itemN)
            self.listWidget.setItemWidget(itemN, widget)

    def removeAtt(self, filepath):
        self.attachments.remove(filepath)
        self.reloadAtt()

    def attCard(self, filepath):
        itemN = QtWidgets.QListWidgetItem() 
        widget = QtWidgets.QWidget()
        widgetPath =  QtWidgets.QLabel(filepath)
        widgetRemove =  QtWidgets.QPushButton("X")
        widgetRemove.setStyleSheet("""color: rgb(255, 0, 0);border:none;font: 75 16pt;""")
        widgetPath.setStyleSheet("""font: 75 9pt;""")
        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.addWidget(widgetRemove)
        widgetLayout.addWidget(widgetPath)
        widgetLayout.addStretch()
        widgetLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        widget.setLayout(widgetLayout)  
        widget.setStyleSheet("""background-color: grey;""")
        itemN.setSizeHint(widget.sizeHint())
        widgetRemove.mouseReleaseEvent = lambda event:self.removeAtt(filepath)
        widgetPath.mouseReleaseEvent = lambda event:os.startfile(filepath)
        return itemN, widget

    def addAttach(self):
        currdir = os.getcwd()
        filepath = filedialog.askopenfilename(parent=self.root, initialdir=currdir, title="Please select a file")
        if len(filepath)>0:
            self.attachments.append(filepath)
            self.reloadAtt()
            

    def __init__(self, km, oa):

        self.KM = km
        self.outlook_app = oa
        self.root = tkinter.Tk()
        self.root.withdraw()
         
        super(Compose,self).__init__()
        uic.loadUi('res/ui/Compose.ui',self)

        self.setWindowIcon(QtGui.QIcon('res/img.png'))

        self.addbtn.clicked.connect(self.addAttach)
        self.sendbtn.clicked.connect(self.send)
        
        self.show()

        #This is for finding functions using auto complete as they cannot be found with the item loaded in the .ui
        # self.x = QtWidgets.QTextEdit(self.centralwidget)
        # self.x.document().toRawText()