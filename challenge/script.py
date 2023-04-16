import os
import boto3
import argparse
import subprocess

def process_video(input_file_path, output_file_path):
    """
    Process a video file by resizing it.
    """
    # ffmpeg command to resize the video to a width of 320 pixels and adjusts the height proportionally.
    command = "ffmpeg -i  {} -vf scale=320:-2 -c:a copy {}".format(input_file_path, output_file_path)
    
    try:
        subprocess.run(command, check= True)
        print("ffmpeg ran successfully")
    
    except subprocess.CalledProcessError as e:
        print("Error:", e)


def upload_to_s3(local_file_path, s3_bucket_name, s3_object_key):
    """
    Upload a file to an S3 bucket using Boto3 library.
    """
    s3 = boto3.client('s3')
    try:
        s3.upload_file(local_file_path, s3_bucket_name, s3_object_key)
        print(f"File uploaded to s3://{s3_bucket_name}/{s3_object_key}")
    except Exception as e:
        print(f"Error uploading file to S3: {e}")
        raise e

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Process and upload a video file to S3.")
    parser.add_argument("input_file_path", type=str, help="Input file path.")
    parser.add_argument("output_file_path", type=str, help="Output file path.")
    parser.add_argument("s3_bucket_name", type=str, help="S3 bucket name.")
    parser.add_argument("s3_object_key", type=str, help="S3 object key.")
    args = parser.parse_args()

    # Validate input file and output file
    if not os.path.isfile(args.input_file_path):
        raise FileNotFoundError("Input file does not exist.")
    if os.path.isfile(args.output_file_path):
        raise FileExistsError("Output file already exists. Please specify a different file path.")

    # Process the video file
    process_video(args.input_file_path, args.output_file_path)

    # Upload the processed file to S3
    upload_to_s3(args.output_file_path, args.s3_bucket_name, args.s3_object_key)

