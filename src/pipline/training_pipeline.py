import sys
import os
from src.components.data_ingestion import dataIngestion
from src.logger import logging
from src.exception import myexception
from src.entity.artifact_entity import DataIngestionArtifact
from src.entity.config_entity import DataIngestionConfig

class TrainingPipeline :
    def __init__(self)->None:
        # self.data_ingestion_artifact = DataIngestionArtifact()
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
    def run_pipeline (self) ->None:
        try:   
            data_artifact = self.start_ingestion()
        except Exception as e:
            raise myexception(e,sys)