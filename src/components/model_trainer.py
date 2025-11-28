import sys
from typing import Tuple

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

from src.exception import myexception
from src.logger import logging
from src.utils.main_utils import load_numpy_array_data, load_object, save_object
from src.entity.config_entity import ModelTrainerConfig
from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact, ClassificationMetricArtifact
from src.entity.estimator import MyModel

class ModelTraining:
    def __init__ (self,Data_tranform_artifact : DataTransformationArtifact,
                  model_training_config : ModelTrainerConfig):
        try :
            logging.info("entered training stage")
            self.data_transform_artifact = Data_tranform_artifact
            self.model_training_config = model_training_config
        except Exception as e:
            raise myexception(e,sys)
        
    def get_model_object_and_report (self ,train : np.array , test : np.array) -> Tuple[object,object] :
        try:
            logging.info("getting ready with data")
            x_train, y_train, x_test, y_test = train[:, :-1], train[:, -1], test[:, :-1], test[:, -1]

            logging.info("model training stared")
            model = RandomForestClassifier(
                n_estimators = self.model_training_config._n_estimators,
                min_samples_split = self.model_training_config._min_samples_split,
                min_samples_leaf = self.model_training_config._min_samples_leaf,
                max_depth = self.model_training_config._max_depth,
                criterion = self.model_training_config._criterion,
                random_state = self.model_training_config._random_state
            )

            model.fit(x_train,y_train)

            logging.info("model trained successfully")

            y_pred = model.predict(x_test)

            logging.info("building matrix")

            accuracy = accuracy_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            logging.info("completed matrix building")

            metric_artifact = ClassificationMetricArtifact(accuracy=accuracy,f1_score=f1, precision_score=precision, recall_score=recall)
            return model, metric_artifact

        except Exception as e:
            raise myexception(e,sys)
        
    def start_training (self) -> ModelTrainerArtifact :
        try:
            logging.info("extracting array")
            train = load_numpy_array_data(self.data_transform_artifact.transformed_train_file_path)
            test = load_numpy_array_data(self.data_transform_artifact.transformed_test_file_path)

            logging.info("extracting pipeline")

            pipeline = load_object(self.data_transform_artifact.transformed_object_file_path)

            my_model , artifact = self.get_model_object_and_report(train,test)

            logging.info("checcking mocdel accuracy with base line accuracy")


            if accuracy_score(train[:, -1], my_model.predict(train[:, :-1])) < self.model_training_config.expected_accuracy:
                logging.info("No model found with score above the base score")
                raise Exception("No model found with score above the base score")
            

            my_model = MyModel(preprocessing_obj = pipeline ,
                               model_obj = my_model)
            save_object(self.model_training_config.trained_model_file_path , my_model)
            
            model_trainer_artifact = ModelTrainerArtifact(
                trained_model_file_path=self.model_training_config.trained_model_file_path,
                metric_artifact=artifact,
            )
            logging.info(f"Model trainer artifact: {model_trainer_artifact}")
            logging.info("exiting model training stage")
            return model_trainer_artifact

        except Exception as e:
            raise myexception(e,sys)