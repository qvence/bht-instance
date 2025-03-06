import boto3
from botocore.exceptions import ClientError

def create_ec2_instance(instance_name, ami_id='ami-07a64b147d3500b6a'):
    """Створює EC2 інстанс t2.micro."""
    ec2 = boto3.resource('ec2')
    try:
        instances = ec2.create_instances(
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType='t3.micro',
            TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': instance_name}]}]
        )
        instance = instances[0]
        instance.wait_until_running()
        print(f"Інстанс {instance_name} створено: {instance.id}")
        return instance
    except ClientError as e:
        print(f"Помилка створення інстансу: {e}")
        return None

def create_s3_bucket(bucket_name, region='eu-north-1'):
    """Створює S3 бакет."""
    s3_client = boto3.client('s3', region_name=region)
    try:
        location = {'LocationConstraint': region}
        if region == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print(f"Бакет {bucket_name} створено.")
        return bucket_name
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Бакет {bucket_name} вже існує.")
            return bucket_name
        else:
            print(f"Помилка створення бакету: {e}")
            return None

def upload_file_to_s3(bucket_name, file_path, s3_key):
    """Завантажує файл в S3 бакет."""
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"Файл {file_path} завантажено до {bucket_name}/{s3_key}")
    except ClientError as e:
        print(f"Помилка завантаження файлу: {e}")

def download_file_from_s3(bucket_name, s3_key, file_path):
    """Завантажує файл з S3 бакету."""
    s3 = boto3.client('s3')
    try:
        s3.download_file(bucket_name, s3_key, file_path)
        print(f"Файл {bucket_name}/{s3_key} завантажено до {file_path}")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"Файл {s3_key} не знайдено в бакеті {bucket_name}.")
        else:
            print(f"Помилка завантаження файлу: {e}")

def delete_s3_bucket(bucket_name):
    """Видаляє S3 бакет."""
    s3 = boto3.resource('s3')
    try:
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        print(f"Бакет {bucket_name} видалено.")
    except ClientError as e:
        print(f"Помилка видалення бакету: {e}")

def terminate_ec2_instance(instance_id):
    """Завершує EC2 інстанс."""
    ec2 = boto3.resource('ec2')
    try:
        instance = ec2.Instance(instance_id)
        instance.terminate()
        instance.wait_until_terminated()
        print(f"Інстанс {instance_id} завершено.")
    except ClientError as e:
        print(f"Помилка завершення інстансу: {e}")

# Приклад використання
instance_name = "shokalo-instance"
bucket_name = "shokalo-bucket"
file_path = "local_file.txt"
s3_key = "remote_file.txt"

instance = create_ec2_instance(instance_name)
if instance:
    create_s3_bucket(bucket_name)
    with open(file_path, 'w') as f:
        f.write("Привіт Світ!")
    upload_file_to_s3(bucket_name, file_path, s3_key)
    download_file_from_s3(bucket_name, s3_key, file_path)
    download_file_from_s3(bucket_name, s3_key, "downloaded_file.txt")
    terminate_ec2_instance(instance.id)
    delete_s3_bucket(bucket_name)
