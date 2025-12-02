import sys
import pandas as pd
import numpy as np
from typing import Optional

from src.configuration.mongo_db_connection import mongoDB_connection
from src.logger import logging
from src.exception import myexception
from src.constants import DB_NAME

class proj1:
    """
    this class imports mongoDB_connection and gets data inside the mongoDB server
    """
    def __init__(self):
        """
        this function calls mongo_connection 
        """
        try:
            self.client = mongoDB_connection(DB_NAME)
            logging.info("build sucess ful connection with mongoDB")
        except Exception as e:
            raise myexception(e,sys)
    
    def collect_in_df (self,collection_name : str,database_name : Optional[str] = None) -> pd.DataFrame:
        """
        this function collects data from mongodb and returns dataframe
        """
        try:
            if database_name == None:
                collection = self.client.database[collection_name]
            else:
                collection = self.client[database_name][collection_name]
            
            data = collection.find()
            df = pd.DataFrame(list(data))

            logging.info("extracted data and converted to df")

            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"], axis=1)
            df.replace({"na":np.nan},inplace=True)
            return df
        except Exception as e:
            raise myexception(e,sys)
        
    def close_connection (self) -> None:
        try:
            if self.client and self.client.client:
                #self.client.client.close()
                logging.info("mongo connection closed")
        except Exception as e:
            raise myexception(e,sys)
