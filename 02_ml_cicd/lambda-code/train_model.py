import boto3
import os
import json
import datetime
import pipeline_utils
import traceback
from time import gmtime, strftime
from boto3.session import Session

sagemaker = boto3.client('sagemaker')
code_pipeline = boto3.client('codepipeline')

def lambda_handler(event, context):

    job_id = pipeline_utils.get_job_id(event)
    job_name = pipeline_utils.get_job_name(event)
    event['job_name'] = job_name
    event['stage'] = 'Training'
    event['status'] = 'InProgress'
    event['message'] = 'training job "{} started."'.format(job_name)

    # Environment variable containing S3 bucket for storing the model artifact
    model_artifact_bucket = os.environ['ModelArtifactBucket']
    print("[INFO]MODEL_ARTIFACT_BUCKET:", model_artifact_bucket)

    # Environment variable containing S3 bucket containing training data
    data_bucket = os.environ['S3DataBucket']
    print("[INFO]TRAINING_DATA_BUCKET:", data_bucket)

    container_path = os.environ['ModelImage']
    print('[INFO]CONTAINER_PATH:', container_path)

    # Role to pass to SageMaker training job that has access to training data in S3, etc
    SageMakerRole = os.environ['SageMakerExecutionRole']
    
    # Configure training job
    create_training_params = \
    {
        "RoleArn": SageMakerRole,
        "TrainingJobName": job_name,
        "AlgorithmSpecification": {
            "TrainingImage": container_path,
            "TrainingInputMode": "File"
        },
        "ResourceConfig": {
            "InstanceCount": 1,
            "InstanceType": 'ml.c4.2xlarge',
            "VolumeSizeInGB": 10
        },
        "InputDataConfig": [
            {
                "ChannelName": "training",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": "s3://{}/train".format(data_bucket),
                        "S3DataDistributionType": "FullyReplicated"
                    }
                },
                "ContentType": "csv",
                "CompressionType": "None"
            }
        ],
        "OutputDataConfig": {
            "S3OutputPath": "s3://{}/{}/output".format(model_artifact_bucket, job_name)
        },
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 60 * 60
        }
    }    

    try:

        # Starts training job        
        response = sagemaker.create_training_job(**create_training_params)

        # Writes down job info to S3
        pipeline_utils.write_job_info_s3(event, { "job_name": job_name })

        # Set CodePipeline task completed
        pipeline_utils.put_job_success(job_id)


    except Exception as e:
        print('[ERROR] Unable to create training job. Exception: ' + str(e))
        event['message'] = str(e)
        print(traceback.format_exc())
        pipeline_utils.put_job_failure(job_id, str(e))

    return event
