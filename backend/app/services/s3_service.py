"""
AWS S3 Service
Handles file uploads to S3 bucket
"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional
from uuid import uuid4
import os
from datetime import datetime
from app.core.config import settings


class S3Service:
    """S3 file storage service"""
    
    def __init__(self):
        """Initialize S3 client"""
        if not settings.AWS_ACCESS_KEY_ID or not settings.S3_BUCKET_NAME:
            raise ValueError("AWS credentials not configured. Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and S3_BUCKET_NAME in .env")
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str,
        folder: str = "issues"
    ) -> Optional[str]:
        """
        Upload file to S3
        
        Args:
            file_content: File bytes
            file_name: Original file name
            content_type: MIME type
            folder: S3 folder (default: issues)
            
        Returns:
            URL of uploaded file or None if failed
        """
        try:
            # Generate unique file name
            file_extension = os.path.splitext(file_name)[1]
            unique_name = f"{uuid4()}{file_extension}"
            
            # Create S3 key with folder structure
            s3_key = f"{folder}/{unique_name}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                # Make file publicly readable (optional - remove if you want private files)
                # ACL='public-read'
            )
            
            # Generate URL
            url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            return url
            
        except ClientError as e:
            print(f"Error uploading file to S3: {str(e)}")
            return None
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from S3
        
        Args:
            file_url: Full S3 URL of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract S3 key from URL
            # URL format: https://bucket.s3.region.amazonaws.com/folder/file.ext
            key = file_url.split(f".amazonaws.com/")[1]
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except (ClientError, IndexError) as e:
            print(f"Error deleting file from S3: {str(e)}")
            return False
    
    def generate_presigned_url(self, file_url: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate presigned URL for temporary access to private files
        
        Args:
            file_url: Full S3 URL of the file
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        try:
            # Extract S3 key from URL
            key = file_url.split(f".amazonaws.com/")[1]
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expiration
            )
            return presigned_url
            
        except (ClientError, IndexError) as e:
            print(f"Error generating presigned URL: {str(e)}")
            return None
    
    @staticmethod
    def validate_image_file(filename: str, content_type: str, file_size: int) -> tuple[bool, str]:
        """
        Validate image file
        
        Args:
            filename: File name
            content_type: MIME type
            file_size: File size in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file extension
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
        file_ext = os.path.splitext(filename.lower())[1]
        
        if file_ext not in allowed_extensions:
            return False, f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"
        
        # Check content type
        allowed_content_types = {
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'image/webp',
            'image/gif'
        }
        
        if content_type not in allowed_content_types:
            return False, f"Invalid content type: {content_type}"
        
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if file_size > max_size:
            return False, f"File too large. Maximum size: 5MB, your file: {file_size / (1024 * 1024):.2f}MB"
        
        return True, ""


# Create singleton instance only if AWS credentials are configured
try:
    s3_service = S3Service()
except ValueError as e:
    print(f"Warning: S3Service not initialized - {str(e)}")
    s3_service = None
