from minio import Minio
from minio.error import S3Error
import io

def store_object(client, bucket_name, object_name, file_content): #file_path):
    try:
        # client.fput_object(bucket
        # file_content = file_object.read()
        # content_length = len(file_content)
        print("nfkjdnfkjndafd")
        # client.put_object(bucket_name, object_name, io.BytesIO(file_object), content_length)
        client.put_object(bucket_name, object_name, io.BytesIO(file_content), len(file_content))
        print("WORKS!!!!!!!!")
    except S3Error as err:
        print("An error occurred:", err)

def retrieve_object(client, bucket_name, object_name, file_path):
    try:
        data = client.get_object(bucket_name, object_name)
        with open(file_path, "wb") as file_data:
            for d in data.stream(32*1024):
                file_data.write(d)
    except S3Error as err:
        print("An error occurred:", err)
