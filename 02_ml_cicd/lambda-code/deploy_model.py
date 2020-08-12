import boto3
import os
import tempfile
import json
import traceback
import pipeline_utils
from boto3.session import Session

DEFAULT_INSTANCE_TYPE = "ml.t2.medium"
DEFAULT_INSTANCE_COUNT = 1
DEFAULT_WEIGHT = 1

sagemaker = boto3.client('sagemaker')

def lambda_handler(event, context):

    try:

        job_id = pipeline_utils.get_job_id(event)
        prev_step = pipeline_utils.read_job_info(event)        
        model_name = prev_step['ModelName']
        model_image = prev_step['ModelImage']
        model_artifact = prev_step['ModelArtifacts']
        endpoint_name = model_name

        create_model(model_name, model_image, model_artifact)
        create_endpoint_config(model_name, endpoint_name)
        create_endpoint(endpoint_name)
        pipeline_utils.put_job_success(job_id)

    except Exception as e:
        print('[ERROR] Unable to deploy model. Exception: ' + str(e))
        print(traceback.format_exc())
        pipeline_utils.put_job_failure(job_id, str(e))


def create_model(model_name, model_image, model_artifact):
    role = os.environ['SageMakerExecutionRole']    
    response = sagemaker.create_model(
        ModelName=model_name,
        PrimaryContainer={
            'Image': model_image,
            'ModelDataUrl': model_artifact
        },
        ExecutionRoleArn=role
    )
    return response


def create_endpoint_config(model_name, endpoint_config_name):
    response = sagemaker.create_endpoint_config(
    EndpointConfigName=endpoint_config_name,
            ProductionVariants=[
                {
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InitialInstanceCount': DEFAULT_INSTANCE_COUNT,
                    'InitialVariantWeight': DEFAULT_WEIGHT,
                    'InstanceType': DEFAULT_INSTANCE_TYPE,
                }
            ]
        )
    return response 


def create_endpoint(endpoint_config_name):
    response = sagemaker.create_endpoint(
        EndpointName=endpoint_config_name,
        EndpointConfigName=endpoint_config_name
    )
    return response         
