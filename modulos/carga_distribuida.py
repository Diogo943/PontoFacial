from modulos.elemento import Elemento as el
from modulos.no import No as no
import numpy as np

class CargaDist():
    def __init__(self, vetor_forca_local_elemento = {}, vetor_forca_global_elemento = {}, carregamento = {}):

        self.vetor_forca_local_elemento = vetor_forca_local_elemento
        self.vetor_forca_global_elemento = vetor_forca_global_elemento
        self.carregamento =carregamento

    def carga_dist(self, n_elem , qxi = 0.0 , qxj = 0.0 ,qyi = 0.0 , qyj = 0.0):
        L = el().Lelem[n_elem]

        vforca = np.zeros((6,1))

        vforca[0,0] = ( ( 1 / 3 ) * L *  qxi ) + ( ( 1 / 6 ) * L * qxj )

        vforca[1,0] = ( ( 7 / 20 ) * L * qyi )  + ( ( 3 / 20 ) * L * qyj )
        
        vforca[2,0] = ( ( 1 / 20 ) * L**2 * qyi)  + ( ( 1 / 30 ) * L**2 * qyj )
        
        vforca[3,0] = ( ( 1 / 6 ) * L * qxi ) + ( ( 1 / 3 ) * L * qxj )
        
        vforca[4,0] = ( ( 3 / 20 ) * L * qyi ) + ( ( 7 / 20 ) * L * qyj )
        
        vforca[5,0] = ( ( -1 / 30 ) * L**2 * qyi ) - ( ( 1 / 20 ) * L**2 * qyj )
        
        #Vetor de forças local dos elementos

        self.vetor_forca_local_elemento[n_elem] = vforca

        self.carregamento[n_elem] = [ qxi , qxj , qyi , qyj ]

        #Vetor de força global dos elementos

        self.vetor_forca_global_elemento[n_elem] = el().RTrans[n_elem].dot(self.vetor_forca_local_elemento[n_elem])

        #Incidências

        inc = el().incidencias[n_elem]

        #vetor de forças global da estrutura

        for linha_aux, linha in enumerate(inc):

            no().vetor_forca_global_est[linha][0] += self.vetor_forca_global_elemento[n_elem][linha_aux][0]

        
    def exibir_vetor_forca_local_elemento(self, n_elem):
        from pandas import DataFrame as df

        if n_elem not in self.vetor_forca_local_elemento.keys():
            print(df(np.zeros((6,1))))
        else:
            print(df(self.vetor_forca_local_elemento[n_elem]))
        
    def exibir_vetor_forca_global_elemento(self, n_elem):
        from pandas import DataFrame as df
        
        if n_elem not in self.vetor_forca_global_elemento.keys():
            print(df(np.zeros((6,1))))
        else:
            print(df(self.vetor_forca_global_elemento[n_elem]))

    def exibir_carregamento(self, n_elem):
        from pandas import DataFrame as df
        
        if n_elem not in self.carregamento.keys():
            print(df(np.zeros((4,1))))
        else:
            print(df(self.carregamento[n_elem]))

    def resetar_cargas_dist(self):
        self.vetor_forca_local_elemento.clear()
        self.vetor_forca_global_elemento.clear()
        self.carregamento.clear()
        


carregamento_dist = CargaDist()