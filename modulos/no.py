import pandas as pd

class No():

    def __init__(self, CoordNo = [], restricao = [],  pos = {}, forca_no = [], vetor_forca_global_est = [],
                 carga_total = [], n_no = 0, reacoes_apoio = [], deslocamento = []):
        
        self.CoordNo = CoordNo
        self.restricao = restricao
        self.pos = pos
        self. forca_no = forca_no
        self.vetor_forca_global_est = vetor_forca_global_est
        self.carga_total = carga_total
        self.n_no = n_no
        self.reacoes_apoio = reacoes_apoio
        self.deslocamento = deslocamento

    def no(self,x,y):
        self.n_no += 1
        self.CoordNo.append([x,y])
        self.pos[self.n_no] = [x,y]
        
        for restricoes in range(3):
            self.restricao.append(0)
            
        for f_global_est in range(3):
            self.vetor_forca_global_est.append([0])
            
        for f_aplicada_no in range(3):
            self.forca_no.append([0])
        
        for forca_total in range(3):
            self.carga_total.append([0])
        
        for reacao in range(3):
            self.reacoes_apoio.append([0])
        
        for desloca in range(3):
            self.deslocamento.append([0])
        

    def exibir_reacoes_no(self, n_no):
        reacao = [ 0 , 0 , 0 ]
        pos = [ 3 * n_no - 3, 3 * n_no - 2 , 3 * n_no - 1 ]

        for i, r in enumerate(pos):
            reacao_ = self.reacoes_apoio[r][0]
            reacao[i] = round(reacao_,3)


        resultado = pd.DataFrame({'Fx (kN)': reacao[0],
                                  'Fy (kN)': reacao[1],
                                  'Mz (kNm)': reacao[2] }, index=[f'Nó {n_no}:'] )
        
        print('\n',resultado)
    
    def exibir_deslocamento_no(self, n_no):
        desloca = [0,0,0]
        pos = [ 3 * n_no - 3, 3 * n_no - 2 , 3 * n_no - 1 ]

        for i, d in enumerate(pos):
            deslocamento_ = self.deslocamento[d][0]
            desloca[i] = deslocamento_


        resultado = pd.DataFrame({'Dx (mm)': desloca[0] * 1000,
                                  'Dy (mm)': desloca[1] * 1000,
                                  'Dz (rad)': desloca[2] }, index=[f'Nó {n_no}:'] )
        
        print('\n',resultado)

    def exibir_vetor_forca_global_est(self):
        from pandas import DataFrame as df

        print(df(self.vetor_forca_global_est))

    def exibir_coord_no(self, num_no):
        print(self.CoordNo[num_no])

    def exibir_restricao(self, num_no):
        print(self.restricao[num_no])

    def exibir_posicao_no(self, num_no):
        print(self.pos[num_no])

    def exibir_forca_no(self, num_no):
        print(self.forca_no[num_no])

    def exibir_carga_total(self):
        print(self.carga_total)
    
    def reseta_no(self):
        self.CoordNo.clear()
        self.restricao.clear()
        self.pos.clear()
        self. forca_no.clear()
        self.vetor_forca_global_est.clear()
        self.carga_total.clear()
        self.n_no = 0
        self.reacoes_apoio.clear()
        self.deslocamento.clear()
    
                
  
no_ = No()