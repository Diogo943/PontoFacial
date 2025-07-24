#from elemento import element

class PropriedadeElemento():
    def __init__(self, prop_elem = {}):
        self.prop_elem = prop_elem
    
    def concreto(self, n_elem, E=25e+6):
        # E = 25 GPa 
        self.prop_elem[n_elem] = E  #MPa (kN/m²)
        
    def aco(self, n_elem, E=205e+6):
        # E = 205 GPa
        self.prop_elem[n_elem] = E #MPa (kN/m²)
    
    def generico(self,n_elem, E):
        self.prop_elem[n_elem] = E
    
    def resetar_prop_elem(self):
        self.prop_elem = {}


propriedade_elemento = PropriedadeElemento()