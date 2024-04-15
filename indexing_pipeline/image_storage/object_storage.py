from minio import Minio
from minio.error import S3Error
from flask import Response
import io

def store_object(client, bucket_name, object_name, file_content): #file_path):
    try:
        # client.put_object(bucket_name, object_name, io.BytesIO(file_object), content_length)
        client.put_object(bucket_name, object_name, io.BytesIO(file_content), len(file_content))
        print("WORKS!!!!!!!!")
    except S3Error as err:
        print("An error occurred:", err)


def retrieve_object(client, bucket_name, object_name):
    try:
        # Retrieve the object from MinIO
        data = client.get_object(bucket_name, object_name)
        # Read the object data
        file_data = data.read()
        # Return the data as a Flask Response object
        print("****file_data ----> ", file_data)
        return Response(file_data, mimetype="image/jpeg")
    except S3Error as err:
        print("An error occurred:", err)
        return None # Or handle the error appropriately