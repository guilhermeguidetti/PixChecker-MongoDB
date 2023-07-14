import socket
import threading
from tkinter import CENTER, NO, messagebox, ttk
import tkinter
from GmailHandler import create_message, get_message, get_service, search_message, send_message
from MongoHandler import add_pix, return_pix_daily
import customtkinter
import html2text
from bs4 import BeautifulSoup
import re
import datetime 
from playsound import playsound
import logging
<<<<<<< Updated upstream
logging.basicConfig(filename='pixlogs.log', encoding='utf-8')
=======
import pystray
from PIL import Image
import pygetwindow as gw

logging.basicConfig(filename='pixlogs.log', encoding='utf-8', level=logging.WARNING)
>>>>>>> Stashed changes

customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):

    WIDTH = 780
    HEIGHT = 330

    def __init__(self):
        super().__init__()
                
        self.title(storeName)
        self.iconbitmap("assets/unlock_pix.ico")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
<<<<<<< Updated upstream
        #self.protocol("WM_DELETE_WINDOW", self.iconify) # call .on_closing() when app gets closed
=======
        self.protocol("WM_DELETE_WINDOW", self.on_closing) # Intercepta o evento de fechar a janela
>>>>>>> Stashed changes
        menubar = tkinter.Menu(self)
        self.config(menu=menubar)

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)


        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_right ============
        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        pixTable = ttk.Treeview(self.frame_right, style='Custom.Treeview')

        # Definir o estilo personalizado para o cabeçalho e os itens da tabela
        style = ttk.Style()
        style.configure('Custom.Treeview.Heading', font=('Courier New', 16, 'bold'))
        style.configure('Custom.Treeview', font=('Courier New', 12))

        pixTable['columns'] = ('pixID', 'pixNome', 'pixValor')

        pixTable.column("#0", width=5, stretch=NO)
        pixTable.column("pixID", anchor=CENTER, width=20)
        pixTable.column("pixNome", anchor=CENTER, width=300)
        pixTable.column("pixValor", anchor=CENTER, width=200)

        pixTable.heading("#0", text="", anchor=CENTER)
        pixTable.heading("pixID", text="ID", anchor=CENTER)
        pixTable.heading("pixNome", text="Nome", anchor=CENTER)
        pixTable.heading("pixValor", text="Valor", anchor=CENTER)

        # Aplicar o estilo personalizado ao cabeçalho e aos itens da tabela
        pixTable.tag_configure('Custom.Treeview.Heading', font=('Courier New', 16, 'bold'))
        pixTable.tag_configure('Custom.Treeview', font=('Courier New', 10))

        pixTable.grid(column=0, row=0, sticky="nsew")


        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure(0, weight=1)



        self.bind('<Escape>', lambda e: self.iconify()) # Minimiza a janela ao pressionar Esc

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
            email = []
            soup = []
            clean_soup = []
            h = html2text.HTML2Text()
            h.ignore_links = True
            list_ids = []
            service = get_service()
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
                match = re.search(r"recebeu uma transferência de (.+?) e o valor|recebeu uma transferência pelo Pix de (.+?) e o valor", clean_soup_string)
                nomesobrenome = match.group(1).title() if match and match.group(1) else match.group(2).title() if match and match.group(2) else 'VER NO APP'
                match2 = re.search(r"R\$ (\d+,\d{2})|R\$ (\d{1,3}(?:\.\d{3})*(?:,\d{2}))", clean_soup_string)
                valor = match2.group(1) if match2 and match2.group(1) else match2.group(2) if match2 and match2.group(2) else 'VER NO APP'
                if(len(str(buscaDia)) < 10):
                    lengthDia = 2
                add_pix("pixchecker", storeName, [nomesobrenome, valor])
                pixadd = f"Pix adicionado {[nomesobrenome, valor]}"
                logging.info(pixadd)
                clean_soup.clear()
                email.clear()
                i += 1
            i = 0
            table_insert_daily()
        
        def table_insert_daily():
            global count
            global total_valor
            if count > 0:
                count = 0
            result = return_pix_daily("pixchecker", storeName, buscaDia, buscaMes, buscaAno)
            pixTable.delete(*pixTable.get_children())
            pixTable.update()
            total_valor = 0.0
            if result:
                for data in result:
                    pixTable.insert(parent='', index='end', iid=f'{count + 1}', values=(count+1, data['nome'], f'R$ {data["valor"]}'))
                    count += 1
                    valor = float(data['valor'].replace('.', '').replace(',', '.')) # Converte o valor para float removendo os pontos de separação de milhar e substituindo a vírgula por ponto
                    total_valor += valor

<<<<<<< Updated upstream
            # Após o loop, exiba o valor total ao lado do botão "Fechar"
            valor_total_label = customtkinter.CTkLabel(master=self.frame_right, text=f"Valor Total: R$ {total_valor:.2f}")
            valor_total_label.configure(font=('Courier New', 16, 'bold'))
            valor_total_label.grid(row=8, column=0, pady=10, padx=20)
            playsound('assets/shineupdate.mp3')
=======
                # Após o loop, exiba o valor total ao lado do botão "Fechar"
                valor_total_label = customtkinter.CTkLabel(master=self.frame_right, text=f"Valor Total: R$ {total_valor:.2f}")
                valor_total_label.configure(font=('Courier New', 16, 'bold'))
                valor_total_label.grid(row=8, column=0, pady=10, padx=20)
                playsound('assets/shineupdate.mp3')

                # Abrir a janela quando a função for chamada
                self.deiconify()

            except Exception as e:
                messagebox.showerror("Erro na atualização", "Erro ao tentar retornar os PIXs do dia.\nContate o Administrador")
                exit()
>>>>>>> Stashed changes

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

        def send_email():
            body = f'O valor total de PIXs recebido hoje foi de: R$ {total_valor:.2f}\n\nDetalhes dos PIXs:\n'
            for data in return_pix_daily("pixchecker", storeName, buscaDia, buscaMes, buscaAno):
                nome = data['nome']
                valor = data['valor']
                body += f'Nome: {nome}\nValor: R$ {valor}\n\n'
            message = create_message('me', 'gzguidetti@gmail.com', f'PIX {buscaDia}/{buscaMes}/{buscaAno}', body)
            send_message(service=get_service(), user_id='me', message=message)

        send_email_button = customtkinter.CTkButton(master=self.frame_right, text="Enviar por e-mail", command=send_email)
        send_email_button.grid(row=8, column=0, pady=10, padx=20, sticky="e")

        self.create_system_tray_icon()  # Cria o ícone da bandeja do sistema

    def on_closing(self):
        self.withdraw()  # Oculta a janela ao ser fechada
        return True

    def create_system_tray_icon(self):
        image = Image.open("assets/unlock_pix.ico")

        def toggle_window(icon, item):
            if self.winfo_viewable():
                self.withdraw()
            else:
                # Encontrar a janela existente e maximizá-la
                hwnd = gw.getWindowsWithTitle(storeName)[0].hwnd
                gw.Window(hwnd).maximize()

        menu = (pystray.MenuItem("Abrir", toggle_window), pystray.MenuItem("Sair", self.quit))
        tray_icon = pystray.Icon("PixApp", image, "PixApp", menu)

        def tray_thread():
            tray_icon.run()

        # Executa o loop de eventos da bandeja do sistema em uma thread separada
        threading.Thread(target=tray_thread, daemon=True).start()

def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False
    
if __name__ == "__main__":
    if check_internet_connection():
        global storeName
        def getStoreName():
            with open('credentials/storename.txt') as f:
                loja = f.readlines()
                return loja[0]
        
        storeName = getStoreName()

        # Verificar se uma instância já está em execução
        existing_window = gw.getWindowsWithTitle(storeName)
        if existing_window:
            # Maximizar a janela existente
            existing_window[0].maximize()
        else:
            app = App()
            app.mainloop()
    else:
        messagebox.showerror("Erro de conexão", "Não foi possível conectar à Internet. Verifique sua conexão e tente novamente.")