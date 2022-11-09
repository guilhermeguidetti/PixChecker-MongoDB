from cgitb import reset
from operator import eq
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid
from datetime import datetime, date
from bson.timestamp import Timestamp
import logging
from GmailHandler import deleteEmail
logging.basicConfig(filename='pixlogs.log', encoding='utf-8', level=logging.DEBUG)

class AlreadyInDB(Exception):
    """Raised when pix is already stored in DB"""
    pass

def connect(
    username: str,
    password: str,
    database: str,
    cluster='cluster0.zovzbqi.mongodb.net') -> Database:
    client = MongoClient(f'mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority')
    return client[database]

def create_collection(db: Database, collection_name:str) -> Collection:
    try: 
        return db.create_collection(collection_name)
    except CollectionInvalid:
        logging.error(f"A coleção {collection_name} já existe, portanto não foi criada.")

def drop_collection(db: Database, collection_name:str) -> dict:
    try: 
        return db.drop_collection(collection_name)
    except CollectionInvalid:
        logging.error(f"A coleção {collection_name} não existe, portanto não foi excluída.")
        
def check_license(db: Database, collection_name:str, value:str):
    try:
        db = connect('guidetti', '13579', 'licenses')
        filter={
                "key": value
        }
        result = list(db[collection_name].find(
            filter=filter
        ))
        if (len(result) > 0):
            return True
        else:
            return False

    except:
        logging.error("Erro ao verificar licença")

def return_pix(db: Database, collection_name:str, fieldName:str, value:int):
    try:
        db = connect('guidetti', '13579', 'pixchecker')
        filter={
                fieldName: value
        }
        result = db[collection_name].find(
            filter=filter
        )
        return result
    except:
        logging.error("Erro ao tentar retornar todos os PIX")
        
def return_pix_daily(db: Database, collection_name:str, dia:int, mes:int, ano:int):
    try:
        db = connect('guidetti', '13579', 'pixchecker')
        filter={
                "dia": dia,
                "mes": mes,
                "ano": ano
        }
        result = db[collection_name].find(
            filter=filter
        )
        return result
    except:
        logging.error("Erro ao tentar retornar os PIXs do dia")
        

def return_qtd_docs(db: Database, collection_name:str):
    try:
        db = connect('guidetti', '13579', 'pixchecker')
        result = list(db[collection_name].find())
        qtd = len(result)
    except:
        logging.error("Erro em recuperar quantidade de documentos")
    return qtd

def add_pix(db: Database, collection_name:str, allPix: list):
    db = connect('guidetti', '13579', 'pixchecker')
    coll = db[collection_name]
    now = datetime.now()
    todays_date = date.today()
    current_year = int(todays_date.year)
    i = 0
    try:
        for pix in allPix:
            mydict = { "nome": allPix[i][0], "valor": allPix[i][1], "dia": allPix[i][2],  "mes": allPix[i][3], "ano": current_year, "horario": now}
            filter={
                'nome': allPix[i][0],
                'valor':allPix[i][1],
                'dia': allPix[i][2],
                'mes':  allPix[i][3],
                'ano': current_year
            }

            result = list(db[collection_name].find(
            filter=filter
            ))
            if result:
                raise AlreadyInDB
            try:
                pix = coll.insert_one(mydict)
            except:
                logging.error(f"Erro ao inserir no banco.")
            i += 1
        deleteEmail()
    except AlreadyInDB:
        deleteEmail()
        return
