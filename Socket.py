import socket
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

storeName = getStoreName()

# Verifica a conexão com a Internet antes de abrir o aplicativo
if check_internet_connection(): 

    # Conexão estabelecida e nenhum bloqueio encontrado, inicie o aplicativo
    app = PixCheckerApp(storeName)
    app.mainloop()
else:
    messagebox.showerror("Erro de conexão", "Não foi possível conectar à Internet. Verifique sua conexão e tente novamente.")
