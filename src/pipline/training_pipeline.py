import sys
import os
from src.components.data_ingestion import dataIngestion
from src.logger import logging
from src.exception import myexception
from src.entity.artifact_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig,DataValidationConfig
from src.components.data_validation import DataValidation

class TrainingPipeline :
    def __init__(self)->None:
        self.data_validation_config = DataValidationConfig()
        self.data_ingestion_config = DataIngestionConfig()
        logging.info("training pipeline started")
    
    def start_ingestion (self) -> DataIngestionArtifact:
        try:
            logging.info("entered ingestion module")
            data_ingestion = dataIngestion()
            data_artifact = data_ingestion.data_ingestion_start()
            logging.info("data ingestion done sucessfully")
        except Exception as e:
            raise myexception(e,sys)

        return data_artifact
    

    def start_validation (self,injection_artifact : DataIngestionArtifact , validation_config : DataValidationConfig) -> DataIngestionArtifact :
        try:
            logging.info("entered validation module")
            data_val = DataValidation(injection_artifact=injection_artifact, validation_config=validation_config)
            data_artifact = data_val.initiate_validation()
            logging.info("data validation done sucessfully")
            return data_artifact
        except Exception as e:
            raise myexception(e,sys)
    def run_pipeline (self) ->None:
        try:   
            data_artifact = self.start_ingestion()
            data_val_artifact = self.start_validation(injection_artifact=data_artifact , validation_config=self.data_validation_config)
        except Exception as e:
            raise myexception(e,sys)