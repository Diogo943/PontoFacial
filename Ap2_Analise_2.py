from modulos.no import no_ as n
from modulos.apoio import apoio as ap
from modulos.carga_aplicada import carga_aplicada as qa
from modulos.elemento import elemento as el
from modulos.propriedade_elemento import propriedade_elemento as pel
from modulos.geometria import prop_secao as ps
from modulos.carga_distribuida import carregamento_dist as cd

#Geometria
A = 6e-3 #m²
I = 180e-6 #m^4
#Propriedade do elemento
E = 200e+6 #kPa

#Definindo os nós (Já criado na interface)
n.no(0,6) #1
n.no(6,6) #2
n.no(6,0) #3

#Criação dos elementos (Já criado na interface)
el.elemento(1,2) #Elemento 1
el.elemento(2,3) #Elemento 2

#Aplicão de apoios (Já criado na interface)
ap.prim_gen(1)
ap.terc_gen(3)

#Cargas aplicadas (Já criado na interface)
qa.forca_aplicada_no(2,20,0,0) #n_no,fx,fy,mz

#Cargas distribuídas

#Propriedades dos elementos (Já criado na interface)
for i in range(1,3):
    pel.generico(i,E)

#Propriedades das seções transversais (Já criado na interface)
for i in range(1,3):
    ps.generico(A,I,i)

from modulos.matrizrigidez import resultado

resultado.executar()

for i in range(1,4):
    n.exibir_reacoes_no(i)

for i in range(1,4):
    n.exibir_deslocamento_no(i)
