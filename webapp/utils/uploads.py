from webapp.utils.tools import generate_string
import boto3
from os import environ

s3 = boto3.client(
    's3',
    aws_access_key_id = environ.get('S3_ACCESS'),
    aws_secret_access_key = environ.get('S3_KEY')
)

def upload_file(upload, bucket):
    ''' Function to upload file to S3'''
    try:
        ext = upload.filename.split('.')
        filename = f'{generate_string(35)}.{ext[-1]}'
        s3.upload_fileobj(
            upload,
            bucket,
            filename,
            ExtraArgs={
                "ContentType" : upload.content_type,
                'Metadata':{
                    "original_filename" : upload.filename
                }
            }
        )
        return filename
    except Exception as e:
        with open('/logging/log.txt', 'a') as l:
            l.write(e + '\n')
            l.close()

def delete_upload(upload, bucket):
    s3.delete_object(Bucket=bucket, Key=upload)

def download_file(upload, bucket):
    file = s3.get_object(Bucket=bucket, Key=upload)

    return {
        'file' : file['Body'].read(),
        'original_filename' : file['Metadata']['original_filename']
    }

def copy_file(upload, bucket, new_bucket):
    ''' after user makes a purchase, copy file to another bucket; so if the seller deletes the file, its still available for the buyer to download'''
    s3.copy_object(
        ACL='public-read',
        Bucket=new_bucket,
        CopySource={'Bucket': bucket, 'Key': upload},
        Key=upload
    )
