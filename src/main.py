from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from sheets import sheet

from email_process import *

app = Flask(__name__)


@app.route('/dtc/maz/download', methods=['GET'])
@cross_origin()
def ScreamingallDiary():
    s = sheet()
    try:
        s.route()
        return jsonify({"response": "Proceso Ejecutado"})
    except Exception as e:
        return jsonify({"response": str(e)})


@app.route('/dtc/maz/emailprocess', methods=['GET'])
@cross_origin()
def emailprocess():

    correo = Correos()
    data = CargaData()
    try:
        
        print("Leer Correos Proceso ->")
        correo.leerCorreos('bavariacuentasbi@gmail.com','bsstprkvkklljcng')

        print("Cargar Data ->")
        data.getData()

        return jsonify({"response": "Proceso Ejecutado Leer Correos y Cargar Data"})
    except Exception as e:
        return jsonify({"response": str(e)})



def main():
    app.run(host= "0.0.0.0", port="5050", debug=True)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Saliendo")
        exit()

