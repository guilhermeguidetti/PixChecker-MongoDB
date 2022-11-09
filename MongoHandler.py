from cgitb import reset
from operator import eq
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid
from datetime import datetime, date

from GmailHandler import deleteEmail


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
        print(f"A coleção {collection_name} já existe, portanto não foi criada.")

def drop_collection(db: Database, collection_name:str) -> dict:
    try: 
        return db.drop_collection(collection_name)
    except CollectionInvalid:
        print(f"A coleção {collection_name} não existe, portanto não foi excluída.")
        
def check_license(db: Database, collection_name:str, value:str):
    try:
        db = connect('guidetti', '13579', 'licenses')
        print(value)
        filter={
                "key": value
        }
        result = list(db[collection_name].find(
            filter=filter
        ))
        print(result)
        if (len(result) > 0):
            return True
        else:
            return False

    except:
        print("Erro")

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
        print("erro def reutrnallpix")

def return_qtd_docs(db: Database, collection_name:str):
    try:
        db = connect('guidetti', '13579', 'pixchecker')
        result = list(db[collection_name].find())
        qtd = len(result)
    except:
        print("Erro em recuperar quantidade de documentos")
    return qtd

def add_pix(db: Database, collection_name:str, allPix: list):
    db = connect('guidetti', '13579', 'pixchecker')
    coll = db[collection_name]
    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")
    todays_date = date.today()
    current_year = int(todays_date.year)
    i = 0
    try:
        for pix in allPix:
            mydict = { "nome": allPix[i][0], "valor": allPix[i][1], "dia": allPix[i][2],  "mes": allPix[i][3], "ano": current_year, "horario": current_time}
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
                print(f"Erro ao inserir no banco.")
            i += 1
        deleteEmail()
    except AlreadyInDB:
        # print("PIX já cadastrado no banco.")
        deleteEmail()
        return
    
'''
percorre o dictionary e ver se a chave error existe,
1- criar uma função que insere um documento em uma collection com o método insert_one
2- criar uma função force_recreate collection (mata toda a collection e cria uma zerada)
'''