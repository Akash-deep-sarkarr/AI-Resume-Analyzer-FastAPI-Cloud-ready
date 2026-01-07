from __future__ import annotations

import os
import uuid
from typing import Optional

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
except Exception:  # pragma: no cover - defensive import
    boto3 = None  # type: ignore
    BotoCoreError = ClientError = NoCredentialsError = Exception  # type: ignore


def _guess_content_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return "application/pdf"
    if lower.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "text/plain"


def store_resume_file(file_bytes: bytes, filename: str) -> Optional[str]:
    """Upload resume bytes to S3 if configuration is available.

    Returns a simple S3 URI (s3://bucket/key) on success, otherwise None.
    This keeps the app runnable without AWS config but cloud-ready for deployment.
    """
    bucket = os.getenv("RESUME_BUCKET_NAME")
    region = os.getenv("AWS_REGION", "us-east-1")

    if not bucket or boto3 is None:
        return None

    key = f"resumes/{uuid.uuid4()}_{filename}"

    try:
        s3 = boto3.client("s3", region_name=region)
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_bytes,
            ContentType=_guess_content_type(filename),
        )
        return f"s3://{bucket}/{key}"
    except (BotoCoreError, ClientError, NoCredentialsError, Exception):
        # Swallow errors to avoid breaking the core AI flow if S3 is misconfigured
        return None
