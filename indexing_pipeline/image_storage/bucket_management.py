# from minio import Minio
# # from minio.error import 
# from minio.error import S3Error,InvalidResponseError #BucketAlreadyExists, BucketAlreadyOwnedByYou
# import os

# # Create a MinIO client
# client = Minio(
#     "localhost:9000",
#     access_key="minioadmin",
#     secret_key="minioadmin",
#     secure=False,
# )
# # print(os.getcwd())

# base_dir = './common/storage'
# data_dirs = [os.path.join(base_dir, "data1"), os.path.join(base_dir, "data2"), os.path.join(base_dir, "data3")]
# erasure_code_config = {"data": 2, "parity": 1}

# bucket_name = "images"

# # Attempt to create the bucket
# # try:
# #     client.make_bucket(bucket_name)
# # except S3Error as err:
# #     # Check if the error is due to the bucket already existing
# #     if 'BucketAlreadyExists' in str(err):
# #         print("Bucket already exists.")
# #     else:
# #         print("An error occurred:", err)
# ################################################
# if not client.bucket_exists(bucket_name):
#     # Attempt to create the bucket if it doesn't exist
#     try:
#         client.make_bucket(bucket_name)
#     except S3Error as err:
#         print("An error occurred:", err)
# else:
#     print("Bucket already exists.")

# image_path = './test_image.jpeg'
# object_name = 'test_image.jpeg'

# try:
#     client.fput_object(bucket_name, object_name, image_path)
# except InvalidResponseError as err:
#     print(err)

# try:
#     data = client.get_object(bucket_name, object_name)
#     with open("retrieved_image.jpg", "wb") as file_data:
#         for d in data.stream(32*1024):
#             file_data.write(d)
# except InvalidResponseError as err:
#     print(err)

from minio import Minio
from minio.error import S3Error

def create_bucket(client, bucket_name):
    if not client.bucket_exists(bucket_name):
        try:
            client.make_bucket(bucket_name)
        except S3Error as err:
            print("An error occurred:", err)
    else:
        print("Bucket already exists.")
