import threading
import time
import os, signal
from tkinter import CENTER, NO, ttk
import tkinter
from GmailHandler import get_message, get_service, search_message
from MongoHandler import add_pix, return_pix_daily
import customtkinter
import html2text
from bs4 import BeautifulSoup
import re
import datetime 
from playsound import playsound
from tkinter import *
from tkinter import font, messagebox
from PIL import ImageTk, Image 
import time
import sys
import logging
logging.basicConfig(filename='pixlogs.log', encoding='utf-8')


from customtkinter.windows.ctk_tk import CTk



customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 360

    def __init__(self):
        super().__init__()
                
        self.title(storeName)
        self.iconbitmap("assets/unlock_pix.ico")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        #self.protocol("WM_DELETE_WINDOW", self.iconify) # call .on_closing() when app gets closed
        menubar = tkinter.Menu(self)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        self.config(menu=menubar)

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
        pixTable['columns'] = ('pixID', 'pixNome', 'pixValor')

        pixTable.column("#0", width=5,  stretch=NO)
        pixTable.column("pixID",anchor=CENTER, width=20)
        pixTable.column("pixNome",anchor=CENTER, width=300)
        pixTable.column("pixValor",anchor=CENTER,width=200)

        pixTable.heading("#0",text="",anchor=CENTER)
        pixTable.heading("pixID",text="ID",anchor=CENTER)
        pixTable.heading("pixNome",text="Nome",anchor=CENTER)
        pixTable.heading("pixValor",text="Valor",anchor=CENTER)
        pixTable.grid(column=1, row=0, sticky="nwe", padx=35, pady=35)

        self.bind('<Escape>', lambda e: self.destroy())

        # ============ Inicializando variáveis ===========
        
        global quantidadeEmailAtual
        quantidadeEmailAtual = 0
        
        global runThread
        runThread = 1
        
        global autenticated
        autenticated = False
        
        global count
        count = 0
        
        global firstInit
        firstInit = 1
        threading.Timer.daemon = True
        
        global buscaAno
        global buscaMes
        global buscaDia
        global buscaMesStr
        current_time = datetime.datetime.now() 
        buscaAno = int(current_time.year)
        buscaMes = int(current_time.month)
        buscaMesStr = datetime.date.today().month
        buscaDia = int(current_time.day)

        # ======== Funções =========

        def qtdEmailAt():
            global quantidadeEmailAtual
            if runThread == 1:
                service = get_service()
                list_ids = []
                busca = f'from:todomundo@nubank.com.br recebeu transferência after:{buscaAno}/{buscaMes}/{buscaDia}'
                list_ids = search_message(service, 'me', busca)
                quantidadeEmailAtual = 0
                for ids in list_ids:
                    quantidadeEmailAtual += 1
                (f'Qtd Email: {quantidadeEmailAtual} qtdEmailAt()')
                if quantidadeEmailAtual > 0:
                    todayPix()
                
                threading.Timer(5.0, qtdEmailAt).start()

        def todayPix():
            i = 0
            pixInfo = []
            email = []
            soup = []
            clean_soup = []
            h = html2text.HTML2Text()
            h.ignore_links = True
            list_ids = []
            service = get_service()
            allPix = []
            busca = f'from:todomundo@nubank.com.br recebeu transferência after:{buscaAno}/{buscaMes}/{buscaDia}'
            list_ids = search_message(service, 'me', busca)

        
            nomesobrenome=[]
            for ids in list_ids:
                email.append(get_message(service, 'me', list_ids[i]))
                email[0] = email[0].replace("\r\n", '').replace('=FA', 'ú').replace('=E7', 'ç').replace('=E3', 'ã').replace('=EA', 'ê').replace('=E1', 'á').replace('=E0', 'à').replace('=', '').replace('E2', 'â').replace("=", '')
                # PEGAR VALORES DO PIX
                soup = BeautifulSoup(email[0], "html.parser")
                clean_soup.append(soup.text.replace('=FA', 'ú').replace('=E7', 'ç').replace('=E3', 'ã').replace('=EA', 'ê').replace('=E1', 'á').replace('=E0', 'à').replace('=E2', 'â').replace('ED', 'í').replace('=', '').replace('JAN às ', '').replace("JAN às ", '').replace('às', '').replace('JAN', '').replace('FEV', '').replace('MAR', '').replace('ABR', '').replace('MAI', '').replace('JUN', '').replace('JUL', '').replace('AGO', '').replace('SET', '').replace('OUT', '').replace('NOV', '').replace('DEZ', ''))
                clean_soup_string = clean_soup[0]
                nomesobrenome = re.search(r"recebeu uma transferência de (.+?) R\$", clean_soup_string).group(1)
                valor = re.search(r"R\$ (\d+,\d{2})", clean_soup_string).group(1)
                pixInfo = re.compile("").sub("", clean_soup_string[0]).split()
                pixInfo.pop()
                lengthDia = len(str(buscaDia))
                if(len(str(buscaDia)) < 10):
                    lengthDia = 2
                allPix.append(nomesobrenome)
                allPix.append(valor)
                add_pix("pixchecker", storeName, allPix)
                pixadd = f"Pix adicionado {allPix}"
                logging.info(pixadd)
                allPix.clear()
                clean_soup.clear()
                email.clear()
                i += 1
            i = 0

            table_insert_daily()
            return allPix
        
        def table_insert_daily():
            global count
            if count > 0:
                count = 0
            result = return_pix_daily("pixchecker", storeName, buscaDia, buscaMes, buscaAno)
            pixTable.delete(*pixTable.get_children())
            pixTable.update()
            for data in result:
                pixTable.insert(parent='', index='end', iid=f'{count + 1}', values=(count+1, data['nome'], data['valor']))
                count += 1
            playsound('assets/shineupdate.mp3')

        

        def startThread():
            global runThread
            runThread = 1
            qtdEmailAt()
        
        def stopThread():
            global runThread
            runThread = 0

        table_insert_daily()
        def change_mode():
            if self.switch_2.get() == 1: 
                startThread()
            else:
                stopThread()


        self.switch_2 = customtkinter.CTkSwitch(master=self.frame_right, 
                                                text="",
                                                command=change_mode)
        self.switch_2.grid(row=8, column=0, pady=10, padx=20, sticky="w")
        self.switch_2.toggle()
        
        self.buttonClear = customtkinter.CTkButton(master=self.frame_right,
                                                text="Fechar",
                                                command=self.destroy)
        self.buttonClear.grid(row=8, column=1, pady=20, padx=10, sticky="e")




if __name__ == "__main__":
    global storeName
    
    def getStoreName():
        with open('credentials/storename.txt') as f:
            loja = f.readlines()
            return loja[0]
    storeName = getStoreName()

    app = App()
    app.mainloop()