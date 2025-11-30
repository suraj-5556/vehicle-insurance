import os
import sys
import pandas as pd
import numpy as np
from src.logger import logging
from src.exception import myexception
from imblearn.pipeline import pipeline

class MyModel :
    def __init__ (self,preprocessing_obj : pipeline , model_obj : object) :
        try:
            self.preprocessing_obj = preprocessing_obj
            self.model_obj = model_obj
        except Exception as e:
            raise myexception(e,sys) 
        
    def prediction (self , dataframe : pd.DataFrame) :
        try:
            logging.info("started prediction")
            features = self.preprocessing_obj.transform(dataframe)
            features = self.model_obj.predict(features)
            logging.info("prediction done sucessfully")
            return features
        except Exception as e:
            raise myexception(e,sys)
        
    def prediction_with_array (self , array : np.array) :
        try:
            logging.info("started prediction")
            features = self.model_obj.predict(array)
            logging.info("prediction done sucessfully")
            return features
        except Exception as e:
            raise myexception(e,sys)

    def __repr__(self):
        return f"{type(self.model_obj).__name__}()"

    def __str__(self):
        return f"{type(self.model_obj).__name__}()"