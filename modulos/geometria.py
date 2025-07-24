import numpy as np

class PropriedadeSecao():
    def __init__(self, secao_elem = {}):
        self.secao_elem = secao_elem

    def generico(self, Area, Inercia, n_elem):
        self.secao_elem[n_elem] = [ Area , Inercia ]

    def ret(self, base, altura, n_elem):
        Area = base*altura
        Inercia = ( base * altura**3 ) / 12
        self.secao_elem[n_elem] = [ Area , Inercia ]

    def circ(self, diametro_d, n_elem):
        Area = (np.pi * diametro_d**2 ) / 4
        Inercia = (np.pi * diametro_d**4 ) / 64
        self.secao_elem[n_elem] = [ Area , Inercia ]

    def resetar_secao_elem(self):
        self.secao_elem.clear()

prop_secao = PropriedadeSecao()