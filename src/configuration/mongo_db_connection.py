import sys
import certifi
import pymongo
import os

from src.constants import DB_NAME,CONNECTION_URL
from src.logger import logging
from src.exception import myexception

ca = certifi.where()

class mongoDB_connection:
    """
    this class helps to build connection with mongo db server using database url
    """
    clint = None
    def __init__(self, database :str = DB_NAME):
        """
        function try to build connection with ca verification
        """
        try:
            if mongoDB_connection.clint == None :
                connection_url = os.getenv(CONNECTION_URL)
                if connection_url == None :
                    raise Exception("mongodb url is empty")
                mongoDB_connection.clint = pymongo.MongoClient(connection_url,tlsCAFile=ca)

            self.client = mongoDB_connection.clint
            self.database = self.client[database]
            self.database_name = database
            logging.info("build connection with mongoDB")

        except Exception as e:
            raise myexception(e,sys)