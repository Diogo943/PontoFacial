from openpyxl import load_workbook
import os

class Registro():
    def __init__(self):
        self.arquivo = load_workbook(f'{os.getcwd()}\\REGISTROS\\registro.xlsx')

    def getDados(self):
        for i in range(1,self.arquivo['Registro'].max_row):
            coluna_data = self.arquivo['Registro'].cell(row=i, column=1).value
            coluna_hora = self.arquivo['Registro'].cell(row=i, column=2).value
            coluna_nome = self.arquivo['Registro'].cell(row=i, column=3).value
            coluna_tipo = self.arquivo['Registro'].cell(row=i, column=4).value

            print(f'{i} - {coluna_data} - {coluna_hora} - {coluna_nome} - {coluna_tipo}')

    def getId(self, nome = '', data = '', hora = '' ):
        for i in range(1,self.arquivo['Registro'].max_row):
            coluna_data = self.arquivo['Registro'].cell(row=i, column=1).value
            coluna_hora = self.arquivo['Registro'].cell(row=i, column=2).value
            coluna_nome = self.arquivo['Registro'].cell(row=i, column=3).value
            coluna_tipo = self.arquivo['Registro'].cell(row=i, column=4).value

            if nome.upper() in coluna_nome.upper() and data.upper() in coluna_data.upper() and hora.upper() in coluna_hora.upper():
                print(f'{i} - {coluna_data} - {coluna_hora} - {coluna_nome} - {coluna_tipo}')

    def setDados(self, data = '', hora = '' , nome = '' , tipo = '' ):
        max_linha = self.arquivo['Registro'].max_row + 1
        self.arquivo['Registro'].cell(row = max_linha, column=1).value =  data
        self.arquivo['Registro'].cell(row = max_linha, column=2).value = hora
        self.arquivo['Registro'].cell(row = max_linha, column=3).value = nome
        self.arquivo['Registro'].cell(row = max_linha, column=4).value = tipo

        self.arquivo.save(f'{os.getcwd()}\\REGISTROS\\registro.xlsx')

    def clearDados(self, linha):

        self.arquivo['Registro'].delete_rows(idx=linha)

        self.arquivo.save(f'{os.getcwd()}\\REGISTROS\\registro.xlsx')


registro = Registro()

registro.clearDados(174)

registro.getId(data= '14')
