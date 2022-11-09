# from curses import window
from distutils.command.build_scripts import first_line_re
import threading
import time
from tkinter import CENTER, NO, ttk
import tkinter
from GmailHandler import get_message, get_service, search_message
from MongoHandler import add_pix, check_license, return_pix, return_pix_daily, return_qtd_docs  
import customtkinter
import html2text
from bs4 import BeautifulSoup
import re
import datetime 
from playsound import playsound
from tkinter import *
from tkinter import font
from PIL import ImageTk, Image 
import time
import sys
import logging
logging.basicConfig(filename='pixlogs.log', encoding='utf-8', level=logging.DEBUG)


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
        self.protocol("WM_DELETE_WINDOW", self.iconify) # call .on_closing() when app gets closed
        menubar = tkinter.Menu(self)
        filemenu = tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Em construção")
        menubar.add_cascade(label="Filtrar", menu=filemenu)
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
        global buscaMesInt
        current_time = datetime.datetime.now() 
        buscaAno = int(current_time.year)
        buscaMes = str(current_time.month)
        buscaMesInt = datetime.date.today().month
        buscaDia = int(current_time.day)

        # ======== Funções =========

        def qtdEmailAt():
            global quantidadeEmailAtual
            if runThread == 1:
                ('Buscando novos PIXs')
                service = get_service()
                list_ids = []
                busca = f'from:todomundo@nubank.com.br recebeu transferência after:{buscaAno}/{buscaMes}/{buscaDia}'
                list_ids = search_message(service, 'me', busca)
                quantidadeEmailAtual = 0
                for ids in list_ids:
                    quantidadeEmailAtual += 1
                (f'Qtd Email: {quantidadeEmailAtual} qtdEmailAt()')
                if quantidadeEmailAtual > 0:
                    ('PIX RECEBIDO!')
                    todayPix()
                else:
                    ('NENHUM PIX ENCONTRADO')
                
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
            mes = 15
            dia = 14
            allPix = []
            busca = f'from:todomundo@nubank.com.br recebeu transferência after:{buscaAno}/{buscaMes}/{buscaDia}'
            list_ids = search_message(service, 'me', busca)

            tag = "ng"
            
            # regex to extract required strings
            reg_str = tag + ">(.*?)</" + "strong" + ">"
            for ids in list_ids:
                email.append(get_message(service, 'me', list_ids[i]))
                
                # PEGAR VALORES DO PIX
                res = re.findall(reg_str, email[i])
                nome = BeautifulSoup(res[0], "html.parser")
                res[0] = nome.text.replace('=FA', 'ú').replace('=E7', 'ç').replace('=E3', 'ã').replace('=EA', 'ê').replace('=E1', 'á').replace('=E0', 'à').replace('=', '').replace('E2', 'â')

                soup = BeautifulSoup(email[i], "html.parser")
                clean_soup.append(soup.text.replace('=FA', 'ú').replace('=E7', 'ç').replace('=E3', 'ã').replace('=EA', 'ê').replace('=E1', 'á').replace('=E0', 'à').replace('=', '').replace('E2', 'â'))
                pixInfo = re.compile("").sub("", clean_soup[i]).split()
                res.append(int(pixInfo[dia]))
                mes = getMonthInt(pixInfo[mes])
                res.append(mes)
                allPix.append(res)
                i += 1
            i = 0
            if allPix[i][2] == "Ouvidoria":
                allPix[i].pop(2)
            for pix in allPix:
                if (len(allPix[i])) == 3:
                    allPix[i].insert(0, "SOMENTE NO APP")
                if (allPix[i][1]) == "Ouvidoria":
                    allPix[i].pop(1)
                    allPix[i].insert(0, "SOMENTE NO APP")
                if allPix[i][2] == "Ouvidoria":
                    allPix[i].pop(2)
                i += 1
            logging.debug(allPix)
            add_pix("pixchecker", storeName, allPix)
            table_insert_daily()
            
            return allPix
        
        def getMonthInt(mes):
            if mes == "JAN":
                return 1
            elif mes == "FEV":
                return 2
            elif mes == "MAR":
                return 3
            elif mes == "ABR":
                return 4
            elif mes == "MAI":
                return 5
            elif mes == "JUN":
                return 6
            elif mes == "JUL":
                return 7
            elif mes == "AGO":
                return 8
            elif mes == "SET":
                return 9
            elif mes == "OUT":
                return 10
            elif mes == "NOV":
                return 11
            elif mes == "DEZ":
                return 12
            else:
                return 99
            
        def table_insert_daily():
            global count
            if count > 0:
                count = 0
            result = return_pix_daily("pixchecker", storeName, buscaDia, buscaMesInt, buscaAno)
            pixTable.delete(*pixTable.get_children())
            pixTable.update()
            for data in result:
                pixTable.insert(parent='', index='end', iid=f'{count + 1}', values=(count+1, data['nome'], data['dia'], data['mes'], data['valor']))
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
    isValid = False
    def getStoreName():
        with open('credentials/storename.txt') as f:
            loja = f.readlines()
            return loja[0]
    
    storeName = getStoreName()
    def getLicense():
        with open('credentials/storename.txt') as f:
            store = f.readlines()
            store = store[0]
        with open('credentials/license.txt') as l:
            license = l.readlines()
            license = license[0]
        licenseKey = license+storeName
        return check_license("licenses", storeName, licenseKey)

    w=Tk()

    #Using piece of code from old splash screen
    width_of_window = 427
    height_of_window = 250
    screen_width = w.winfo_screenwidth()
    screen_height = w.winfo_screenheight()
    x_coordinate = (screen_width/2)-(width_of_window/2)
    y_coordinate = (screen_height/2)-(height_of_window/2)
    w.geometry("%dx%d+%d+%d" %(width_of_window,height_of_window,x_coordinate,y_coordinate))
    #w.configure(bg='#ED1B76')
    w.overrideredirect(1) #for hiding titlebar

    Frame(w, width=427, height=250, bg='#272727').place(x=0,y=0)
    label1=Label(w, text='    PIXCHECKER', fg='white', bg='#272727') #decorate it 
    label1.configure(font=("Game Of Squids", 24, "bold"))   #You need to install this font in your PC or try another one
    label1.place(x=80,y=90)

    label2=Label(w, text='Validando licença...', fg='white', bg='#272727') #decorate it 
    label2.configure(font=("Calibri", 11))
    label2.place(x=10,y=215)

    #making animation

    image_a=ImageTk.PhotoImage(Image.open('assets/c2.png'))
    image_b=ImageTk.PhotoImage(Image.open('assets/c1.png'))

        #5loops
    l1=Label(w, image=image_a, border=0, relief=SUNKEN).place(x=180, y=145)
    l2=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=200, y=145)
    l3=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=220, y=145)
    l4=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=240, y=145)
    w.update_idletasks()
    time.sleep(0.5)

    l1=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=180, y=145)
    l2=Label(w, image=image_a, border=0, relief=SUNKEN).place(x=200, y=145)
    l3=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=220, y=145)
    l4=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=240, y=145)
    w.update_idletasks()
    time.sleep(0.5)

    l1=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=180, y=145)
    l2=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=200, y=145)
    l3=Label(w, image=image_a, border=0, relief=SUNKEN).place(x=220, y=145)
    l4=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=240, y=145)
    w.update_idletasks()
    time.sleep(0.5)

    l1=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=180, y=145)
    l2=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=200, y=145)
    l3=Label(w, image=image_b, border=0, relief=SUNKEN).place(x=220, y=145)
    l4=Label(w, image=image_a, border=0, relief=SUNKEN).place(x=240, y=145)
    w.update_idletasks()
    time.sleep(0.5)
    isValid = getLicense()
    if(isValid == True):
        w.destroy()
        app = App()
        app.mainloop()
        
    else:
        errorApp = customtkinter.CTk()
        errorApp.geometry("330x110")
        errorApp.title("Erro na validação da licença")
        w.destroy()
        errorApp.iconbitmap("assets/lock_pix.ico")
        def button_function():
            exit()

        # Use CTkButton instead of tkinter Button
        label = customtkinter.CTkLabel(master=errorApp, text="Regularize sua licensa para \ncontinuar utilizando nosso software!")
        label.place(relx=0.5, rely=0.22, anchor=customtkinter.CENTER)

        button = customtkinter.CTkButton(master=errorApp, text="Licença inválida", command=button_function)
        button.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)
        errorApp.mainloop()

    w.mainloop()