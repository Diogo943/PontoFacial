from modulos.no import No
import numpy as np


class Elemento():
    def __init__(self, Relem ={}, RTrans = {}, Lelem = {}, elem = {}, ligacao = {}, n_elem = 0, coord_elem = {}, arct = {},
                  incidencias = {}):
        self.Relem = Relem
        self.RTrans = RTrans
        self.Lelem = Lelem
        self.elem = elem
        self.ligacao = ligacao
        self.n_elem = n_elem
        self.coord_elem = coord_elem
        self.arct = arct
        self.incidencias = incidencias

    def elemento(self, pos_i,pos_j):
        
        self.n_elem += 1

        xi = No().pos[pos_i][0]
        yi = No().pos[pos_i][1]
        
        xf = No().pos[pos_j][0]
        yf = No().pos[pos_j][1]

        dx = xf - xi
        dy = yf - yi

        L_elem = np.sqrt(dx**2 + dy**2)

        cos_theta = dx / L_elem
        sen_theta = dy / L_elem

        theta = None

        if dx == 0:
            theta = 0
        
        if dx != 0:
            theta = np.arctan(dy/dx) * 180 / np.pi

        matriz_Rotacao = np.array([
                                    [ cos_theta  , sen_theta  ,   0   ,     0     ,     0      ,  0  ],
                                    [-sen_theta  , cos_theta  ,   0   ,     0     ,     0      ,  0  ],
                                    [     0      ,     0      ,   1   ,     0     ,     0      ,  0  ],
                                    [     0      ,     0      ,   0   , cos_theta , sen_theta  ,  0  ],
                                    [     0      ,     0      ,   0   ,-sen_theta , cos_theta  ,  0  ],
                                    [     0      ,     0      ,   0   ,     0     ,     0      ,  1  ]])
                    
        
        self.Relem[self.n_elem] = matriz_Rotacao
        self.RTrans[self.n_elem] = matriz_Rotacao.T
        self.Lelem[self.n_elem] = L_elem
        self.elem[self.n_elem] = [pos_i, pos_j]
        self.ligacao[self.n_elem] = ['3','3']
        self.coord_elem[self.n_elem] = [xi, xf, yi, yf]
        self.arct[self.n_elem] = theta
        self.incidencias[self.n_elem] = [3 * pos_i - 3, 3 * pos_i - 2, 3 * pos_i - 1, 3 * pos_j - 3, 3 * pos_j - 2, 3 * pos_j - 1 ]

    def exibir_matriz_rotacao_elemento(self,n_elem):

        print(self.Relem[n_elem])

    def exibir_matriz_rotacaoT_elemento(self, n_elem):

        print(self.RTrans[n_elem])

    def exibir_comprimento_elemento(self, n_elem):

        print(self.Lelem[n_elem])

    def exibir_elemento(self, n_elem):

        print(self.elem[n_elem])

    def exibir_ligacao_elemento(self, n_elem):

        print(self.ligacao[n_elem])

    def exibir_coordenada_elemento(self, n_elem):

        print(self.coord_elem[n_elem])

    def exibir_incidencias_elemento(self, n_elem):

        print(self.incidencias[n_elem])
    
    def resetar_elemento(self):
        self.Relem.clear()
        self.RTrans.clear()
        self.Lelem.clear()
        self.elem.clear()
        self.ligacao.clear()
        self.n_elem = 0
        self.coord_elem.clear()
        self.arct.clear
        self.incidencias.clear()


elemento = Elemento()