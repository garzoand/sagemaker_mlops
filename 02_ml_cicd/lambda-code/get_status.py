import boto3
import os
import json
import tempfile
import botocore
import traceback
import pipeline_utils

sagemaker = boto3.client('sagemaker')

def lambda_handler(event, context):

    job_id = pipeline_utils.get_job_id(event)

    try:

        # reads previous step info from pipeline artifacts stored on S3
        prev_step = pipeline_utils.read_job_info(event)
        sm_job_name = prev_step['job_name']
        print("[INFO]Job to monitor:", sm_job_name)

        # gets user params set for this stage
        stage_name = pipeline_utils.get_user_params(event)
        print("[INFO]Current stage: " + stage_name)

        # Training
        if stage_name == "training":

            # Gets the training job status from Sagemaker
            response = sagemaker.describe_training_job(TrainingJobName=sm_job_name)
            job_status = response['TrainingJobStatus']
            print("[INFO]Training job status: " + job_status)

            if job_status == "Completed":
                s3_output_path = response['OutputDataConfig']['S3OutputPath']
                model_data_url = os.path.join(s3_output_path, sm_job_name, 'output/model.tar.gz')
                print("[INFO]Training is completed. Model url: " + model_data_url)
                pipeline_utils.write_job_info_s3(event, { 'model_data_url': model_data_url})
                pipeline_utils.put_job_success(job_id)
            
            elif job_status == "InProgress":
                pipeline_utils.continue_job_later(job_id)

            elif job_status == "Failed":
                failure_reason = training_details['FailureReason']
                pipeline_utils.put_job_failure(event, 'Training job failed. {}'.format(failure_reason))

            # invalid state
            else:
                pipeline_utils.put_job_failure(job_id, "Invalid training job status")
                

        # invalid stage name
        else:
            print("ERROR: invalid stage name")
            pipeline_utils.put_job_failure(job_id, "Invalid stage name")

    except Exception as e:
        print('[ERROR] Unable to create training job. Exception: ' + str(e))        
        print(traceback.format_exc())
        pipeline_utils.put_job_failure(job_id, str(e))
