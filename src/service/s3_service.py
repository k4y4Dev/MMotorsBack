# services/s3_service.py
import boto3
from PIL import Image
from io import BytesIO
from config import settings

class S3Service:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket = settings.aws_bucket_name

    def compress_image(self, contents: bytes, content_type: str) -> BytesIO:
        image = Image.open(BytesIO(contents))
        
        # Convertir en RGB si nécessaire (ex: PNG avec transparence)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Redimensionner si trop grande
        max_size = (1200, 1200)
        image.thumbnail(max_size)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        return buffer

    def upload_image(self, contents: bytes, filename: str, content_type: str) -> str:
        # Compression avec Pillow
        buffer = self.compress_image(contents, content_type)

        # Upload vers S3
        key = f"cars/{filename}"
        self.s3.upload_fileobj(
            buffer,
            self.bucket,
            key,
            ExtraArgs={'ContentType': 'image/jpeg'}
        )

        # Générer une presigned URL valable 1 heure
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': key},
            ExpiresIn=3600
        )
        return url

    def delete_image(self, filename: str):
        self.s3.delete_object(
            Bucket=self.bucket,
            Key=f"cars/{filename}"
        )

s3_service = S3Service()