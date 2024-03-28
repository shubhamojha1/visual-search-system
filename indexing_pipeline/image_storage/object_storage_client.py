from minio import Minio
from minio.error import InvalidResponseError
import os

# Create a MinIO client
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)
# print(os.getcwd())

base_dir = './common/storage'
data_dirs = [os.path.join(base_dir, "data1"), os.path.join(base_dir, "data2"), os.path.join(base_dir, "data3")]
erasure_code_config = {"data": 2, "parity": 1}

# print(data_dirs)

bucket_name = "images"
try:
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name, erasure_code="myerasureset")
except Exception as err:
    pass  # Bucket already exists
except InvalidResponseError as err:
    print(err)


# image_path = ''
# object_name = ''

