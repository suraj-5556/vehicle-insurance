import sys
import os
from src.components.data_ingestion import dataIngestion
from src.logger import logging
from src.exception import myexception
from src.entity.artifact_entity import DataIngestionArtifact , DataTransformationArtifact
from src.entity.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig
from src.components.data_validation import DataValidation
from src.components.data_transformation import DataTransformation

class TrainingPipeline :
    def __init__(self)->None:
        self.data_validation_config = DataValidationConfig()
        self.data_ingestion_config = DataIngestionConfig()
        self.data_transform_config = DataTransformationConfig()
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
        
    def start_transformation (self,ingection_artifact : DataIngestionArtifact ,
                              validation_articat : DataValidationConfig ,
                              transformation_config : DataTransformationConfig) -> DataTransformationArtifact:
        try:
            transform = DataTransformation(ingection_artifact,
                                           validation_articat,
                                           transformation_config)
            transform_artifact = transform.start_transform()

            return transform_artifact
        except Exception as e:
            raise myexception(e,sys)
    def run_pipeline (self) ->None:
        try:   
            data_artifact = self.start_ingestion()
            data_val_artifact = self.start_validation(injection_artifact=data_artifact , 
                                                      validation_config=self.data_validation_config)
            data_transform_artifact = self.start_transformation(data_artifact,
                                                                data_val_artifact,
                                                                self.data_transform_config)
        except Exception as e:
            raise myexception(e,sys)