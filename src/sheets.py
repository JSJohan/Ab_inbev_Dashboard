import gspread
from descargaData import gtU

class sheet():

    def __init__(self):
        self.__sa = gspread.service_account(filename ="./src/Sheets.json")
        self.__sh = self.__sa.open("Data dashboard automatizada - DTC")

    def route(self):
        wks = self.__sh.worksheet("Configuracion")

        #cuenta = wks.acell('A6').value 
        row = 6
        cuenta = ''
        sheetsName = ''
        keyJson = ''

        while True:
            cuenta = wks.cell(row, 1).value
            sheetsName = wks.cell(row, 2).value
            keyJson = wks.cell(row, 3).value
            if str(cuenta) == "None":
                break
            else:
                print(row, "->", cuenta, "Name Sheets", sheetsName)
                self.process(sheetsName = sheetsName, cuenta = cuenta, keyJson = keyJson)
                wks.update_cell(row, 4, wks.acell('D1').value)
                row += 1

    def process(self, **kwargs):
        print("Proceso en ->", kwargs["sheetsName"])
        reskws = self.__sh.worksheet(kwargs["sheetsName"])   
        j = 1
        while True:
            j +=1
            fechas = reskws.cell(2, j).value
            if str(fechas) == "None":
                break
            else:
                init = str(fechas).split("|")[0].strip()
                fin = str(fechas).split("|")[1].strip()
                

        print(j,"-> ",init,"|",fin)        
        
        g = gtU()
        respuesta = g.runReport(kwargs['cuenta'],init,fin, keyJson = kwargs["keyJson"])    

        print(respuesta)

        reskws.update_cell(4,j-1, respuesta[0])
        reskws.update_cell(5,j-1, respuesta[1])
        reskws.update_cell(6,j-1, respuesta[2])
        reskws.update_cell(7,j-1, respuesta[3])
        reskws.update_cell(8,j-1, respuesta[4])
        reskws.update_cell(9,j-1, str(respuesta[5])[0:6])
        reskws.update_cell(10,j-1, respuesta[6])
        reskws.update_cell(11,j-1, respuesta[7])

        

