import os
import boto3
import subprocess
import botocore
import json

def lambda_handler(event, context):

    s3 = boto3.client("s3")
    sns = boto3.client("sns")

    for record in event['Records']:

        topic_arn = record['Sns']['TopicArn']
        message = record['Sns']['Message']
        message_dict = json.loads(message)
        bucket_name = message_dict['Records'][0]['s3']['bucket']['name']
        object_key = message_dict['Records'][0]['s3']['object']['key']
        file_name = os.path.splitext(os.path.basename(object_key))[0] 

        try:
            s3.download_file(bucket_name, "{}.mp4".format(file_name) , "/tmp/{}.mp4".format(file_name))
            print("download successful")

        except botocore.exceptions.ClientError as e:
            print(f"Error downloading file from S3: {e.response['Error']['Message']}")
            return {'statusCode': 500, 'body': 'Error downloading file from S3'}


        # ffmpeg command to take a screenshot
        command = "/var/task/ffmpeg -i /tmp/{}.mp4 -ss 00:00:01.000 -vframes 1 /tmp/{}.png".format(file_name, file_name)
        try:
            #print(command)
            #os.system(command)
            subprocess.run(command, check= True)
            print("ffmpeg ran successfully")
        
        except subprocess.CalledProcessError as e:
            print(f"Error running ffmpeg command: {e}")
            return {'statusCode': 500, 'body': 'Error running ffmpeg command'}
                
        try:
            s3.upload_file("/tmp/{}.png".format(file_name), bucket_name, "thumbnails/{}.png".format(file_name))
            print("thumbnail uploaded")
            
                        
        except botocore.exceptions.ClientError as e:
            print(f"Error uploading thumbnail to S3: {e.response['Error']['Message']}")
            return {'statusCode': 500, 'body': 'Error uploading thumbnail to S3'}

        try:
            message = f"Processing job for {object_key} is complete."
            sns.publish(TopicArn=topic_arn, Message=message)
            print("topic published")
            return {'statusCode': 200, 'body': 'Thumbnail created'}

        except botocore.exceptions.ClientError as e:
            print(f"Error publishing message to the topic: {e.response['Error']['Message']}")
            return {'statusCode': 500, 'body': 'Error publishing message to SNS'}
    