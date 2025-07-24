from modulos.geometria import prop_secao as prop
from modulos.no import no_ as nd
from modulos.elemento import elemento as el
from modulos.carga_distribuida import CargaDist as ql
from modulos.propriedade_elemento import propriedade_elemento as pe
import numpy as np
from pandas import DataFrame as df



Kglobal_est = np.zeros((3*len(nd.CoordNo), 3*len(nd.CoordNo)))

class MatrizRigidez():
    def __init__(self, klelem = {}, kgelem = {}, kg_est = 0):
        self.klelem = klelem
        self.kgelem = kgelem
        self.kg_est = kg_est
    
    def rigidez(self, n_elem):
        
        A = prop.secao_elem[n_elem][0]
        I = prop.secao_elem[n_elem][1]
        E = pe.prop_elem[n_elem]
        L = el.Lelem[n_elem]

        #Matriz de rigidez local dos elementos

        self.klelem[n_elem] = np.array([
        [E * A / L  ,0                  ,0                 ,-E * A / L  ,0                  ,0                 ],
        [0          ,12 * E * I / L**3  ,6 * E * I / L**2  ,0           ,-12 * E * I / L**3 ,6 * E * I / L**2  ],
        [0          ,6 * E * I / L**2   ,4 * E * I / L     ,0           ,-6 * E * I / L**2  ,2 * E * I / L     ],
        [-E * A / L ,0                  ,0                 ,E * A / L   ,0                  ,0                 ],
        [0          ,-12 * E * I / L**3 ,-6 * E * I / L**2 ,0           ,12 * E * I / L**3  ,-6 * E * I / L**2 ],
        [0          ,6 * E * I / L**2   ,2 * E * I / L     ,0           ,-6 * E * I / L**2  ,4 * E * I / L     ]])

        #Matriz de rigidez global dos elementos
        kg = el.RTrans[n_elem].dot(self.klelem[n_elem].dot(el.Relem[n_elem]))
        self.kgelem[n_elem] = kg

        #Incidência

        inc = el.incidencias[n_elem]

        #Matriz de rigidez global da estrutura

        for linha_aux, linha in enumerate(inc):
            for coluna_aux, coluna in enumerate(inc):

                Kglobal_est[linha][coluna] += kg[linha_aux][coluna_aux]
        
        self.kg_est = Kglobal_est

    def exibir_matriz_rigidez_elem(self, n_elem):
        print(df(self.klelem[n_elem]))
    
    def exibir_matriz_global_elem(self,n_elem):
        print(df(self.kgelem[n_elem]))

    def resetar_matriz_rigidez(self):
        self.klelem.clear()
        self.kgelem.clear()
        self.kg_est = 0


matrizrigidez = MatrizRigidez()

for i in range(1, len(el.Lelem) + 1,1):
    MatrizRigidez().rigidez(i)

Kglobal_est_copy = Kglobal_est.copy() #Matriz global sem contorno

def exibir_matriz_global_est_sem_contorno():
        print(df(Kglobal_est_copy))

for pos in range(3 * len(nd.CoordNo)):
    nd.carga_total[pos][0] = nd.vetor_forca_global_est[pos][0] + nd.forca_no[pos][0]

nd.carga_total = np.array(nd.carga_total)

#Condicão de contorno

for i in range(3 * len(nd.CoordNo)):
    if nd.restricao[i] == 1:
        nd.carga_total[i][0] = 0

for i in range(3 * len(nd.CoordNo)):
    if nd.restricao[i] == 1:

        for j in range(3 * len(nd.CoordNo)):
            Kglobal_est[i][j] = 0
            Kglobal_est[j][i] = 0
        Kglobal_est[i][i] = 1

def exibir_Kglobal_com_contorno():

    print(pd.DataFrame(Kglobal_est))

def DeslocamentoGlobal():
    from numpy import linalg

    kg_inv = linalg.inv(Kglobal_est)

    Ug = kg_inv.dot(nd.carga_total) #deslocamento

    return Ug

def exibir_deslocamento_global():
    print(df(DeslocamentoGlobal()))

def Deslocamento_no():
    desloc = DeslocamentoGlobal()

    for pos,desloca in enumerate(desloc):
        if nd.restricao[pos] == 0:
            nd.deslocamento[pos] = desloca

Deslocamento_no()

def Reacoes_Apoio():
    reacao_total = Kglobal_est_copy.dot(DeslocamentoGlobal()) - nd.vetor_forca_global_est

    for pos,reacao in enumerate(reacao_total):
        if nd.restricao[pos] == 1:
            nd.reacoes_apoio[pos] = reacao
            

Reacoes_Apoio()

          
class DeslocamentosLocal():
    def __init__(self, ul = {}):

        self.ul = ul

    def deslocamento_elemento(self, n_elem):

        ug = np.zeros((6,1))

        inc = el.incidencias[n_elem]

        for linha_aux, i in enumerate(inc):
            ug[linha_aux] = DeslocamentoGlobal()[i]

        self.ul[n_elem] = el.Relem[n_elem].dot(ug)
    
    def obter_deslocamento_local(self, n_elem):
        return self.ul[n_elem]


for i in range(1, len(el.Lelem) + 1, 1):
    DeslocamentosLocal().deslocamento_elemento(i)

import pandas as pd

class EsforcoInterno():
    def __init__(self, f_interno = {}, n_elem = 0):

        self.f_interno = f_interno
        self.n_elem = n_elem

    def esforco_interno(self):

        self.n_elem +=1
        self.f_interno[self.n_elem] = MatrizRigidez().klelem[self.n_elem].dot(DeslocamentosLocal().ul[self.n_elem])

        for i in range(6):
            self.f_interno[self.n_elem][i][0] = round(self.f_interno[self.n_elem][i][0],3)

        if self.n_elem in ql().vetor_forca_local_elemento.keys():
            for i in range(6):
                self.f_interno[self.n_elem][i][0] -= round(ql().vetor_forca_local_elemento[self.n_elem][i][0],3)

        resultado = pd.DataFrame({ 'Normal (kN)' : [' ',-self.f_interno[self.n_elem][0][0], self.f_interno[self.n_elem][3][0]],
                                    'Cortante (kN)' :[' ',self.f_interno[self.n_elem][1][0], -self.f_interno[self.n_elem][4][0]],
                                    'Momento (kNm)': [' ',-self.f_interno[self.n_elem][2][0], self.f_interno[self.n_elem][5][0]]},
                                    index= [f'ELEMENTO',f'   {el.elem[self.n_elem][0]}',f'   {el.elem[self.n_elem][1]}'])
        
        print('\n',resultado)

    def exibir_esforco_interno(self, n_elem):
        print(self.f_interno[n_elem])

    def  resetar_esforco_interno(self):
        self.f_interno.clear()
        self.n_elem = 0

esforco_interno = EsforcoInterno()

class Resultado():
    def executar(self):
        for i in range(1, len(el.Lelem)+1, 1):
            esforco_interno.esforco_interno()

resultado = Resultado()