from minio import Minio
from minio.error import ResponseError

# Create a MinIO client
client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False,
)