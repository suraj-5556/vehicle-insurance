import sys
import numpy as np
import pandas as pd
from imblearn.combine import SMOTEENN
from imblearn.pipeline import Pipeline

# from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.compose import ColumnTransformer

from src.constants import TARGET_COLUMN, SCHEMA_FILE_PATH
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataTransformationArtifact, DataIngestionArtifact, DataValidationArtifact
from src.exception import myexception
from src.logger import logging
from src.utils.main_utils import save_object, save_numpy_array_data, read_yaml_file

class DataTransformation :
    def __init__(self,data_integration_artifact : DataIngestionArtifact,
                 data_validation_artifact : DataValidationArtifact,
                 data_tranform_config : DataTransformationConfig):
        
        try:
            self.data_integration_artifact = data_integration_artifact
            self.data_validation_artifact = data_validation_artifact
            self.data_transform_config = data_tranform_config

            self.schema = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise myexception(e,sys)
        
    def read_csv (self , path : str) -> pd.DataFrame : 
        try:
            return pd.read_csv(path)
        except Exception as e:
            raise myexception(e,sys)
    
    def data_transform_object (self) -> Pipeline:

        try:
            mm_scaler = MinMaxScaler()
            nm_scaler = StandardScaler()

            mm_features = self.schema["mm_columns"]
            nm_features = self.schema["num_features"]

            preprocessing = ColumnTransformer(
                transformers=[
                    ("standrad",nm_scaler,nm_features),
                    ("min_max",mm_scaler,mm_features)
                ],
                remainder="passthrough"
            )

            final_pipeline = Pipeline(steps=[("final",preprocessing)])

            return final_pipeline
        except Exception as e:
            raise myexception(e,sys)
        
    def drop_cols (self,df) :
        try:
            df = df.drop(self.schema["drop_columns"],axis=1)
            return df
        except Exception as e:
            raise myexception(e,sys)
        
    def _map_gender_column(self, df):
        logging.info("Mapping 'Gender' column to binary values")
        df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1}).astype(int)
        return df

    def _create_dummy_columns(self, df):
        logging.info("Creating dummy variables for categorical features")
        df = pd.get_dummies(df, drop_first=True)
        return df

    def _rename_columns(self, df):
        logging.info("Renaming specific columns and casting to int")
        df = df.rename(columns={
            "Vehicle_Age_< 1 Year": "Vehicle_Age_lt_1_Year",
            "Vehicle_Age_> 2 Years": "Vehicle_Age_gt_2_Years"
        })
        for col in ["Vehicle_Age_lt_1_Year", "Vehicle_Age_gt_2_Years", "Vehicle_Damage_Yes"]:
            if col in df.columns:
                df[col] = df[col].astype('int')
        return df
    def start_transform (self) -> DataTransformationArtifact :
        try:
            if not self.data_validation_artifact.validation_status:
                logging.error("validation not done")
                raise Exception("validation not done")
            df_train = self.read_csv(self.data_integration_artifact.trained_file_path)
            df_test = self.read_csv(self.data_integration_artifact.test_file_path)

            input_train_col = df_train.drop(TARGET_COLUMN,axis=1)
            target_train_col = df_train[TARGET_COLUMN].values

            input_test_col = df_test.drop(TARGET_COLUMN,axis=1)
            target_test_col = df_test[TARGET_COLUMN].values

            input_train_col = self.drop_cols(input_train_col)
            input_train_col = self._map_gender_column(input_train_col)
            input_train_col = self._create_dummy_columns(input_train_col)
            input_train_col = self._rename_columns(input_train_col)

            input_test_col = self.drop_cols(input_test_col)
            input_test_col = self._map_gender_column(input_test_col)
            input_test_col = self._create_dummy_columns(input_test_col)
            input_test_col = self._rename_columns(input_test_col)

            preprocessor = self.data_transform_object()
            input_train_col = preprocessor.fit_transform(input_train_col)
            input_test_col = preprocessor.transform(input_test_col)

            logging.info("Applying SMOTEENN for handling imbalanced dataset.")
            smt = SMOTEENN(sampling_strategy="minority")

            input_train_features,target_train_features = smt.fit_resample(input_train_col,
                                                                          target_train_col)
            train_arr = np.hstack((input_train_features,np.array(target_train_features).reshape(-1, 1)))
            test_arr = np.hstack((input_test_col,np.array(target_test_col).reshape(-1, 1)))

            save_object(self.data_transform_config.transformed_object_file_path, preprocessor)
            save_numpy_array_data(self.data_transform_config.transformed_train_file_path, array=train_arr)
            save_numpy_array_data(self.data_transform_config.transformed_test_file_path, array=test_arr)
            logging.info("Saving transformation object and transformed files.")

            logging.info("Data transformation completed successfully")
            return DataTransformationArtifact(
                transformed_object_file_path=self.data_transform_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transform_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transform_config.transformed_test_file_path
            )

        except Exception as e:
            raise myexception(e,sys)