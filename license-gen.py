import pymongo
from datetime import datetime, timedelta
import json

def load_config(filename):
    with open(filename, "r") as file:
        config = json.load(file)
    return config

# Carregar a configuração do arquivo config.json
config = load_config("config.json")

# Configurações do banco de dados
mongo_client = pymongo.MongoClient(f"mongodb+srv://{config['username']}:{config['password']}@{config['cluster']}/{config['database']}?retryWrites=true&w=majority")
db = mongo_client[config["licensesDatabase"]]
collection = db[config["storeName"]]

def gerar_nova_licenca(dias):
    data_expiracao = datetime.utcnow() + timedelta(days=dias)
    nova_licenca = {
        "key": str(data_expiracao),  # Usamos a data de expiração como chave
        "data_expiracao": data_expiracao
    }
    collection.insert_one(nova_licenca)
    return nova_licenca

def atualizar_licenca(chave, dias):
    filtro = {"key": chave}
    licenca_atual = collection.find_one(filtro)
    if licenca_atual:
        data_expiracao = licenca_atual["data_expiracao"] + timedelta(days=dias)
        collection.update_one(filtro, {"$set": {"data_expiracao": data_expiracao}})
        licenca_atual["data_expiracao"] = data_expiracao
        return licenca_atual
    else:
        return None

if __name__ == "__main__":
    print("1 - Gerar nova licença")
    print("2 - Atualizar licença existente")
    opcao = input("Escolha uma opção (1 ou 2): ")

    if opcao == "1":
        dias = int(input("Digite o número de dias da nova licença: "))
        nova_licenca = gerar_nova_licenca(dias)
        print(f"Licença gerada com sucesso: {nova_licenca}")
    elif opcao == "2":
        id_licenca = input("Digite o ID da licença que deseja atualizar: ")
        dias = int(input("Digite o número de dias a serem adicionados: "))
        licenca_atualizada = atualizar_licenca(id_licenca, dias)
        if licenca_atualizada:
            print(f"Licença atualizada com sucesso: {licenca_atualizada}")
        else:
            print("Licença não encontrada.")
    else:
        print("Opção inválida.")
