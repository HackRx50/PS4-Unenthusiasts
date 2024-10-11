import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from settings import Settings

env = Settings()

class S3Storage:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=env.aws_access_key,
            aws_secret_access_key=env.aws_secret_key,
            region_name="ap-south-1"
        )

    def upload_file(self, filePath, object_name=None, metadata=None):
        """
        Uploads a file to the S3 bucket with optional metadata.
        
        :param file_name: Path to the file to upload
        :param object_name: S3 object name (optional). If not specified, the file_name is used.
        :param metadata: A dictionary of metadata to associate with the object (optional).
        :return: True if file was uploaded, else False
        """

        try:
            # Extra arguments to pass during upload
            extra_args = {"Metadata": metadata} if metadata else None
            
            # Upload the file with metadata if provided
            self.s3.upload_file(
                filePath,
                self.bucket_name,
                object_name,
                ExtraArgs=extra_args
            )
            print(f"File '{filePath}' uploaded to '{self.bucket_name}/{object_name}' with metadata: {metadata}.","HELLO1")
            return True
        except FileNotFoundError:
            print("The file was not found.")
            return False
        except NoCredentialsError:
            print("Credentials not available.")
            return False
        except ClientError as e:
            print(f"Client error occurred: {e}")
            return False

    def download_file(self, object_name, file_name):
        """
        Downloads a file from the S3 bucket.
        
        :param object_name: S3 object name
        :param file_name: Local path where the file will be saved
        :return: True if file was downloaded, else False
        """
        try:
            self.s3.download_file(self.bucket_name, object_name, file_name)
            print(f"File '{object_name}' downloaded from bucket '{self.bucket_name}' to '{file_name}'.")
            return True
        except NoCredentialsError:
            print("Credentials not available.")
            return False
        except ClientError as e:
            print(f"Client error occurred: {e}")
            return False

    def check_file_exists(self, object_name):
        """
        Checks if a file exists in the S3 bucket.
        
        :param object_name: S3 object name
        :return: True if the file exists, else False
        """
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=object_name)
            print(f"File '{object_name}' exists in bucket '{self.bucket_name}'.")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"File '{object_name}' does not exist in bucket '{self.bucket_name}'.")
                return False
            else:
                print(f"Client error occurred: {e}")
                return False

    def delete_file(self, object_name):
        """
        Deletes a file from the S3 bucket.
        
        :param object_name: S3 object name
        :return: True if file was deleted, else False
        """
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_name)
            print(f"File '{object_name}' deleted from bucket '{self.bucket_name}'.")
            return True
        except ClientError as e:
            print(f"Client error occurred: {e}")
            return False

    def get_file_metadata(self, object_name):
        """
        Retrieves the metadata of a file stored in the S3 bucket.
        
        :param object_name: S3 object name
        :return: Metadata dictionary if file exists, else None
        """
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=object_name)
            metadata = response.get("Metadata", {})
            print(f"Metadata for '{object_name}': {metadata}")
            return metadata
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"File '{object_name}' does not exist in bucket '{self.bucket_name}'.")
                return None
            else:
                print(f"Client error occurred: {e}")
                return None
