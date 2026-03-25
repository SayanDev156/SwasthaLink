"""
AWS S3 Service
Handles file uploads with 24-hour auto-delete lifecycle
Phase 7 - Post-MVP feature for PDF/image uploads
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load AWS credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Initialize S3 client
s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        logger.info("AWS S3 client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {e}")
else:
    logger.warning("AWS credentials not found in environment variables")


class S3ServiceError(Exception):
    """Custom exception for S3 service errors"""
    pass


def _get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename

    Args:
        filename: Original filename

    Returns:
        File extension (e.g., '.pdf', '.jpg')
    """
    return os.path.splitext(filename)[1].lower()


def _generate_unique_filename(session_id: str, original_filename: str) -> str:
    """
    Generate unique S3 object key

    Args:
        session_id: Session ID
        original_filename: Original filename

    Returns:
        S3 object key (e.g., 'uploads/session-id/filename.pdf')
    """
    extension = _get_file_extension(original_filename)
    clean_filename = f"{uuid.uuid4()}{extension}"
    return f"uploads/{session_id}/{clean_filename}"


async def upload_file(
    file_content: bytes,
    filename: str,
    session_id: str,
    content_type: str = "application/octet-stream"
) -> Dict[str, Any]:
    """
    Upload file to S3 with 24-hour lifecycle

    Args:
        file_content: Binary file content
        filename: Original filename
        session_id: Session ID for organizing files
        content_type: MIME type

    Returns:
        Dict with upload info:
        {
            "success": bool,
            "s3_key": str,
            "url": str,
            "expires_at": str (ISO 8601)
        }
    """
    try:
        if not s3_client or not S3_BUCKET_NAME:
            raise S3ServiceError("S3 client not initialized. Check AWS credentials and bucket name.")

        # Generate unique S3 key
        s3_key = _generate_unique_filename(session_id, filename)

        # Calculate expiration (24 hours from now)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        # Upload metadata
        metadata = {
            "session_id": session_id,
            "original_filename": filename,
            "uploaded_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat()
        }

        # Upload to S3
        logger.info(f"Uploading file to S3: {s3_key}")
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type,
            Metadata=metadata
        )

        # Generate presigned URL (valid for 24 hours)
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET_NAME, 'Key': s3_key},
            ExpiresIn=86400  # 24 hours in seconds
        )

        logger.info(f"File uploaded successfully: {s3_key}")

        return {
            "success": True,
            "s3_key": s3_key,
            "url": url,
            "expires_at": expires_at.isoformat(),
            "bucket": S3_BUCKET_NAME,
            "size_bytes": len(file_content)
        }

    except NoCredentialsError:
        logger.error("AWS credentials not found")
        raise S3ServiceError("AWS credentials not configured")

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_msg = e.response.get('Error', {}).get('Message', str(e))
        logger.error(f"S3 upload failed: {error_code} - {error_msg}")
        raise S3ServiceError(f"Failed to upload file: {error_msg}")

    except Exception as e:
        logger.error(f"Unexpected error uploading file: {e}")
        raise S3ServiceError(f"Failed to upload file: {str(e)}")


async def get_file(s3_key: str) -> Dict[str, Any]:
    """
    Retrieve file from S3

    Args:
        s3_key: S3 object key

    Returns:
        Dict with file content and metadata
    """
    try:
        if not s3_client or not S3_BUCKET_NAME:
            raise S3ServiceError("S3 client not initialized")

        logger.info(f"Retrieving file from S3: {s3_key}")

        # Get object
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)

        # Read file content
        file_content = response['Body'].read()

        # Get metadata
        metadata = response.get('Metadata', {})

        return {
            "success": True,
            "content": file_content,
            "content_type": response.get('ContentType'),
            "size_bytes": response.get('ContentLength'),
            "metadata": metadata,
            "last_modified": response.get('LastModified').isoformat() if response.get('LastModified') else None
        }

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == 'NoSuchKey':
            logger.warning(f"File not found: {s3_key}")
            raise S3ServiceError(f"File not found or already expired: {s3_key}")
        else:
            logger.error(f"S3 get failed: {error_code}")
            raise S3ServiceError(f"Failed to retrieve file: {error_code}")

    except Exception as e:
        logger.error(f"Unexpected error retrieving file: {e}")
        raise S3ServiceError(f"Failed to retrieve file: {str(e)}")


async def delete_file(s3_key: str) -> Dict[str, Any]:
    """
    Manually delete file from S3 (before 24-hour lifecycle)

    Args:
        s3_key: S3 object key

    Returns:
        Dict with deletion status
    """
    try:
        if not s3_client or not S3_BUCKET_NAME:
            raise S3ServiceError("S3 client not initialized")

        logger.info(f"Deleting file from S3: {s3_key}")

        # Delete object
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)

        logger.info(f"File deleted successfully: {s3_key}")

        return {
            "success": True,
            "s3_key": s3_key,
            "message": "File deleted successfully"
        }

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"S3 delete failed: {error_code}")
        raise S3ServiceError(f"Failed to delete file: {error_code}")

    except Exception as e:
        logger.error(f"Unexpected error deleting file: {e}")
        raise S3ServiceError(f"Failed to delete file: {str(e)}")


def check_s3_health() -> Dict[str, Any]:
    """
    Check if S3 service is accessible and healthy

    Returns:
        Dict with status information
    """
    try:
        if not s3_client or not S3_BUCKET_NAME:
            return {
                "status": "down",
                "message": "S3 client not initialized. Check credentials and bucket name.",
                "available": False
            }

        # Try to head bucket (check if bucket exists and is accessible)
        s3_client.head_bucket(Bucket=S3_BUCKET_NAME)

        # Check lifecycle configuration
        try:
            lifecycle = s3_client.get_bucket_lifecycle_configuration(Bucket=S3_BUCKET_NAME)
            lifecycle_configured = True
        except ClientError as e:
            if e.response.get('Error', {}).get('Code') == 'NoSuchLifecycleConfiguration':
                lifecycle_configured = False
            else:
                raise

        return {
            "status": "ok",
            "message": "S3 service is healthy",
            "available": True,
            "bucket": S3_BUCKET_NAME,
            "region": AWS_REGION,
            "lifecycle_configured": lifecycle_configured
        }

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"S3 health check failed: {error_code}")
        return {
            "status": "down",
            "message": f"S3 error: {error_code}",
            "available": False
        }

    except Exception as e:
        logger.error(f"S3 health check failed: {e}")
        return {
            "status": "down",
            "message": str(e),
            "available": False
        }


# Lifecycle configuration helper (documentation)
S3_LIFECYCLE_POLICY = {
    "Rules": [
        {
            "Id": "auto-delete-24hr",
            "Status": "Enabled",
            "Prefix": "uploads/",
            "Expiration": {
                "Days": 1
            }
        }
    ]
}


def setup_lifecycle_policy() -> Dict[str, Any]:
    """
    Setup 24-hour auto-delete lifecycle policy on S3 bucket
    (Run this once during setup)

    Returns:
        Dict with setup status
    """
    try:
        if not s3_client or not S3_BUCKET_NAME:
            raise S3ServiceError("S3 client not initialized")

        logger.info(f"Setting up lifecycle policy on bucket: {S3_BUCKET_NAME}")

        # Put lifecycle configuration
        s3_client.put_bucket_lifecycle_configuration(
            Bucket=S3_BUCKET_NAME,
            LifecycleConfiguration=S3_LIFECYCLE_POLICY
        )

        logger.info("Lifecycle policy configured successfully")

        return {
            "success": True,
            "message": "24-hour auto-delete lifecycle policy configured",
            "policy": S3_LIFECYCLE_POLICY
        }

    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"Failed to setup lifecycle policy: {error_code}")
        raise S3ServiceError(f"Failed to setup lifecycle policy: {error_code}")

    except Exception as e:
        logger.error(f"Unexpected error setting up lifecycle policy: {e}")
        raise S3ServiceError(f"Failed to setup lifecycle policy: {str(e)}")


def get_lifecycle_instructions() -> str:
    """
    Get instructions for manually configuring S3 lifecycle policy

    Returns:
        Instructions string
    """
    return f"""
    📦 **Configure S3 24-Hour Auto-Delete Lifecycle:**

    **Option 1: Via AWS Console**
    1. Go to AWS S3 Console
    2. Select bucket: {S3_BUCKET_NAME or '<your-bucket>'}
    3. Go to "Management" tab
    4. Click "Create lifecycle rule"
    5. Rule name: auto-delete-24hr
    6. Prefix: uploads/
    7. Enable "Expire current versions of objects"
    8. Days after object creation: 1
    9. Save rule

    **Option 2: Via Python (run once)**
    ```python
    from s3_service import setup_lifecycle_policy
    result = setup_lifecycle_policy()
    print(result)
    ```

    **Option 3: Via AWS CLI**
    ```bash
    aws s3api put-bucket-lifecycle-configuration \\
      --bucket {S3_BUCKET_NAME or '<your-bucket>'} \\
      --lifecycle-configuration file://lifecycle.json
    ```

    Where lifecycle.json contains:
    {S3_LIFECYCLE_POLICY}

    **Why 24 hours?**
    - Compliance: Files auto-delete after processing
    - Privacy: Minimizes PHI exposure window
    - Cost: Reduces storage costs

    **Production Note:**
    For true HIPAA compliance, consider using server-side encryption (SSE-KMS)
    and bucket policies restricting access.
    """
