import os
import boto3
import argparse
import subprocess
import yaml
import sys
import time

def process_video(input_file_path):
    """
    Process a video file by resizing it.
    """ 

    # Time logging
    start = time.time()
    
    # Extract name and extension
    name, extension = os.path.splitext(os.path.basename(input_file_path))
    save_location = os.path.dirname(input_file_path) +  "/processed-"+ name + extension

    # ffmpeg command to resize the video to a width of 320 pixels and adjusts the height proportionally.
    command = "ffmpeg -i  {} -vf scale=320:-2 -c:a copy {}".format(input_file_path, save_location )
    
    try:
        subprocess.run(command, check= True)
        print("ffmpeg ran successfully")
        return save_location, time.time() - start
    
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        raise e


def create_thumbnail(input_file_path):
    """
    Create a thumbnail from a video.
    """

    # Time logging
    start = time.time()
    
    # Extract name and path
    name, extension = os.path.splitext(os.path.basename(input_file_path))
    save_location = os.path.dirname(input_file_path) +  "/"+  name 

    # ffmpeg command to resize the video to a width of 320 pixels and adjusts the height proportionally.
    command = "ffmpeg -i {} -ss 00:00:01.000 -vframes 1 {}.png".format(input_file_path, save_location)
    
    try:
        subprocess.run(command, check= True)
        print("ffmpeg ran successfully")
        return save_location + ".png" , time.time() - start
    
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        raise e



def upload_to_s3(local_file_path, s3_bucket_name):
    """
    Upload a file to an S3 bucket using Boto3 library.
    """

    # Time logging
    start = time.time()

    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_file_path, s3_bucket_name, os.path.basename(local_file_path))
        print(f"File uploaded to s3://{s3_bucket_name}")
        return time.time() - start
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        raise e

def read_yaml_configs(yaml_path):
    """
    Read the relevant info from config
    """
    # Time logging
    start = time.time()

    with open(yaml_path, "r") as stream:
        try:
            result = yaml.safe_load(stream)
            return result["Resources"]["MainBucket"]["Properties"]["BucketName"], time.time() - start
        except yaml.YAMLError as exc:
            print("Erorr:", exc)
            raise exc


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process and upload a video file to S3.")
    parser.add_argument("input_file_path", type=str, help="Input file path.")
    parser.add_argument("process_yaml_path", type=str, help="Video Processing YAML path.")
    parser.add_argument("thubmnail_yaml_path", type=str, help="Thumbnail YAML path.")
    args = parser.parse_args()

    # Validate input file and output file
    if not os.path.isfile(args.input_file_path):
            raise FileNotFoundError("Input file does not exist.")
    if not os.path.isfile(args.process_yaml_path):
            raise FileNotFoundError("Video Processing YAML does not exist.")
    if not os.path.isfile(args.thubmnail_yaml_path):
            raise FileNotFoundError("Thumbnail YAML does not exist.")

    # Read in the bucekts and save location from yaml files
    bucket1_name, time_read_1 = read_yaml_configs(args.process_yaml_path)
    bucket2_name, time_read_2 = read_yaml_configs(args.thubmnail_yaml_path)

    # Processing Step 
    save_location, time_process = process_video(args.input_file_path)
    # Upload the processed file to S3
    time_save_process = upload_to_s3(save_location, bucket1_name)

    
    # Thumbnail Step
    save_location, time_thumbnail = create_thumbnail(save_location)
    # Upload the processed file to S3
    time_save_thumbnail = upload_to_s3(save_location, bucket2_name)

    print("Read Config 1:{0}, Process Vid:{1}, Upload:{2} \nRead Config 2:{3}, Create Thumbnail:{4}, Upload:{5} ".format(time_read_1, time_process, time_save_process, time_read_2, time_thumbnail ,time_save_thumbnail))

