from functools import lru_cache

from boto3.session import Session

from ..config import settings


class S3Client:
    session= Session(
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key
    )
    bucket = session.resource("s3").Bucket(settings.s3_bucket_name)

    @classmethod
    @lru_cache
    def get_object(cls, key: str):
        assert key is not None, "key must not be None"
        return cls.bucket.Object(key)

    @classmethod
    @lru_cache
    def list_objects(cls, prefix: str = ""):
        return cls.bucket.objects.filter(Prefix=prefix)
