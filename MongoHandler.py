from tkinter import messagebox
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid, OperationFailure
from datetime import datetime, date
import logging
from GmailHandler import deleteEmail
import json
logging.basicConfig(filename='pixlogs.log', encoding='utf-8', level=logging.WARNING)
file_path = 'config.json'


def read_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

config = read_config('config.json')

def connect(user, passw, db):
    try:
        username = str(user)
        password = str(passw)
        database = str(db)
        cluster = config['cluster']
        client = MongoClient(f'mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority')
        return client[database]
    except:
            logging.error("Authentication failed. Please check your credentials.")


def create_collection(db: Database, collection_name:str) -> Collection:
    try: 
        return db.create_collection(collection_name)
    except CollectionInvalid:
        logging.error(f"A coleção {collection_name} já existe, portanto não foi criada.")

def drop_collection(db: Database, collection_name:str) -> dict:
    try: 
        db = connect(config['username'], config['password'], 'licenses')
        return db.drop_collection(collection_name)
    except CollectionInvalid:
        logging.error(f"A coleção {collection_name} não existe, portanto não foi excluída.")
        
def check_license(db: Database, collection_name:str, value:str):
    try:
        db = connect(config['username'], config['password'], 'pixchecker')
        result = list(db[collection_name].find({"key": value}))
        if len(result) > 0:
            return True
        else:
            return False
    except:
        logging.error("Erro ao verificar licença")

def return_pix(db: Database, collection_name:str):
    try:
        db = connect(config['username'], config['password'], 'pixchecker')
        result = db[collection_name].find()
        return result
    except:
        logging.error("Erro ao tentar retornar todos os PIX")
        
def return_pix_daily(db: Database, collection_name:str, dia:int, mes:str, ano:int):
    try:
        db = connect(config['username'], config['password'], 'pixchecker')
        filter={
            "dia": dia,
            "mes": mes,
            "ano": ano
        }
        result = db[collection_name].find(filter=filter)
        return result
    except:
        messagebox.showerror("Erro na atualização", "Erro ao tentar retornar os PIXs do dia.")
        logging.error("Erro ao tentar retornar os PIXs do dia - " + str(datetime.now()))
        exit()

def return_pix_month(db: Database, collection_name:str, mes:str):
    try:
        db = connect(config['username'], config['password'], 'pixchecker')
        filter={
            "mes": mes
        }
        result = db[collection_name].find(filter=filter)
        return result
    except:
        logging.error(f"Erro ao tentar retornar os PIXs do mes {mes}")

def return_pix_day_month(db: Database, collection_name:str, dia:int, mes:str):
    try:
        db = connect(config['username'], config['password'], 'pixchecker')
        filter={
            "dia": dia,
            "mes": mes
        }
        result = db[collection_name].find(filter=filter)
        return result
    except:
        logging.error(f"Erro ao tentar retornar os PIXs do dia {dia} e mes {mes} - " + str(datetime.now()))
        

def return_qtd_docs(db: Database, collection_name:str):
    try:
        db = connect(config['username'], config['password'], 'pixchecker')
        result = list(db[collection_name].find())
        qtd = len(result)
    except:
        logging.error("Erro em recuperar quantidade de documentos")
    return qtd

def add_pix(db: Database, collection_name: str, allPix: list):
    db = connect(config['username'], config['password'], 'pixchecker')
    coll = db[collection_name]
    now = datetime.now()
    todays_date = date.today()
    current_year = int(todays_date.year)
    try:
        nome = allPix[0]
        valor = allPix[1]
        existing_pix = coll.find_one({"nome": nome, "valor": valor})
        
        if existing_pix:
            existing_horario = existing_pix.get("horario")
            # Comparar o horário existente com o horário atual com uma margem de 1 minuto
            if (now - existing_horario).total_seconds() > 60:
                mydict = {"nome": nome, "valor": valor, "dia": todays_date.day, "mes": todays_date.month, "ano": current_year, "horario": now}
                try:
                    coll.insert_one(mydict)
                except:
                    logging.error(f"Erro ao inserir no banco.")
            else:
                messagebox.WARNING (("Aviso",f"O PIX com nome '{nome}' e valor '{valor}' já existe no banco de dados com horário próximo."))
                logging.warning(f"O PIX com nome '{nome}' e valor '{valor}' já existe no banco de dados com horário próximo.")
        else:
            mydict = {"nome": nome, "valor": valor, "dia": todays_date.day, "mes": todays_date.month, "ano": current_year, "horario": now}
            try:
                coll.insert_one(mydict)
            except:
                messagebox.showerror("Erro ao inserir no banco", "Erro ao tentar adicionar novo pix no banco.")
                logging.error(f"Erro ao inserir no banco.")
    
        deleteEmail()
    
    except:
        messagebox.showerror("Erro add_pix", "Erro ao tentar adicionar novo pix no banco.")
        return
