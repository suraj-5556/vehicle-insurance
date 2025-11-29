import sys
import os
from src.components.data_ingestion import dataIngestion
from src.logger import logging
from src.exception import myexception
from src.entity.artifact_entity import (DataIngestionArtifact ,
                                        DataTransformationArtifact,
                                        ModelTrainerArtifact,
                                        ModelEvaluationArtifact,
                                        ModelPusherArtifact)
from src.entity.config_entity import (DataIngestionConfig,
                                      DataValidationConfig,
                                      DataTransformationConfig,
                                      ModelTrainerConfig,
                                      ModelEvaluationConfig,
                                      ModelPusherConfig)
from src.components.data_validation import DataValidation
from src.components.data_transformation import DataTransformation
from src.components.model_trainer import ModelTraining
from src.components.model_evaluation import ModelEvaluation
from src.components.model_pusher import ModelPusher

class TrainingPipeline :
    def __init__(self)->None:
        self.data_validation_config = DataValidationConfig()
        self.data_ingestion_config = DataIngestionConfig()
        self.data_transform_config = DataTransformationConfig()
        self.model_training_config = ModelTrainerConfig()
        self.model_eval_config = ModelEvaluationConfig()
        self.model_pusher_config = ModelPusherConfig()
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
        
    def start_training (self , Data_transform_artifact :DataTransformationArtifact,
                        model_training_config : ModelTrainerConfig) -> ModelTrainerArtifact:
        try:
            trainer = ModelTraining(Data_tranform_artifact=Data_transform_artifact , 
                                    model_training_config=model_training_config)
            artifact = trainer.start_training()

            return artifact
        except Exception as e:
            raise myexception(e,sys)
    def start_model_evaluation(self, data_transform_artifact: DataTransformationArtifact,
                               model_trainer_artifact: ModelTrainerArtifact) -> ModelEvaluationArtifact:

        try:
            logging.info("entered model eval stage")
            model_evaluation = ModelEvaluation(model_eval_config=self.model_eval_config,
                                               data_transform_artifact=data_transform_artifact,
                                               model_train_artifact=model_trainer_artifact)
            model_evaluation_artifact = model_evaluation.start_eval()
            logging.info("completed model evaluation")
            return model_evaluation_artifact
        except Exception as e:
            raise myexception(e, sys)

    def start_model_pusher(self, model_evaluation_artifact: ModelEvaluationArtifact) -> ModelPusherArtifact:

        try:
            logging.info("entered model pushing stage")
            model_pusher = ModelPusher(model_eval_artifact=model_evaluation_artifact,
                                       model_pusher_config=self.model_pusher_config
                                       )
            model_pusher_artifact = model_pusher.start_pusher()
            logging.info("model push to aws successfully")
            return model_pusher_artifact
        except Exception as e:
            raise myexception(e, sys)

    def run_pipeline (self) ->None:
        try:   
            data_artifact = self.start_ingestion()
            data_val_artifact = self.start_validation(injection_artifact=data_artifact , 
                                                      validation_config=self.data_validation_config)
            data_transform_artifact = self.start_transformation(data_artifact,
                                                                data_val_artifact,
                                                                self.data_transform_config)
            model_training_artifact = self.start_training(Data_transform_artifact=data_transform_artifact,
                                                          model_training_config= self.model_training_config)
            
            model_evaluation_artifact = self.start_model_evaluation(data_transform_artifact=data_transform_artifact,
                                                                    model_trainer_artifact=model_training_artifact)
            if not model_evaluation_artifact.is_model_accepted:
                logging.info(f"Model not accepted.")
                return None
            model_pusher_artifact = self.start_model_pusher(model_evaluation_artifact=model_evaluation_artifact)
        except Exception as e:
            raise myexception(e,sys)