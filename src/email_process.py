import urllib.request
from datetime import date
import imaplib
import email
import os
import pandas as pd
import warnings
import psycopg2
from os import remove

from email.header import decode_header
from email.utils import parseaddr 

class Correos():

    remitente = '' 
    urlEmail = '' 

    def __init__(self):
        self.remitente = ''
        self.fechaValidacion = None
       # self.listaCorreos = self.con.correosParaValidar()

    def leerCorreos(self,email,password):    
        print("leerCorreos")     
        #print(self.urls)
        #self.calculaFechaPraCorreos()
        self.get_emails("smtp.gmail.com", email, password, True)


    def get_emails(self,gmailsmtpsvr, gmailusr, gmailpwd, bshowbody):
        print("get_emails")  
        try:
            # Conectamos a nuestro servidor, gmail necesita un ssl socket (encriptado) por lo que utilizamos 
            # la subclase IMAP4_SSL
            # Parámetros: host='', port=IMAP4_SSL_PORT, keyfile=None, certfile=None, ssl_context=None
            # El puerto por defecto IMAP4_SSL_PORT es el 993, en el caso de gmail lo dejamos como está, el resto de 
            # parámetros tampoco son necesarios en este caso.
            # Únicamente es necesario pasar como parámetro el servidor stmp de gmail 
            mail = imaplib.IMAP4_SSL(gmailsmtpsvr)
            # logamos:
            mail.login(gmailusr, gmailpwd)
            # seleccionamos bandeja de entrada 'inbox'
            mail.select("inbox")
            # recuperamos lista de emails, es posible filtrar la consulta
            # ALL devuelve todos los emails
            # Ejemplo de filtro: '(FROM "altaruru" SUBJECT "ejemplo python")'        
            result, data = mail.search(None, 'ALL')
            strids = data[0] # coge lista de ids encontrados
            lstids = strids.split()
            # recuperamos valores para bucle
            firstid = int(lstids[0])
            lastid = int(lstids[-1])
            countid = 0
            # mostramos datos de los ids encontrados
            #print("primer id: %d\nultimo id: %d\n..." % (firstid, lastid))
            # recorremos lista de mayor a menor (mas recientes primero)
            for id in range(lastid, firstid-1, -1):   
                print("ID => " + str(id))    
                typ, data = mail.fetch(str(id), '(RFC822)' ) # el parámetro id esperado es tipo cadena
                if (self.get_emailinfo(id, data, bshowbody)):
                    countid+=1
                    #Eliminacion del correo
                    mail.store(str(id), '+FLAGS', '\\Deleted')
                    break
            # fin, si llegamos aqui todo es correcto
            #print("emails listados %d" % countid)
            mail.expunge() 
            mail.close() 
            mail.logout() 
        except Exception as e:
            print("Error: %s" % (e))
            return ""
        except:
            print("Error desconocido")
            return ""

    def get_emailinfo(self,id, data, bshowbody=False):
        print("get_emailinfo")  
        for contenido in data:
            # comprueba que 'contenido' sea una tupla, si es así continua
            if isinstance(contenido, tuple):         
                # recuperamos información del email:                    
                msg = email.message_from_string(contenido[1].decode())
                # mostramos resultados:
                if int(msg['from'].find('noreply@datorama.com'))==0:
                    # solo valido los correos que ll
                    #if self.fechaValidacion == msg['date'][5:16]:
                    #print(msg)
                    if(bshowbody):
                        texto = self.get_body(msg)
                        print("---> ", texto)
                        self.downloadFail(msg)
                return True
        # si no hay info
        return False

    def downloadFail(self, msg):
        print("downloadFail")  
        for part in msg.walk():  
            fileName = part.get_filename()  
            fileName = self.decode_str(fileName)
                                 # Guardar archivo adjunto  
            if fileName:  
                fileName = fileName.replace("\r\n","")
                print("fileName  =>>> ", fileName)
                with open(fileName, 'wb') as fEx:
                    data = part.get_payload(decode=True) 
                    fEx.write(data)  
                    print ("El archivo adjunto% s se ha guardado"% fileName)

    def decode_str(self, s):
        print("decode_str")  
        if not s:
            return None
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def get_body(self, tmsg):  
        print("get_body")  
        body = ""
        if tmsg.is_multipart():        
            for part in tmsg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))    
                # skip any text/plain (txt) attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = str(part.get_payload(decode=True))  # decode
                    body=body.replace("\\r\\n","\n")                
                    break
        # not multipart - i.e. plain text, no attachments, keeping fingers crossed
        else:
            body = str(tmsg.get_payload(decode=True))
        return body

class CargaData():
    def __init__(self):        
        self.__ruta = os.path.abspath(os.getcwd())
        print("ruta file", self.__ruta)

    def getName(self):
        with os.scandir(self.__ruta) as ficheros:
            for fichero in ficheros:
                if len(str(fichero.name).split(".")) > 1:
                    if str(fichero.name).split(".",1)[1] == "xlsx":
                        return fichero.name

    def getData(self):
        #print(self.getName())
        archivo = str(self.__ruta + "/" + self.getName())
        print(archivo)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            df = pd.read_excel(archivo, engine="openpyxl", skiprows=6)
            cuerpo = "INSERT INTO dtc_regional_maz (Country, Brand, Platform, Month, day , Impressions, Link, Media) VALUES "
            titulos = df.columns.values
            for j in df.index:
                cuerpo += str("('{}','{}','{}','{}','{}',{},{},{}),").format(
                    df[titulos[0]][j],
                    df[titulos[1]][j],
                    df[titulos[2]][j],
                    df[titulos[3]][j],
                    df[titulos[4]][j],
                    df[titulos[5]][j],
                    df[titulos[6]][j],
                    df[titulos[7]][j])
        print(cuerpo[:-1])
        self.ejecutarConsulta(cuerpo[:-1])
        remove(str(self.__ruta + "/" + self.getName()))

    def ejecutarConsulta(self, sql):
        print("Ejecuta Consulta")
        try:
            self.con = psycopg2.connect(database= "db_server1", user="app_knime" , password="knime2020#", host="190.60.218.154", port="5432")
            self.cur = self.con.cursor()
            self.cur.execute(sql)
            #print(sql)
            self.con.commit()
            self.con.close()
        except (Exception, psycopg2.DatabaseError) as error:  
            controlarErr = str(error)         
            if controlarErr.find('(0x0000274C/10060)')>1 :
                print('Reintento de acceder')
                self.ejecutarConsulta(sql)
            else:   
                print(error) 
                print('*************************************')
                print(sql)
                print('*************************************')


