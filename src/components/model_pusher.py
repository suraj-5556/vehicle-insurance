import sys

from src.cloud_storage.aws_storage import SimpleStorageService
from src.exception import myexception
from src.logger import logging
from src.entity.s3_estimator import Proj1Estimator
from src.entity.artifact_entity import ModelPusherArtifact,ModelEvaluationArtifact
from src.entity.config_entity import ModelPusherConfig
                                        
class ModelPusher:
    def __init__ (self , model_eval_artifact = ModelEvaluationArtifact ,
                  model_pusher_config = ModelPusherConfig):
        
        logging.info("model pusher sharted")
        self.s3 = SimpleStorageService()
        self.model_eval_artifact = model_eval_artifact
        self.model_pusher_config = model_pusher_config
        self.proj1_estimator = Proj1Estimator(bucket_name=self.model_pusher_config.bucket_name ,
                                              model_path=self.model_eval_artifact.s3_model_path)
        
    def start_pusher (self) -> ModelPusherArtifact:
        try:
            logging.info("model saving")
            self.proj1_estimator.save_model(from_file=self.model_eval_artifact.trained_model_path)
            logging.info("saved model")
            model_pusher_artifact = ModelPusherArtifact(bucket_name=self.model_pusher_config.bucket_name,
                                                        s3_model_path=self.model_pusher_config.s3_model_key_path)
            logging.info("model pushed to aws")
            return model_pusher_artifact
        except Exception as e:
            raise myexception(e,sys)