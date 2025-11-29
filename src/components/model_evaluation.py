import os
import sys
import pandas as pd
from imblearn import pipeline

from src.entity.config_entity import ModelEvaluationConfig,DataTransformationConfig
from src.entity.artifact_entity import (ModelPusherArtifact,ModelEvaluationArtifact,ModelTrainerArtifact,
                                        EvaluateModelResponse,DataTransformationArtifact)
from src.logger import logging
from src.exception import myexception
from sklearn.metrics import f1_score
from src.utils.main_utils import load_object,load_numpy_array_data
from src.entity.s3_estimator import Proj1Estimator

class ModelEvaluation :
    def __init__(self,model_eval_config : ModelEvaluationConfig ,
                 data_transform_artifact :DataTransformationArtifact ,
                 model_train_artifact : ModelTrainerArtifact) :
        self.model_eval_config = model_eval_config
        self.model_train_atifact = model_train_artifact
        self.data_transform_artifact = data_transform_artifact

    def get_aws_model (self) :
        try:
            logging.info("trying to get model from aws")
            bucket_name = self.model_eval_config.bucket_name
            model_path = self.model_eval_config.s3_model_key_path

            proj1_obj = Proj1Estimator(bucket_name=bucket_name,model_path=model_path)

            if proj1_obj.is_model_present(model_path=model_path):
                logging.info("previous model found")
                return proj1_obj
            logging.info("no previous model found")
            return None

        except Exception as e:
            raise myexception(e,sys)
        
    def model_eval (self) -> EvaluateModelResponse:
        try:
            logging.info("loding testing data")
            test = load_numpy_array_data(self.data_transform_artifact.transformed_test_file_path)

            x = test[:,:-1]
            y = test[:,-1]

            proj1_obj = self.get_aws_model()

            if proj1_obj != None:
                y_pred = proj1_obj.predict(array=x)
                obj_score = f1_score(y_true=y,y_pred=y_pred)
            else:
                obj_score = 0

            trained_model_score = self.model_train_atifact.metric_artifact.f1_score

            best_model_f1_score = obj_score if obj_score > (trained_model_score - self.model_eval_config.changed_threshold_score) else trained_model_score
            artifact = EvaluateModelResponse(trained_model_f1_score = trained_model_score,
                                             best_model_f1_score = best_model_f1_score,
                                             is_model_accepted = trained_model_score > (obj_score + self.model_eval_config.changed_threshold_score),
                                             difference = trained_model_score - obj_score 
                                             )
            return artifact
        except Exception as e:
            raise myexception(e,sys)
        
    def start_eval (self) :
        try:
            model_eval = self.model_eval()
            s3_model_path = self.model_eval_config.s3_model_key_path

            artifact = ModelEvaluationArtifact(is_model_accepted=model_eval.is_model_accepted,
                                               changed_accuracy=model_eval.best_model_f1_score,
                                               s3_model_path=s3_model_path,
                                               trained_model_path=self.model_train_atifact.trained_model_file_path)
            return artifact
        except Exception as e:
            raise myexception(e,sys)