import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from src.logger import logging
from src.exception import myexception
from src.entity.artifact_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig
from src.data_access.proj1_data import proj1

class dataIngestion:
    def __init__ (self,data_config: DataIngestionConfig = DataIngestionConfig())->None:
        """
        this takes DataIngestionConfig module and build local object for it
        """
        try:
            self.data_config = data_config
        except Exception as e:
            raise myexception(e,sys)
        
    def save_dataframe (self) -> pd.DataFrame:
        """
        build connection using proj1_data() and extract data in form of dataframe
        
        :param self: self
        :return: dataframe
        :rtype: DataFrame
        """
        try:
            data = proj1()
            dataframe = data.collect_in_df(self.data_config.collection_name)

            logging.info("collected data in dataframe")

            collection_store_path = self.data_config.feature_store_file_path
            dir_path = os.path.dirname(collection_store_path)
            os.makedirs(dir_path,exist_ok=True)

            dataframe.to_csv(collection_store_path,index=False)

            logging.info("dataframe saved ")

            return dataframe
        except Exception as e:
            raise myexception(e,sys)
    
    def save_train_test (self,dataframe :pd.DataFrame)->None:
        """
        takes dataframe and divedes and save in train,test
        
        :param : takes dataframe as input given by save dataframe module
        """
        try:
            train,test = train_test_split(dataframe,test_size=self.data_config.train_test_split_ratio)

            logging.info("split dataframe in train test split")

            train_store_path = self.data_config.training_file_path
            test_store_path = self.data_config.testing_file_path

            file_path = os.path.dirname(self.data_config.testing_file_path)

            os.makedirs(file_path,exist_ok=True)

            train.to_csv(train_store_path,index=False)
            test.to_csv(test_store_path,index=False)

            logging.info("train test saved")
        except Exception as e:
            raise myexception(e,sys)
    def data_ingestion_start (self) -> DataIngestionArtifact :
        """
        this is function that is intial stage for pipeline and saes path in DataIngestionArtifact
        """
        try:
            df = self.save_dataframe()
            self.save_train_test(df)

            artifact = DataIngestionArtifact(trained_file_path=self.data_config.training_file_path,
                                             test_file_path=self.data_config.testing_file_path)
            
            logging.info(f"Data ingestion artifact: {artifact}")
            
            return artifact
        except Exception as e:
            raise myexception(e,sys)