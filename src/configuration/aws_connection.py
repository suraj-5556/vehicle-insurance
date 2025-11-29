import boto3
import os
from src.constants import AWS_SECRET_ACCESS_KEY_ENV_KEY, AWS_ACCESS_KEY_ID_ENV_KEY, REGION_NAME

class s3client :
    s3_client = None
    s3_resource = None

    def __init__ (self):
        if s3client.s3_client == None or s3client.s3_resource == None :
            access_id = os.getenv(AWS_ACCESS_KEY_ID_ENV_KEY)
            access_key = os.getenv(AWS_SECRET_ACCESS_KEY_ENV_KEY)
            region_name = REGION_NAME

            if access_id == None:
                raise Exception("plz set access_id")
            if access_key == None:
                raise Exception("plz set access_key")
            if region_name == None:
                raise Exception("plz set region_name")
            
            s3client.s3_resource = boto3.resource('s3',
                                            aws_access_key_id=access_id,
                                            aws_secret_access_key=access_key,
                                            region_name=region_name
                                            )
            s3client.s3_client = boto3.client('s3',
                                        aws_access_key_id=access_id,
                                        aws_secret_access_key=access_key,
                                        region_name=region_name
                                        )
        self.s3_resource = s3client.s3_resource
        self.s3_client = s3client.s3_client