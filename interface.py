'''
import subprocess

bibliotecas_requeridas = ['customtkinter','pandas','numpy','matplotlib']

for biblioteca in bibliotecas_requeridas:
    try:
        __import__(biblioteca)
    except ImportError:
        subprocess.check_call(['python', '-m', 'pip', 'install', biblioteca])
'''

import os
import sys
os.environ['TK_SCALE'] = '1'


import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import messagebox, Menu
from matplotlib.patches import Arc
from matplotlib.widgets import Cursor
from matplotlib.ticker import MultipleLocator

#Módulos criados para analise estrutural
from modulos.no import No as no
from modulos.elemento import Elemento as elem
from modulos.apoio import Apoio as apoio
from modulos.carga_aplicada import CargaAplicada as carga_aplicada
from modulos.carga_distribuida import CargaDist as carga_distribuida
from modulos.propriedade_elemento import PropriedadeElemento as prop_elem
from modulos.geometria import PropriedadeSecao as prop_secao




class StrucFrame():
    def __init__(self, root):
        super().__init__()

        self.root = root
        self.root.title("Simulação de Estruturas")
        self.root.geometry("1200x600+1+1")
        self.root.resizable(True, True)


        #Variáveis de controle
        self.ponto_inicial = None
        self.posi = None
        self.posf = None
        self.linha_temporaria = None
        self.linhas = {}
        self.pos = None
        self.pontos = None
        self.grid_ativado = False
        self.snap_ativado = False
        self.elemento_ativado = False
        self.tipo_apoio = None
        self.pontos_medios = {}
        self.press = {}
        self.tipo_elem = None
        self.tipo_secao = None
        self.localizador_mult_x = 1
        self.localizador_mult_y = 1
        self.coord_x = None
        self.coord_y = None
        self.limExIn = -10
        self.limExFi = 10
        self.janela_ajuste_grid = None
        self.janela_prop_elemento = None
        self.janela_prop_secao = None
        self.janela_prop_apoio = None
        self.janela_adicionar_forca_distribuida = None
        self.adicionar_forca_no = None


        #Criando instâncias dos módulos
        self.no = no()
        self.elem = elem()
        self.apoio = apoio()
        self.carga_aplicada = carga_aplicada()
        self.carga_distribuida = carga_distribuida()
        self.prop_elem = prop_elem()
        self.prop_secao = prop_secao()
        
        self.grafico()
        self.widget()
        self.mpl_connect_events()

 
    def mpl_connect_events(self):
        
        self.fig.canvas.mpl_connect('motion_notify_event', self.move_mouse)
        self.canvas.mpl_connect('scroll_event', self.zoom)
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        

    def grafico(self):
        # Criando a figura do Matplotlib
        self.fig, self.ax = plt.subplots()

        # Configurando o canvas do Matplotlib no CustomTkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().place(x=0, y=0, relwidth=1, relheight=0.96)

        self.fig.subplots_adjust(left=0.03, right=0.98, bottom=0.04, top=0.98)
        self.ax.set_xlim(self.limExIn, self.limExFi)
        self.ax.set_ylim(self.limExIn, self.limExFi)

        # Força os ticks a aparecerem em todas as unidades inteiras
        self.set_major_locator_x = self.ax.xaxis.set_major_locator(MultipleLocator(self.localizador_mult_x))
        self.set_major_locator_y = self.ax.yaxis.set_major_locator(MultipleLocator(self.localizador_mult_y))
  

    def widget(self):

        # Adicionando menu
        self.menu = Menu(self.root)

        #Adicionar menu file
        self.menu_file = Menu(self.menu, tearoff=0, activebackground='blue', activeforeground='white', bg='white', fg='black', font=('Arial', 10), relief='raised' )
        self.menu_file.add_command(label= 'Resetar',  command= self.resetar_elem)
        self.menu_file.add_command(label= 'Quit', command= lambda :self.root.quit())
        self.menu.add_cascade(label= 'File', menu= self.menu_file)

        #Menu View
        self.menu_view = Menu(self.menu, tearoff=0, activebackground='blue', activeforeground='white', bg='white', fg='black', font=('Arial', 10), relief='raised' )
        #self.menu_view.add_command(label= 'Número do elemento')

        #Adicionar menu de apoio
        self.menu_apoios = Menu(self.menu, tearoff=0, activebackground='blue', activeforeground='white', bg='white', fg='black', font=('Arial', 10), relief='raised' )
        self.menu_apoios.add_command(label='Fixo', command=lambda: self.aplicar_apoios('Fixo'))
        self.menu_apoios.add_command(label='Móvel', command=lambda: self.aplicar_apoios('Móvel'))
        self.menu_apoios.add_command(label='Engaste', command=lambda: self.aplicar_apoios('Engaste'))
        self.menu.add_cascade(label='Apoio', menu=self.menu_apoios)

        #Adicionar menu força
        self.menu_forca = Menu(self.menu, tearoff=0, activebackground='blue', activeforeground='white', bg='white', fg='black', font=('Arial', 10), relief='flat')
        self.menu_forca.add_command(label='Aplicada', command=lambda: self.aplicar_forcas('Aplicada'))
        self.menu_forca.add_command(label='Distribuída', command=lambda: self.aplicar_forcas('Distribuída'))
        self.menu.add_cascade(label='Força', menu=self.menu_forca)
        
        #Adicionar menu de propriedades do elemento
        self.menu_prop_elem = Menu(self.menu, tearoff=0, activebackground='blue', activeforeground='white', bg='white', fg='black', font=('Arial', 10), relief='flat')
        self.menu_prop_elem.add_command(label='Concreto', command=lambda: self.aplicar_prop_elemento('Concreto'))
        self.menu_prop_elem.add_command(label='Aço', command=lambda: self.aplicar_prop_elemento('Aço'))
        self.menu_prop_elem.add_command(label='Genérico', command=lambda: self.aplicar_prop_elemento('Genérico'))
        self.menu.add_cascade(label='Prop. do Elemento', menu=self.menu_prop_elem)

        #Adicionar menu de propriedades da seção
        self.menu_prop_secao = Menu(self.menu, tearoff=0, activebackground='blue', activeforeground='white', bg='white', fg='black', font=('Arial', 10), relief='flat')
        self.menu_prop_secao.add_command(label='Retangular', command=lambda: self.aplicar_prop_secao('Retangular'))
        self.menu_prop_secao.add_command(label='Circular', command=lambda: self.aplicar_prop_secao('Circular'))
        self.menu_prop_secao.add_command(label='Genérico', command= lambda : self.aplicar_prop_secao('Genérico'))
        self.menu.add_cascade(label='Prop. da Seção', menu=self.menu_prop_secao)

        #Adicionar menu snap
        self.menu.add_command(label='Snap: OFF', command=self.snap, state='disabled')
        
        #Adicionar menu de grid
        self.menu.add_command(label='Grid: OFF', command= self.grid)

        #Adicionar menu de desenho de elementos
        self.menu.add_command(label='Elemento: OFF', command= self.ativar_desenho)

        #Adicionar menu de run
        self.menu_run = Menu(self.menu, tearoff=0, activebackground='blue', activeforeground='white', bg='white', fg='black', font=('Arial', 10), relief='raised' )
        self.menu_run.add_command(label='Run', command= lambda: self.run('Executar'))
        self.menu.add_cascade(label= 'Executar', menu= self.menu_run)

        self.root.config(menu=self.menu)

        #Adicionar barra inferir
        self.barra_inferior = ctk.CTkFrame(self.root, fg_color='blue', bg_color='white')
        self.barra_inferior.place(relx=0, rely=0.96, relwidth=1, relheight=0.05)

        #Exibir coordenadas e tamanho
        self.lb_coordenadas = ctk.CTkLabel(self.barra_inferior, text= f'Coordenadas: (0.00 , 0.00)',
                                            font=('Arial', 12))
        self.lb_coordenadas.place(relx=0.02, rely=0.00001)

        #ajuste de grid
        self.bt_grid_ajuste = ctk.CTkButton(self.barra_inferior,text = 'Ajuste grid', 
                                            command= self.ajuste_grid, anchor= 'center', state='disabled', font=('Arial', 12), text_color='white', text_color_disabled= 'blue')
        self.bt_grid_ajuste.place(relx = 0.6, rely = 0.1, relheight = 0.7)
    
        
        #clicar na tecla D para desenhar elementos
        self.root.bind('<d>', self.retorno_desenho)
        self.root.bind('<D>', self.retorno_desenho)

        #clicar na tecla S para ativar/desativar snap
        #if self.grid_ativado:

        self.root.bind('<s>', self.retorno_snap)
        self.root.bind('<S>', self.retorno_snap)

        #clicar na tecla G para ativar/desativar grid
        self.root.bind('<g>', self.retorno_grid)
        self.root.bind('<G>', self.retorno_grid)
        

    def move_mouse(self, event):
        x, y = event.xdata, event.ydata
        try:
            self.lb_coordenadas.configure(text= f'Coordenadas: ({x:.2f} , {y:.2f})')
        except:
            pass

    
    def zoom(self, event):

        escala_base = 0.9

        xlim_atual = self.ax.get_xlim()
        ylim_atual = self.ax.get_ylim()

        xdata = event.xdata
        ydata = event.ydata

        fator_escala = escala_base if event.button == 'up' else 1 / escala_base

        nova_largura = (xlim_atual[1] - xlim_atual[0]) * fator_escala
        nova_altura = (ylim_atual[1] - ylim_atual[0]) * fator_escala
        relx = (xlim_atual[1] - xdata) / (xlim_atual[1] - xlim_atual[0])
        rely = (ylim_atual[1] - ydata) / (ylim_atual[1] - ylim_atual[0])

        self.ax.set_xlim([xdata - nova_largura * (1 - relx), xdata + nova_largura * relx])
        self.ax.set_ylim([ydata - nova_altura * (1 - rely), ydata + nova_altura * rely])

        self.fig.canvas.draw()


    def on_press(self,event):
        if event.inaxes:
            if event.button == 2:
                self.press['x'], self.press['y'] = event.xdata, event.ydata

    def estilo_cursor(self, estilo):
        '''
        "arrow" - Setinha normal 
        "circle" - Círculo
        "clock" - Relógio (esperando)
        "cross" - Cruz fina
        "crosshair" - Cruz tipo mira
        "dotbox" - Caixa pontilhada
        "exchange" - Setas cruzadas
        "fleur" - Quatro setas (mover)
        "heart" - Coração 
        "man" - Bonequinho
        "mouse" - Ícone de mouse
        "pirate" - Caveira
        "plus" - Sinal de mais
        "shuttle" - Nave (antigo)
        "sizing" - Setas para redimensionar
        "spider" - Aranha
        "spraycan" - Spray
        "star" - Estrela
        "target" - Alvo
        "tcross" - Cruz grossa
        "trek" - Trekker (?)
        "watch" - Relógio (espera)
        '''
        
        self.canvas.get_tk_widget().config(cursor = estilo)

    def on_motion(self,event):
        if 'x' in self.press and event.inaxes:
            dx = self.press['x'] - event.xdata
            dy = self.press['y'] - event.ydata

            x0, x1 = self.ax.get_xlim()
            y0, y1 = self.ax.get_ylim()
            self.ax.set_xlim(x0 + dx, x1 + dx)
            self.ax.set_ylim(y0 + dy, y1 + dy)

            self.estilo_cursor('fleur')

            self.fig.canvas.draw()

    def on_release(self,event):
        self.press.clear()
        self.estilo_cursor('arrow')
        self.fig.canvas.draw()


    def retorno_desenho(self, event):
        if event.keysym == 'd' or event.keysym == 'D':
            if not self.elemento_ativado:
                self.ativar_desenho()
            else:
        
                self.ativar_desenho()
    
    def retorno_grid(self, event):
        if event.keysym == 'g' or event.keysym == 'G':
            if not self.grid_ativado:
                self.ativar_grid()
            else:
                self.desativar_grid()

    
    def retorno_snap(self, event):
        if event.keysym == 's' or event.keysym == 'S':
            if self.grid_ativado and not self.snap_ativado:
                self.ativar_snap()

            elif self.snap_ativado:
                self.desativar_snap()

            else:
                pass

    def ativar_desenho(self):
        
        if not self.elemento_ativado:
    
            self.elemento_ativado = True
            self.menu.entryconfig('Elemento: OFF', label='Elemento: ON')
            #Conectando eventos de clique e movimento do mouse no gráfico
            self.inserir = self.fig.canvas.mpl_connect("button_press_event", self.inserir_elemento)
            self.movimento = self.fig.canvas.mpl_connect("motion_notify_event", self.no_movimento)

        else:
            
            self.elemento_ativado = False
            self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
            self.fig.canvas.mpl_disconnect(self.inserir)
            self.fig.canvas.mpl_disconnect(self.movimento)
            try:
                self.cursor.disconnect_events()
            except:
                pass

    def snap_to_grid(self, x, y ):

        grid_size_x = self.localizador_mult_x
        grid_size_y = self.localizador_mult_y

        snapped_x = round(x / grid_size_x) * grid_size_x
        snapped_y = round(y / grid_size_y) * grid_size_y

        return snapped_x, snapped_y
    
    def ativar_snap(self):
        self.menu.entryconfig('Snap: OFF', label='Snap: ON')
        self.snap_ativado = not self.snap_ativado
            
    def desativar_snap(self):
        self.menu.entryconfig('Snap: ON', label='Snap: OFF')
        self.snap_ativado = not self.snap_ativado
            
    def snap(self):
        
        if not self.snap_ativado:
            self.ativar_snap()
        else:
            self.desativar_snap()

    def ativar_grid(self):
        
        self.menu.entryconfig('Grid: OFF', label='Grid: ON')
        self.grid_ativado = not self.grid_ativado
        
        # Mostrar a grade principal
        self.ax.grid(self.grid_ativado, which='major', color='grey', linestyle='-', linewidth=0.75)
        #Habilitar snap e ajuste grid
        if not self.snap_ativado:
            self.menu.entryconfig('Snap: OFF', state='active')

        else:
            self.menu.entryconfig('Snap: ON', state='active')

        self.bt_grid_ajuste.configure(state='active')
    
        self.canvas.draw()

    def desativar_grid(self):

        self.menu.entryconfig('Grid: ON', label='Grid: OFF')
        self.grid_ativado = not self.grid_ativado

        # Mostrar a grade principal
        self.ax.grid(self.grid_ativado)
    
        #Desabilitar snap e ajuste grid
        if not self.snap_ativado:
            self.menu.entryconfig('Snap: OFF', state='disabled')
        else:
            self.menu.entryconfig('Snap: ON', state='disabled')
            self.desativar_snap()

        self.bt_grid_ajuste.configure(state='disabled')

        self.canvas.draw()
            
    def grid(self):
        
        if not self.grid_ativado:
            self.ativar_grid()
        else:
            self.desativar_grid()

    def inserir_elemento(self, event):

        self.cursor = Cursor(self.ax, useblit=True, color='red', linewidth=0.5, linestyle='--')
        
        if event.button == 1:
            self.cursor.active = True
        else:
            self.cursor.active = False
            return

        if event.xdata is None or event.ydata is None:
            return
        
        x, y = event.xdata, event.ydata

        if self.snap_ativado:
            x, y = self.snap_to_grid(x, y)


        if self.ponto_inicial is None:
            self.ponto_inicial = [x, y]

            if self.ponto_inicial in self.no.CoordNo:
                self.posi = self.no.CoordNo.index(self.ponto_inicial) + 1
            else:
                self.no.no(x,y)
                self.posi = self.no.CoordNo.index([x,y]) + 1
            
        else:
            x1, y1 = self.ponto_inicial
            x2, y2 = x, y
            
            if [x2,y2] in self.no.CoordNo: 
                self.posf =  self.no.CoordNo.index([x2,y2]) + 1
            else:
                self.no.no(x2,y2)
                self.posf = self.no.CoordNo.index([x2,y2]) + 1
            
            self.ponto_medio = [(x1 + x2) / 2, (y1 + y2) / 2]

            self.pontos_medios[self.elem.n_elem] = self.ponto_medio

            self.elem.elemento(self.posi, self.posf)
        
            self.ax.text(self.ponto_medio[0],self.ponto_medio[1], f'{self.elem.n_elem}', fontsize=10, color='b')

            self.ax.text(x1,y1, f'{self.posi}', fontsize=10, color='g')
            self.ax.text(x2,y2, f'{self.posf}', fontsize=10, color='g')
            
            linha, = self.ax.plot([x1, x2], [y1, y2], 'ro-', linewidth=1, markersize=1.5, markerfacecolor='blue', picker=True)

            self.ax.scatter(x1, y1, color='r', marker='o',s=10, picker=True)
            self.ax.scatter(x2, y2, color='r', marker='o',s=10, picker=True)

            
            self.lb_coordenadas.configure(text=f'Coordenadas: ({x:.2f} , {y:.2f})          Tamanho: {self.elem.Lelem[self.elem.n_elem]:.2f}')
            
            self.linhas[self.elem.n_elem] = linha
            self.ponto_inicial = None
            #self.lb_coordenadas.configure(text=f'Coordenadas: (0.00 , 0.0)          Tamanho: 0.00')
    
            
            if self.linha_temporaria:
                self.linha_temporaria[0].remove()
                self.linha_temporaria = None
        
            
            self.canvas.draw()    
        

        if self.posi is not None and self.posf is not None: 
            self.posi = None
            self.posf = None


    def no_movimento(self, event):
        if self.ponto_inicial is not None and event.xdata is not None and event.ydata is not None:
            if self.linha_temporaria:
                self.linha_temporaria[0].remove()

            x1, y1 = self.ponto_inicial
            x2, y2 = event.xdata, event.ydata
            
            self.lb_coordenadas.configure(text=f'Coordenadas: ({x2:.2f} , {y2:.2f})          Tamanho: {((x2-x1)**2 + (y2-y1)**2)**0.5:.2f}')
        
            self.linha_temporaria = self.ax.plot([x1, x2], [y1, y2], 'b--')
            self.canvas.draw()


    def capturar_ponto_apoio(self, event):
        if event.xdata is None or event.ydata is None:
            return
        
        x, y = event.xdata, event.ydata

        if self.snap_ativado:
            x, y = self.snap_to_grid(x, y)
        
        if [x,y] in self.no.CoordNo:
            self.pos_apoio = self.no.CoordNo.index([x,y]) + 1

        else:
            messagebox.showerror("Erro", "Não foi possível inserir o apoio. O ponto selecionado não pertence a um nó.")
            self.fig.canvas.mpl_disconnect(self.inserir) #trocar o nome 
            return

        if self.tipo_apoio == 'Fixo':
            self.apoio.seg_gen(self.pos_apoio)
            self.ax.plot(x, y - 0.11, '^r', markersize=8)

        elif self.tipo_apoio == 'Móvel':
            self.apoio.prim_gen(self.pos_apoio)
            self.ax.plot(x, y - 0.11, '^b', markersize=8)
            self.ax.plot(x, y-0.22, '_', markersize=10, color='b')

        elif self.tipo_apoio == 'Engaste':
            self.apoio.terc_gen(self.pos_apoio)
            self.ax.plot([x,x], [y + 0.15, y - 0.15], '-', markersize=8, color='g', linewidth=1.25)
            self.ax.plot([x - 0.025 , x + 0.025], [y + 0.15, y + 0.10], '-', markersize=8, color='g', linewidth=1.25)
            self.ax.plot([x - 0.025 , x + 0.025], [y + 0.025, y - 0.025], '-', markersize=8, color='g', linewidth=1.25)
            self.ax.plot([x - 0.025 , x + 0.025], [y - 0.1, y - 0.15], '-', markersize=8, color='g', linewidth=1.25)

        self.canvas.draw()

        self.fig.canvas.mpl_disconnect(self.inserir_apoio)

        if self.tipo_apoio is not None:
            self.tipo_apoio = None

    def capturar_ponto_forca(self, event):
        if event.xdata is None or event.ydata is None:
            return
        
        x, y = event.xdata, event.ydata   

        if self.snap_ativado:
            x, y = self.snap_to_grid(x, y)
        
        if [x,y] in self.no.CoordNo:
            self.pos_forca = self.no.CoordNo.index([x,y]) + 1
        
        else:
            messagebox.showerror("Erro", "Não foi possível inserir a forca. O ponto selecionado não pertence a um nó.")
            self.inserir_info_no.remove()
            self.canvas.draw()
            self.fig.canvas.mpl_disconnect(self.adicionar_forca)


        
        self.adicionar_forca_no = ctk.CTkToplevel(self.root)
        self.adicionar_forca_no.title("Forca")
        self.adicionar_forca_no.geometry("250x300+1+1")
        self.adicionar_forca_no.resizable(False, False)
        self.adicionar_forca_no.grab_set()
        self.adicionar_forca_no.focus_set()

        self.label_Fx = ctk.CTkLabel(self.adicionar_forca_no, text="Fx:")
        self.label_Fx.place(relx=0.1, rely=0.1, anchor='w')

        self.entry_Fx = ctk.CTkEntry(self.adicionar_forca_no)
        self.entry_Fx.place(relx=0.3, rely=0.1, anchor='w')

        self.label_Fy = ctk.CTkLabel(self.adicionar_forca_no, text="Fy:")
        self.label_Fy.place(relx=0.1, rely=0.2, anchor='w')
        
        self.entry_Fy = ctk.CTkEntry(self.adicionar_forca_no)
        self.entry_Fy.place(relx=0.3, rely=0.2, anchor='w')

        self.label_M = ctk.CTkLabel(self.adicionar_forca_no, text="M:")
        self.label_M.place(relx=0.1, rely=0.3, anchor='w')
        
        self.entry_M = ctk.CTkEntry(self.adicionar_forca_no)
        self.entry_M.place(relx=0.3, rely=0.3, anchor='w')

        def set_forcas_aplicadas():

            Fx = float(self.entry_Fx.get()) if self.entry_Fx.get() != '' else 0.0
            Fy = float(self.entry_Fy.get()) if self.entry_Fy.get() != '' else 0.0
            M = float(self.entry_M.get()) if self.entry_M.get() != '' else 0.0


            self.carga_aplicada.forca_aplicada_no(self.pos_forca, Fx, Fy, M)
            distancia = self.localizador_mult_x
            raio = distancia
            #Criar um circulo em torno do ponto
            momento = Arc((x, y), raio, raio, angle=0, theta1=0, theta2=180, color='black', linewidth=1)
            
            if Fx > 0:
                self.ax.annotate(f"{Fx}kN", xytext=(x - distancia , y), xy=(x, y))
                self.ax.annotate("", xytext=(x - distancia, y), xy=(x , y),arrowprops=dict(arrowstyle="->"))
            
            if Fy > 0:
                self.ax.annotate(f"{Fy}kN", xytext=(x, y - distancia), xy=(x , y))
                self.ax.annotate("", xytext=(x, y - distancia), xy=(x , y),arrowprops=dict(arrowstyle="->"))

            if M > 0:
                
                self.ax.add_patch(momento)
                self.ax.annotate("", xytext=(x - raio / 2, y ), xy=(x - raio / 2 , y - raio/4),arrowprops=dict(arrowstyle="->"))
                self.ax.annotate(f"{M}kNm", xytext=(x , y + raio/2), xy=(x , y))
    
            if Fx < 0:
                self.ax.annotate(f"{-Fx}kN", xytext=(x + distancia , y), xy=(x, y))
                self.ax.annotate("", xytext=(x + distancia, y), xy=(x , y),arrowprops=dict(arrowstyle="->"))
            
            if Fy < 0:
                self.ax.annotate(f"{-Fy}kN", xytext=(x, y + distancia), xy=(x , y))
                self.ax.annotate("", xytext=(x, y + distancia), xy=(x , y),arrowprops=dict(arrowstyle="->"))

            if M < 0:
                
                self.ax.add_patch(momento)
                self.ax.annotate("", xytext=(x + raio / 2, y ), xy=(x + raio / 2 , y - raio/4),arrowprops=dict(arrowstyle="->"))
                self.ax.annotate(f"{-M}kNm", xytext=(x , y + raio/2), xy=(x , y))
            

            self.inserir_info_no.remove()
            self.canvas.draw()
            
            self.adicionar_forca_no.destroy()

        self.botao_confirmar = ctk.CTkButton(self.adicionar_forca_no, text="Confirmar", command= set_forcas_aplicadas)
        self.botao_confirmar.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        def cancelar_forcas_aplicadas():
            self.inserir_info_no.remove()
            self.canvas.draw()
            self.adicionar_forca_no.destroy()

        self.botao_cancelar = ctk.CTkButton(self.adicionar_forca_no, text="Cancelar", command= cancelar_forcas_aplicadas)
        self.botao_cancelar.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
        

        self.fig.canvas.mpl_disconnect(self.adicionar_forca)
        

    def aplicar_apoios(self, event): #CORRIGIR OS APOIOS PARA REDIMENSIONAMENTO JUNTO COM O GRID DINÂMICO
    
        if self.no.CoordNo == []:
            messagebox.showerror("Erro", "Nenhum nó foi inserido")

        elif event == 'Fixo':
            if self.elemento_ativado:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            self.tipo_apoio = 'Fixo'
            self.inserir_apoio = self.fig.canvas.mpl_connect("button_press_event", self.capturar_ponto_apoio)
            
        elif event == 'Móvel':
            if self.elemento_ativado:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            self.tipo_apoio = 'Móvel'
            self.inserir_apoio = self.fig.canvas.mpl_connect("button_press_event", self.capturar_ponto_apoio)

        elif event == 'Engaste':
            if self.elemento_ativado :
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()
                
            self.tipo_apoio = 'Engaste'
            self.inserir_apoio = self.fig.canvas.mpl_connect("button_press_event", self.capturar_ponto_apoio)

    def capturar_elemento_cargas(self, event):

        elemento = event.artist
            
        if elemento in self.linhas.values():
            id_elemento = list(self.linhas.values()).index(elemento) + 1

            if self.janela_adicionar_forca_distribuida is None or not self.janela_adicionar_forca_distribuida.winfo_exists():

                self.janela_adicionar_forca_distribuida = ctk.CTkToplevel(self.root)
                self.janela_adicionar_forca_distribuida.title("Força distribuída")
                self.janela_adicionar_forca_distribuida.geometry("250x300+1+1")
                self.janela_adicionar_forca_distribuida.resizable(False, False)
                self.janela_adicionar_forca_distribuida.grab_set()
                self.janela_adicionar_forca_distribuida.focus_set()

                self.label_qxi = ctk.CTkLabel(self.janela_adicionar_forca_distribuida, text="Qxi:")
                self.label_qxi.place(relx=0.1, rely=0.1, anchor='w')

                self.entry_qxi = ctk.CTkEntry(self.janela_adicionar_forca_distribuida)
                self.entry_qxi.place(relx=0.3, rely=0.1, anchor='w')

                self.label_qyi = ctk.CTkLabel(self.janela_adicionar_forca_distribuida, text="Qyi:")
                self.label_qyi.place(relx=0.1, rely=0.2, anchor='w')

                self.entry_qyi = ctk.CTkEntry(self.janela_adicionar_forca_distribuida)
                self.entry_qyi.place(relx=0.3, rely=0.2, anchor='w')

                self.label_qxj = ctk.CTkLabel(self.janela_adicionar_forca_distribuida, text="Qxj:")
                self.label_qxj.place(relx=0.1, rely=0.3, anchor='w')

                self.entry_qxj = ctk.CTkEntry(self.janela_adicionar_forca_distribuida)
                self.entry_qxj.place(relx=0.3, rely=0.3, anchor='w')

                self.label_qyj = ctk.CTkLabel(self.janela_adicionar_forca_distribuida, text="Qyj:")
                self.label_qyj.place(relx=0.1, rely=0.4, anchor='w')

                self.entry_qyj = ctk.CTkEntry(self.janela_adicionar_forca_distribuida)
                self.entry_qyj.place(relx=0.3, rely=0.4, anchor='w')

                def set_forca_distribuida(id_elemento):
                    Qxi = float(self.entry_qxi.get()) if self.entry_qxi.get() != '' else 0.0
                    Qyi = float(self.entry_qyi.get()) if self.entry_qyi.get() != '' else 0.0
                    Qxj = float(self.entry_qxj.get()) if self.entry_qxj.get() != '' else 0.0
                    Qyj = float(self.entry_qyj.get()) if self.entry_qyj.get() != '' else 0.0

                    self.carga_distribuida.carga_dist(id_elemento, Qxi, Qyi, Qxj, Qyj)

                    print(self.carga_distribuida.carregamento)

                    self.inserir_info_elem.remove()
                    self.canvas.draw()
                    self.fig.canvas.mpl_disconnect(self.inserir_carga_elemento)

                    if self.janela_adicionar_forca_distribuida != None and self.janela_adicionar_forca_distribuida.winfo_exists():
                        
                        self.janela_adicionar_forca_distribuida.destroy()

                self.bt_ok = ctk.CTkButton(self.janela_adicionar_forca_distribuida, text="OK", command= lambda: set_forca_distribuida(id_elemento))
                self.bt_ok.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)

                def fechar_forca_distribuida():
                    self.inserir_info_elem.remove()
                    self.fig.canvas.mpl_disconnect(self.inserir_carga_elemento)
                    self.canvas.draw()

                    if self.janela_adicionar_forca_distribuida != None and self.janela_adicionar_forca_distribuida.winfo_exists():
                        self.janela_adicionar_forca_distribuida.destroy()

                self.bt_cancelar = ctk.CTkButton(self.janela_adicionar_forca_distribuida, text="Cancelar", command= fechar_forca_distribuida)
                self.bt_cancelar.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)

            else:

                self.janela_adicionar_forca_distribuida.grab_set()
                self.janela_adicionar_forca_distribuida.focus_set()


        else:
            messagebox.showerror("Erro", "Não foi possível inserir a carga. O ponto selecionado não pertence a um elemento.")
            self.fig.canvas.mpl_disconnect(self.inserir_carga_elemento)
            
        
    def aplicar_forcas(self, event):
        if self.no.CoordNo == []:
            messagebox.showerror("Erro", "Nenhum nó foi inserido")

        elif event == 'Aplicada':

            if self.elemento_ativado == True:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            self.inserir_info_no =self.ax.annotate("Clique no nó para inserir a força", xy=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25), xytext=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25), color='black', fontsize=10)
            self.canvas.draw()
            
            self.adicionar_forca = self.canvas.mpl_connect("button_press_event", self.capturar_ponto_forca)
            
        elif event == 'Distribuída':

            if self.elemento_ativado == True:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            
            self.inserir_info_elem =self.ax.annotate("Clique no elemento para inserir a carga distribuida", xy=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25), xytext=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25), color='black', fontsize=10)
            self.canvas.draw()

            self.inserir_carga_elemento = self.canvas.mpl_connect("pick_event", self.capturar_elemento_cargas)

    
    def aplicar_prop_elemento(self, event):
        if self.no.CoordNo == []:
            messagebox.showerror("Erro", "Nenhum elemento foi inserido")

        elif event == 'Concreto':

            if self.elemento_ativado == True:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            self.tipo_elem = 'Concreto'

            self.inserir_info_elem =self.ax.annotate("Clique no elemento para inserir a propriedade", xy=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25), xytext=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25), color='black', fontsize=10)
            self.canvas.draw()

            self.inserir_prop_elem = self.fig.canvas.mpl_connect("pick_event", self.capturar_elemento_prop_elem)

        elif event == 'Aço':

            if self.elemento_ativado == True:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()
            
            self.tipo_elem = 'Aço'

            self.inserir_info_elem =self.ax.annotate("Clique no elemento para inserir a propriedade",
                                                     xy=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                     xytext=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25), color='black', fontsize=10)
            self.canvas.draw()

            self.inserir_prop_elem = self.fig.canvas.mpl_connect("pick_event", self.capturar_elemento_prop_elem)


        elif event == 'Genérico':

            if self.elemento_ativado:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            self.tipo_elem = 'Genérico'

            self.inserir_info_elem =self.ax.annotate("Clique no elemento para inserir a propriedade",
                                                     xy=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                     xytext=(self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                     color='black',
                                                     fontsize=10)
            self.canvas.draw()

            self.inserir_prop_elem = self.fig.canvas.mpl_connect("pick_event", self.capturar_elemento_prop_elem)
    
    def aplicar_prop_secao(self, event):
        if self.no.CoordNo == []:
            messagebox.showerror("Erro", "Nenhum elemento foi inserido")

        elif event == 'Retangular':

            if self.elemento_ativado:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            self.tipo_secao = 'Retangular'

            self.inserir_info_elem = self.ax.annotate("Clique no elemento para inserir a propriedade da seção",
                                                      xy = (self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                      xytext = (self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                      color = 'black',
                                                      fontsize = 10)
            self.canvas.draw()

            self.inserir_prop_secao = self.fig.canvas.mpl_connect("pick_event", self.capturar_elemento_prop_secao)


        elif event == 'Circular':

            if self.elemento_ativado:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            self.tipo_secao = 'Circular'

            self.inserir_info_elem = self.ax.annotate("Clique no elemento para inserir a propriedade da seção",
                                                      xy = (self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                      xytext = (self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                      color = 'black',
                                                      fontsize = 10)
            self.canvas.draw()

            self.inserir_prop_secao = self.fig.canvas.mpl_connect("pick_event", self.capturar_elemento_prop_secao)

        elif event == 'Genérico':

            if self.elemento_ativado:
                self.elemento_ativado = False
                self.menu.entryconfig('Elemento: ON', label='Elemento: OFF')
                self.fig.canvas.mpl_disconnect(self.inserir)
                self.fig.canvas.mpl_disconnect(self.movimento)
                self.cursor.disconnect_events()

            self.tipo_secao = 'Genérico'

            self.inserir_info_elem = self.ax.annotate("Clique no elemento para inserir a propriedade da seção",
                                                      xy = (self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                      xytext = (self.ax.get_xlim()[0], self.ax.get_ylim()[1] - 0.25),
                                                      color = 'black',
                                                      fontsize = 10)
            self.canvas.draw()

            self.inserir_prop_secao = self.fig.canvas.mpl_connect("pick_event", self.capturar_elemento_prop_secao)


    def capturar_elemento_prop_elem(self, event):
        elemento = event.artist

        if elemento in self.linhas.values():
            id_elemento = list(self.linhas.values()).index(elemento) + 1

            if self.janela_prop_elemento is None or not self.janela_prop_elemento.winfo_exists():

                self.janela_prop_elemento = ctk.CTkToplevel(self.root)
                self.janela_prop_elemento.title("Propriedades do elemento")
                self.janela_prop_elemento.geometry("250x300+1+1")
                self.janela_prop_elemento.resizable(False, False)
                self.janela_prop_elemento.grab_set()
                self.janela_prop_elemento.focus_set()

                self.label_prop_elem = ctk.CTkLabel(self.janela_prop_elemento, text="E:")
                self.label_prop_elem.place(relx=0.1, rely=0.2, anchor='w')

                self.entry_prop_elem = ctk.CTkEntry(self.janela_prop_elemento, placeholder_text= 'Informe o módulo de elasticidade do elemento',
                                                    width= 200)
                self.entry_prop_elem.place(relx=0.15, rely=0.2, anchor='w')


                if self.tipo_elem == 'Concreto':
                    self.prop_elem.concreto(n_elem=id_elemento)
                    self.entry_prop_elem.insert(0, self.prop_elem.prop_elem[id_elemento])

                elif self.tipo_elem == 'Aço':
                    self.prop_elem.aco(n_elem=id_elemento)
                    self.entry_prop_elem.insert(0, self.prop_elem.prop_elem[id_elemento])

                def set_prop_elemento():
                    try:

                        if self.tipo_elem == 'Genérico':

                            E = float(self.entry_prop_elem.get()) if self.entry_prop_elem.get() != '' else 0.0
                            self.prop_elem.generico(n_elem=id_elemento, E=E)
                            #self.entry_prop_elem.insert(0, self.prop_elem.prop_elem[id_elemento])

                            self.label_ = ctk.CTkLabel(self.janela_prop_elemento, text="Propriedade genérica aplicada.")
                            self.label_.place(relx=0.5, rely=0.45, anchor=ctk.CENTER)

                        E = self.prop_elem.prop_elem

                        self.inserir_info_elem.remove()
                        self.canvas.draw()
                    except:
                        pass

                if self.tipo_elem == 'Genérico':

                    self.bt_aplicar = ctk.CTkButton(self.janela_prop_elemento, text="Aplicar", command= set_prop_elemento)
                    self.bt_aplicar.place(relx=0.5, rely=0.65, anchor=ctk.CENTER)

        
                def cancelar_prop_elemento():
                    if self.prop_elem.prop_elem == {}:
                        self.prop_elem.prop_elem.clear()

                    self.inserir_info_elem.remove()
                    self.canvas.mpl_disconnect(self.inserir_prop_elem)
                    self.canvas.draw()
                    
                    if self.janela_prop_elemento != None and self.janela_prop_elemento.winfo_exists():
                        self.janela_prop_elemento.destroy()

                def confirmar_ok():
                    E = self.prop_elem.prop_elem
                    self.inserir_info_elem.remove()
                    self.canvas.draw()

                    self.canvas.mpl_disconnect(self.inserir_prop_elem)

                    if self.janela_prop_elemento != None and self.janela_prop_elemento.winfo_exists():
                        self.janela_prop_elemento.destroy()

                self.bt_ok = ctk.CTkButton(self.janela_prop_elemento, text="Ok",
                                                 command= confirmar_ok, width=3)
                self.bt_ok.place(relx=0.6, rely=0.85, anchor='e')

                self.bt_cancelar = ctk.CTkButton(self.janela_prop_elemento, text="Cancelar",
                                                 command= cancelar_prop_elemento, width=3)
                self.bt_cancelar.place(relx=0.9, rely=0.85, anchor='e')

            else:
                self.janela_prop_elemento.grab_set()
                self.janela_prop_elemento.focus_set()

    def capturar_elemento_prop_secao(self, event):
        elemento = event.artist

        if elemento in self.linhas.values():
            id_elemento = list(self.linhas.values()).index(elemento) + 1

            if self.janela_prop_secao is None or not self.janela_prop_secao.winfo_exists():

                if self.tipo_secao == 'Retangular': #Corrigir isso

                    self.janela_prop_secao = ctk.CTkToplevel(self.root)
                    self.janela_prop_secao.title("Propriedades da seção retangular")
                    self.janela_prop_secao.geometry("250x300+1+1")
                    self.janela_prop_secao.resizable(False, False)
                    self.janela_prop_secao.grab_set()
                    self.janela_prop_secao.focus_set()

                    self.label_base = ctk.CTkLabel(self.janela_prop_secao, text="Base:")
                    self.label_base.place(relx=0.1, rely=0.1, anchor='w')

                    self.entry_base = ctk.CTkEntry(self.janela_prop_secao)
                    self.entry_base.place(relx=0.3, rely=0.1, anchor='w')

                    self.label_altura = ctk.CTkLabel(self.janela_prop_secao, text="Altura:")
                    self.label_altura.place(relx=0.1, rely=0.2, anchor='w')

                    self.entry_altura = ctk.CTkEntry(self.janela_prop_secao)
                    self.entry_altura.place(relx=0.3, rely=0.2, anchor='w')


                    def set_prop_secao():
                        base = float(self.entry_base.get()) if self.entry_base.get() != '' else 0.0
                        altura = float(self.entry_altura.get()) if self.entry_altura.get() != '' else 0.0

                        self.prop_secao.ret(base, altura, id_elemento)

                        if self.tipo_secao != None:
                            self.tipo_secao = None

                        if self.janela_prop_secao != None and self.janela_prop_secao.winfo_exists():
                            self.janela_prop_secao.destroy()

                    self.bt_ok = ctk.CTkButton(self.janela_prop_secao, text="OK", command=set_prop_secao)
                    self.bt_ok.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
                    self.bt_cancelar = ctk.CTkButton(self.janela_prop_secao, text="Cancelar", command= lambda : self.janela_prop_secao.destroy())
                    self.bt_cancelar.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)

                elif self.tipo_secao == 'Circular':

                    self.janela_prop_secao = ctk.CTkToplevel(self.root)
                    self.janela_prop_secao.title("Propriedades da seção circular")
                    self.janela_prop_secao.geometry("250x300+1+1")
                    self.janela_prop_secao.resizable(False, False)
                    self.janela_prop_secao.grab_set()
                    self.janela_prop_secao.focus_set()

                    self.label_diametro = ctk.CTkLabel(self.janela_prop_secao, text="Diâmetro:")
                    self.label_diametro.place(relx=0.1, rely=0.1, anchor='w')

                    self.entry_diametro = ctk.CTkEntry(self.janela_prop_secao)
                    self.entry_diametro.place(relx=0.35, rely=0.1, anchor='w')

                    def set_prop_secao():
                        diametro = float(self.entry_diametro.get()) if self.entry_diametro.get() != '' else 0.0

                        self.prop_secao.circ(diametro, id_elemento)

                        if self.tipo_secao != None:
                            self.tipo_secao = None

                        if self.janela_prop_secao != None and self.janela_prop_secao.winfo_exists():
                            self.janela_prop_secao.destroy()

                    self.bt_ok = ctk.CTkButton(self.janela_prop_secao, text="OK", command=set_prop_secao)
                    self.bt_ok.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
                    self.bt_cancelar = ctk.CTkButton(self.janela_prop_secao, text="Cancelar",
                                                         command=self.janela_prop_secao.destroy)
                    self.bt_cancelar.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)

                elif self.tipo_secao == 'Genérico':

                    self.janela_prop_secao = ctk.CTkToplevel(self.root)
                    self.janela_prop_secao.title("Propriedades da seção genérica")
                    self.janela_prop_secao.geometry("250x300+1+1")
                    self.janela_prop_secao.resizable(False, False)
                    self.janela_prop_secao.grab_set()
                    self.janela_prop_secao.focus_set()

                    self.label_area = ctk.CTkLabel(self.janela_prop_secao, text="Área:")
                    self.label_area.place(relx=0.1, rely=0.1, anchor='w')

                    self.entry_area = ctk.CTkEntry(self.janela_prop_secao)
                    self.entry_area.place(relx=0.3, rely=0.1, anchor='w')

                    self.label_inercia = ctk.CTkLabel(self.janela_prop_secao, text="Inércia:")
                    self.label_inercia.place(relx=0.1, rely=0.2, anchor='w')

                    self.entry_inercia = ctk.CTkEntry(self.janela_prop_secao)
                    self.entry_inercia.place(relx=0.3, rely=0.2, anchor='w')

                    def set_prop_secao():
                        area = float(self.entry_area.get()) if self.entry_area.get() != '' else 0.0
                        inercia = float(self.entry_inercia.get()) if self.entry_inercia.get() != '' else 0.0

                        self.prop_secao.generico(area, inercia, id_elemento)

                        if self.tipo_secao != None:
                            self.tipo_secao = None

                        if self.janela_prop_secao != None and self.janela_prop_secao.winfo_exists():
                            self.janela_prop_secao.destroy()

                    self.bt_ok = ctk.CTkButton(self.janela_prop_secao, text="OK", command=set_prop_secao)
                    self.bt_ok.place(relx=0.5, rely=0.6, anchor=ctk.CENTER)
                    self.bt_cancelar = ctk.CTkButton(self.janela_prop_secao, text="Cancelar",
                                                     command=self.janela_prop_secao.destroy)
                    self.bt_cancelar.place(relx=0.5, rely=0.7, anchor=ctk.CENTER)

            else:
                self.janela_prop_secao.grab_set()
                self.janela_prop_secao.focus_set()

    def resetar_elem(self):

        #Variáveis de controle
        self.ponto_inicial = None
        self.posi = None
        self.posf = None
        self.linha_temporaria = None
        self.linhas = {}
        self.pos = None
        self.pontos = None
        self.tipo_apoio = None
        self.pontos_medios = {}
        self.press = {}
        self.tipo_elem = None
        self.localizador_mult_x = 1
        self.localizador_mult_y = 1
        self.coord_x = None
        self.coord_y = None
        self.limExIn = -10
        self.limExFi = 10

        self.no.reseta_no()
        self.elem.resetar_elemento()
        self.apoio.resetar_apoios()
        self.carga_distribuida.resetar_cargas_dist()
        self.prop_elem.resetar_prop_elem()
        self.prop_secao.resetar_secao_elem()
        self.ax.clear()
        self.ax.set_xlim(self.limExIn, self.limExFi)
        self.ax.set_ylim(self.limExIn, self.limExFi)
        # Força os ticks a aparecerem em todas as unidades inteiras
        self.set_major_locator_x = self.ax.xaxis.set_major_locator(MultipleLocator(self.localizador_mult_x))
        self.set_major_locator_y = self.ax.yaxis.set_major_locator(MultipleLocator(self.localizador_mult_y))
        self.ax.grid(self.grid_ativado)


        self.canvas.draw()
        

    def ajuste_grid(self):

        if self.janela_ajuste_grid is None or not self.janela_ajuste_grid.winfo_exists():

            self.janela_ajuste_grid = ctk.CTkToplevel(self.root)
            self.janela_ajuste_grid.title('Ajuste grid')
            self.janela_ajuste_grid.geometry('200x200+1+1')
            self.janela_ajuste_grid.resizable(False,False)
            self.janela_ajuste_grid.grab_set()
            self.janela_ajuste_grid.focus_set()

            self.lb_ajuste_x = ctk.CTkLabel(self.janela_ajuste_grid, text = 'X:')
            self.lb_ajuste_x.place(relx = 0.15, rely = 0.1)
            
            self.entry_ajuste_x = ctk.CTkEntry(self.janela_ajuste_grid, placeholder_text= f'{self.localizador_mult_x}m')
            self.entry_ajuste_x.place(relx = 0.25, rely = 0.1, relwidth = 0.5)

            self.lb_ajuste_y = ctk.CTkLabel(self.janela_ajuste_grid, text = 'Y:')
            self.lb_ajuste_y.place(relx = 0.15, rely = 0.4)
            
            self.entry_ajuste_y = ctk.CTkEntry(self.janela_ajuste_grid, placeholder_text= f'{self.localizador_mult_y}m')
            self.entry_ajuste_y.place(relx = 0.25, rely = 0.4, relwidth = 0.5)

            def get_ajustes():
                self.localizador_mult_x = float(self.entry_ajuste_x.get()) if self.entry_ajuste_x.get() != '' else self.localizador_mult_x
                
                self.localizador_mult_y = float(self.entry_ajuste_y.get()) if self.entry_ajuste_y.get() != '' else self.localizador_mult_y

                self.set_major_locator_x = self.ax.xaxis.set_major_locator(MultipleLocator(self.localizador_mult_x))
                
                self.set_major_locator_y = self.ax.yaxis.set_major_locator(MultipleLocator(self.localizador_mult_y))

                self.canvas.draw()

                if self.janela_ajuste_grid != None:
                    self.janela_ajuste_grid.destroy()

            self.bt_ok = ctk.CTkButton(self.janela_ajuste_grid, text='Ok', command= get_ajustes, anchor= ctk.CENTER)
            self.bt_ok.place(relx = 0.125, rely = 0.65)
        
        else:
            
            self.janela_ajuste_grid.grab_set()
            self.janela_ajuste_grid.focus_set()

    def run(self, event):
        from modulos.matrizrigidez import resultado
    
        resultado.executar()
        
    def fechar_com_seguranca(self):
        try:
            self.canvas.get_tk_widget().quit()
        except:
            pass

        #self.root.destroy()
        self.root.quit()


if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = StrucFrame(root)
        root.protocol("WM_DELETE_WINDOW", app.fechar_com_seguranca)  # <-- isso é importante
        try:
            root.mainloop()
        except:
            pass
    except ValueError as e:
        print(e)