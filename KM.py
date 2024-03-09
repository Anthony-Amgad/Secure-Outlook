import os
import pickle
from RSA import generate_key_pair, rsa_pubencrypt_data, rsa_privdecrypt_data, rsa_privserialize, rsa_pubserialize
from MDB import MDB

class KM():

    privateKey = None
    mdb = None

    def setPublicKey(self, email):
        snk = False
        if os.path.isfile(f"res/RSA{email}.sav"):
            self.privateKey = pickle.load(open(f"res/RSA{email}.sav",'rb'))
            publickey = self.mdb.getKey(str(email))
            if publickey == None:
                snk = True
            else:  
                plain = os.urandom(32)
                encr = rsa_pubencrypt_data(plain, publickey)
                try:
                    if rsa_privdecrypt_data(encr, self.privateKey) != plain:
                        self.mdb.deleteKey(str(email))
                        snk = True
                except:
                    self.mdb.deleteKey(str(email))
                    snk = True
        else:
            self.mdb.deleteKey(str(email))
            snk = True
        
        if snk:
            privKey, publickey = generate_key_pair()
            self.privateKey = rsa_privserialize(privKey)
            pickle.dump(self.privateKey, open(f"res/RSA{email}.sav", 'wb'))
            self.doc = self.mdb.addKey(str(email), rsa_pubserialize(publickey))

    def __init__(self) -> None:
        self.mdb = MDB()


