# from curses import window
from distutils.command.build_scripts import first_line_re
import threading
from tkinter import CENTER, NO, ttk
from GmailHandler import get_message, get_service, search_message
from MongoHandler import add_pix, return_pix, return_qtd_docs  
import customtkinter
import html2text
from bs4 import BeautifulSoup
import re
import datetime 
from playsound import playsound



customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 360

    def __init__(self):
        super().__init__()
                
        def getStoreName():
            print("getStoreName() inicializada")
            with open('credentials/storename.txt') as f:
                loja = f.readlines()
                return loja[0]
        global storeName
        storeName = getStoreName()
        self.title(storeName)
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_right ============

        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.frame_right.rowconfigure(7, weight=20)
        self.frame_right.columnconfigure((0, 1, 2), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        # ============ frame_right ============
        pixTable = ttk.Treeview(self)
        pixTable['columns'] = ('pixID','pixNome', 'pixDia', 'pixMes', 'pixValor')

        pixTable.column("#0", width=0,  stretch=NO)
        pixTable.column("pixID",anchor=CENTER, width=1)
        pixTable.column("pixNome",anchor="w",width=160)
        pixTable.column("pixDia",anchor=CENTER,width=1)
        pixTable.column("pixMes",anchor=CENTER,width=10)
        pixTable.column("pixValor",anchor=CENTER,width=20)

        pixTable.heading("#0",text="",anchor=CENTER)
        pixTable.heading("pixID",text="ID",anchor=CENTER)
        pixTable.heading("pixNome",text="Nome",anchor="w")
        pixTable.heading("pixDia",text="Dia",anchor=CENTER)
        pixTable.heading("pixMes",text="Mes",anchor=CENTER)
        pixTable.heading("pixValor",text="Valor",anchor=CENTER)
        pixTable.grid(column=1, row=0, sticky="nwe", padx=35, pady=35)

        # ============ Inicializando variáveis ===========
        
        global runThread
        runThread = 1
        
        
        global count
        count = 0
        
        global qtdPixAntiga
        qtdPixAntiga = 0

        threading.Timer.daemon = True
        
        global buscaAno
        global buscaMes
        global buscaDia
        current_time = datetime.datetime.now() 
        buscaAno = int(current_time.year)
        buscaMes = str(current_time.month)
        buscaDia = int(current_time.day)

        # ======== Funções =========
        def check_for_pix():
            global qtdPixAntiga
            qtdPixNovo = return_qtd_docs("pixchecker", storeName)
            if (qtdPixAntiga != qtdPixNovo):
                table_insert_daily()
                qtdPixAntiga = qtdPixNovo
            else:
                print("Nada encontrado")
            threading.Timer(5.0, check_for_pix).start()

        def table_insert_daily():
            print("table_insert_daily() inicializada")
            global count
            global firstInit
            if count > 0:
                count = 0
            result = return_pix("pixchecker", storeName, "dia", buscaDia)
            pixTable.delete(*pixTable.get_children())
            pixTable.update()
            for data in result:
                pixTable.insert(parent='', index='end', iid=f'{count + 1}', values=(count+1, data['nome'], data['dia'], data['mes'], data['valor']))
                count += 1
            playsound('./shineupdate.mp3')
            return_qtd_docs("pixchecker", storeName)

        def startThread():
            print('\n')
            print("startThread() inicializada")
            global runThread
            runThread = 1
            check_for_pix()

        
        def stopThread():
            print('\n')
            print("stopThread() inicializada")
            global runThread
            runThread = 0
    
        def change_mode():
            print('\n')
            print("change_mode() inicializada")
            if self.switch_2.get() == 1: 
                startThread()
            else:
                stopThread()


        self.switch_2 = customtkinter.CTkSwitch(master=self.frame_right, 
                                                text="",
                                                command=change_mode)
        self.switch_2.grid(row=8, column=0, pady=10, padx=20, sticky="w")
        self.switch_2.toggle()
        
    def on_closing(self, event=0):
        self.destroy()



if __name__ == "__main__":
    app = App()
    app.mainloop()