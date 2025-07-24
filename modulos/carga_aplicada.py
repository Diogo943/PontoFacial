from modulos.no import No


class CargaAplicada():
    def __init__(self):
        pass

    def forca_aplicada_no(self, no_id, Px , Py, Mz):

        No().forca_no[3 * (no_id - 1) + 0][0] += Px
        No().forca_no[3 * (no_id - 1) + 1][0] += Py
        No().forca_no[3 * (no_id - 1) + 2][0] += Mz
    

carga_aplicada = CargaAplicada()