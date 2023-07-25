import socket

def simulate_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind(('localhost', port))
        server_socket.listen(1)
        print(f"Servidor simulado na porta {port} iniciado.")
        while True:
            connection, address = server_socket.accept()
            print(f"Conexão estabelecida com {address}")
            connection.close()
    except Exception as e:
        print(f"Erro ao iniciar o servidor na porta {port}: {e}")
    finally:
        server_socket.close()
        print(f"Servidor simulado na porta {port} encerrado.")

# Porta a ser simulada (pode ser a mesma porta que você está testando no seu programa principal)
port_to_simulate = 65535

# Executando o servidor fictício para simular a porta em uso
simulate_server(port_to_simulate)
