import datetime
import logging
import os
import re
import sys
from tkinter import CENTER, NO, ttk, messagebox
import tkinter
from PIL import ImageTk, Image
from bs4 import BeautifulSoup
from playsound import playsound
from customtkinter.windows.ctk_tk import CTk
import customtkinter
import html2text
from GmailHandler import get_message, get_service, search_message
from MongoHandler import add_pix, return_pix_daily

logging.basicConfig(filename='pixlogs.log', encoding='utf-8')

customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class PixCheckerApp(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 360

    def __init__(self, storeName):
        super().__init__()

        self.title(storeName)
        self.iconbitmap("assets/unlock_pix.ico")
        self.geometry(f"{PixCheckerApp.WIDTH}x{PixCheckerApp.HEIGHT}")
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

        pixTable.column("#0", width=5, stretch=NO)
        pixTable.column("pixID", anchor=CENTER, width=20)
        pixTable.column("pixNome", anchor=CENTER, width=300)
        pixTable.column("pixValor", anchor=CENTER, width=200)

        pixTable.heading("#0", text="", anchor=CENTER)
        pixTable.heading("pixID", text="ID", anchor=CENTER)
        pixTable.heading("pixNome", text="Nome", anchor=CENTER)
        pixTable.heading("pixValor", text="Valor", anchor=CENTER)
        pixTable.grid(column=1, row=0, sticky="nwe", padx=35, pady=35)

        self.bind('<Escape>', lambda e: close_application())

        # ============ Inicializando variáveis ===========

        self.quantidadeEmailAtual = 0
        self.runThread = 1
        self.autenticated = False
        self.count = 0
        self.firstInit = 1

        current_time = datetime.datetime.now()
        self.buscaAno = int(current_time.year)
        self.buscaMes = int(current_time.month)
        self.buscaMesStr = datetime.date.today().month
        self.buscaDia = int(current_time.day)

        # ======== Funções =========

        def qtdEmailAt():
            if self.runThread == 1:
                service = get_service()
                list_ids = []
                busca = f'from:todomundo@nubank.com.br recebeu transferência after:{self.buscaAno}/{self.buscaMes}/{self.buscaDia}'
                list_ids = search_message(service, 'me', busca)
                self.quantidadeEmailAtual = len(list_ids)
                if self.quantidadeEmailAtual > 0:
                    todayPix() 

                self.after(5000, qtdEmailAt)

        def todayPix():
            service = get_service()
            busca = f'from:todomundo@nubank.com.br recebeu transferência after:{self.buscaAno}/{self.buscaMes}/{self.buscaDia}'
            list_ids = search_message(service, 'me', busca)

            for ids in list_ids:
                email = get_message(service, 'me', ids)
                soup = BeautifulSoup(email, "html.parser")
                clean_soup_string = soup.text.replace('=FA', 'ú').replace('=E7', 'ç').replace('=E3', 'ã').replace('=EA', 'ê').replace('=E1', 'á').replace('=E0', 'à').replace('=E2', 'â').replace('ED', 'í').replace('=', '').replace('JAN às ', '').replace("JAN às ", '').replace('às', '').replace('JAN', '').replace('FEV', '').replace('MAR', '').replace('ABR', '').replace('MAI', '').replace('JUN', '').replace('JUL', '').replace('AGO', '').replace('SET', '').replace('OUT', '').replace('NOV', '').replace('DEZ', '')

                match = re.search(r"recebeu uma transferência de (.+?) R\$|recebeu uma transferência pelo Pix de (.+?) e o valor", clean_soup_string)
                nomesobrenome = match.group(1) if match and match.group(1) else match.group(2) if match and match.group(2) else 'VER NO APP'

                match2 = re.search(r"R\$ (\d+,\d{2})|R\$ (\d{1,3}(?:\.\d{3})*(?:,\d{2}))", clean_soup_string)
                valor = match2.group(1) if match2 and match2.group(1) else match2.group(2) if match2 and match2.group(2) else 'VER NO APP'

                add_pix("pixchecker", storeName, [nomesobrenome, valor])

            table_insert_daily()
            self.state('zoomed')  # Maximizar a janela

        def table_insert_daily():
            self.count = 0
            result = return_pix_daily("pixchecker", storeName, self.buscaDia, self.buscaMes, self.buscaAno)
            pixTable.delete(*pixTable.get_children())
            pixTable.update()
            for data in result:
                self.count += 1
                pixTable.insert(parent='', index='end', iid=f'{self.count + 1}', values=(self.count, data['nome'], data['valor']))
            playsound('assets/shineupdate.mp3')

        def startThread():
            self.runThread = 1
            qtdEmailAt()

        def stopThread():
            self.runThread = 0

        table_insert_daily()

        def change_mode():
            if self.switch_2.get() == 1:
                startThread()
            else:
                stopThread()

        def close_application():
            self.destroy()

        self.switch_2 = customtkinter.CTkSwitch(master=self.frame_right,
                                                text="",
                                                command=change_mode)
        self.switch_2.grid(row=8, column=0, pady=10, padx=20, sticky="w")
        self.switch_2.toggle()

        self.buttonClear = customtkinter.CTkButton(master=self.frame_right,
                                                   text="Fechar",
                                                   command=close_application)
        self.buttonClear.grid(row=8, column=1, pady=20, padx=10, sticky="e")