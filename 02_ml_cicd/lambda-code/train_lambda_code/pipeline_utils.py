import boto3
import os
import json
import datetime
from time import gmtime, strftime
from boto3.session import Session

code_pipeline = boto3.client('codepipeline')

def put_job_success(job_id):
    print("[INFO] Job submitted.")
    code_pipeline.put_job_success_result(jobId=job_id)


def put_job_failure(job_id, message):
    print('[FAILURE]Putting job failure')
    print(message)
    code_pipeline.put_job_failure_result(jobId=job_id, failureDetails={'message': message, 'type': 'JobFailed'})


def write_job_info_s3(event):
    objectKey = event['CodePipeline.job']['data']['outputArtifacts'][0]['location']['s3Location']['objectKey']
    bucketname = event['CodePipeline.job']['data']['outputArtifacts'][0]['location']['s3Location']['bucketName']
    artifactCredentials = event['CodePipeline.job']['data']['artifactCredentials']
    artifactName = event['CodePipeline.job']['data']['outputArtifacts'][0]['name']
    S3SSEKey = os.environ['KMSKey']
    
    json_data = json.dumps(event)
    print(json_data)

    session = Session(aws_access_key_id=artifactCredentials['accessKeyId'],
                  aws_secret_access_key=artifactCredentials['secretAccessKey'],
                  aws_session_token=artifactCredentials['sessionToken'])
    s3 = session.resource("s3")
    object = s3.Object(bucketname, objectKey)
    object.put(Body=json_data, ServerSideEncryption='aws:kms', SSEKMSKeyId=S3SSEKey)    
    print('[SUCCESS]Job Information Written to S3')


def get_job_id(event):
    return event['CodePipeline.job']['id']

def get_user_params(event):
    userParamText = event['CodePipeline.job']['data']['actionConfiguration']['configuration']['UserParameters']
    return json.loads(userParamText)

def get_job_name(event):
    job_name = 'mlops-train-' + strftime("%Y-%m-%d-%H-%M-%S", gmtime())
    return job_name
