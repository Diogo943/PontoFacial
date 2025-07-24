from modulos.no import no_

class Apoio():
    def __init__(self, apoios = {}):
        self.apoios = apoios

    def prim_gen(self, no_id):

        coord_x = no_.pos[no_id][0]
        coord_y = no_.pos[no_id][1]

        for i in range(len(no_.CoordNo)):
            if no_.CoordNo[i][0] == coord_x and no_.CoordNo[i][1] == coord_y:
                no_.restricao[3*i + 1] = 1

        self.apoios[no_id] = 'móvel' #[ 0 1 0]

    def seg_gen(self, no_id):

        coord_x = no_.pos[no_id][0]
        coord_y = no_.pos[no_id][1]

        for i in range(len(no_.CoordNo)):
            if no_.CoordNo[i][0] == coord_x and no_.CoordNo[i][1] == coord_y:
                no_.restricao[3 * i] = 1
                no_.restricao[3 * i + 1] = 1

        self.apoios[no_id] = 'fixo' #[1 1 0]

    def terc_gen(self, no_id):
        
        coord_x = no_.pos[no_id][0]
        coord_y = no_.pos[no_id][1]

        for i in range(len(no_.CoordNo)):
            if no_.CoordNo[i][0] == coord_x and no_.CoordNo[i][1] == coord_y:
                no_.restricao[3*i] = 1
                no_.restricao[3*i + 1] = 1
                no_.restricao[3*i + 2] = 1

        self.apoios[no_id] = 'engaste' #[1 1 1]
    
    def resetar_apoios(self):
        self.apoios.clear()

apoio = Apoio()