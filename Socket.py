import socket
import os
import psutil
from tkinter import messagebox
from Simpliest import PixCheckerApp

def getStoreName():
    with open('credentials/storename.txt') as f:
        loja = f.readlines()
        return loja[0]

def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False

def check_single_instance():
    current_pid = os.getpid()
    for process in psutil.process_iter(['name', 'cmdline']):
        try:
            process_name = process.info['name']
            process_cmdline = process.info['cmdline']
            if "pixchecker" in process_name and "python" in process_cmdline:
                pid = process.pid
                if pid != current_pid:
                    # Outra instância do aplicativo já está em execução, exibe uma mensagem de erro e sai
                    messagebox.showerror("Erro", "O aplicativo Pix Checker já está em execução.")
                    exit()
        except (psutil.Error, psutil.AccessDenied):
            continue

storeName = getStoreName()

# Verifica a conexão com a Internet antes de abrir o aplicativo
if check_internet_connection():
    # Verifica se já existe uma instância do aplicativo em execução
    check_single_instance()

    # Conexão estabelecida e nenhum bloqueio encontrado, inicie o aplicativo
    app = PixCheckerApp(storeName)
    app.mainloop()
else:
    messagebox.showerror("Erro de conexão", "Não foi possível conectar à Internet. Verifique sua conexão e tente novamente.")
