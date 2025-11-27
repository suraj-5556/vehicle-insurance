import os
import sys
import pandas as pd
import json
from src.logger import logging
from src.exception import myexception
from src.utils.main_utils import read_yaml_file
from src.constants import SCHEMA_FILE_PATH
from src.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact
from src.entity.config_entity import DataValidationConfig

class DataValidation :
    def __init__ (self , injection_artifact : DataIngestionArtifact , validation_config : DataValidationConfig) -> None :
        try:
            self.ingestion_artifact = injection_artifact
            self.validation_config = validation_config
            self.schema = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise myexception(e,sys)
    
    def check_no_of_columns (self , dataframe : pd.DataFrame) -> bool :
        try :
            logging.info("started sucessfully")
            status = len(dataframe.columns) == len(self.schema["columns"])
            logging.info("no issue with column numbers")
            return status
        except Exception as e:
            raise myexception(e,sys)
        
    def check_mismatch_columns (self , dataframe : pd.DataFrame) -> str :
        try:
            logging.info("next step type check")
            numeric_missing_col = []
            categorical_missing_col = []
            data_column = dataframe.columns.to_list()

            logging.info("type check started")

            for data in self.schema["categorical_columns"]:
                if data not in data_column:
                    categorical_missing_col.append(data)

            if len(categorical_missing_col) > 0:
                logging.warning(f"categorical columns {categorical_missing_col} are missing")

            for data in self.schema["numerical_columns"]:
                if data not in data_column:
                    numeric_missing_col.append(data)

            if len(numeric_missing_col) > 0:
                logging.warning(f"categorical columns {numeric_missing_col} are missing")

            stat = False if len(categorical_missing_col) > 0 or len(numeric_missing_col) > 0 else True
            logging.info(f"type check done with {stat}")

            return stat
        except Exception as e:
            raise myexception(e,sys)
        
    def read_csv (self , path : str) -> pd.DataFrame : 
        try:
            return pd.read_csv(path)
        except Exception as e:
            raise myexception(e,sys)
        
    def initiate_validation (self) -> DataValidationArtifact :
        try:
            train_df = self.read_csv(self.ingestion_artifact.trained_file_path)
            test_df = self.read_csv(self.ingestion_artifact.test_file_path)

            val_str = ""
            logging.info("running training check")

            status = self.check_no_of_columns(dataframe=train_df)

            if not status:
                val_str += " column no missing in train , "
                logging.error("column no missmatch in train ")

            status = self.check_mismatch_columns(dataframe=train_df)

            if not status:
                val_str += " column type miss match in train , "
                logging.error("column type miss match in train")

            logging.info("running test check")

            status = self.check_no_of_columns(dataframe=test_df)

            if not status:
                val_str += " column no missing in test , "
                logging.error("column no missmatch in test ")

            status = self.check_mismatch_columns(dataframe=test_df)

            if not status:
                val_str += " column type miss match in test , "
                logging.error("column type miss match in test")

            validation_state = len(val_str) == 0

            logging.info("building report")

            data_validation_config = DataValidationArtifact(
                validation_status = validation_state,
                message = val_str,
                validation_report_file_path=self.validation_config.validation_report_file_path
            )

            logging.info("saving report")

            validation_report = {
                "validation_status" : validation_state ,
                "message" : val_str
            }

            report_dir = os.path.dirname(self.validation_config.validation_report_file_path)
            os.makedirs(report_dir,exist_ok=True)

            with open(self.validation_config.validation_report_file_path,"w") as report :
                json.dump(validation_report,report,indent=4)

            return data_validation_config
        except Exception as e:
            raise myexception(e,sys)