"""
Test S3 Connection
Verify AWS credentials and S3 bucket access
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.config import settings
from app.services.s3_service import s3_service


def test_s3_connection():
    """Test S3 connection and bucket access"""
    print("=" * 60)
    print("Testing S3 Connection")
    print("=" * 60)
    
    # Check configuration
    print("\n1. Checking AWS Configuration...")
    print(f"   AWS Region: {settings.AWS_REGION}")
    print(f"   S3 Bucket: {settings.S3_BUCKET_NAME}")
    print(f"   Access Key ID: {settings.AWS_ACCESS_KEY_ID[:10]}..." if settings.AWS_ACCESS_KEY_ID else "   Access Key ID: Not set")
    
    if not settings.AWS_ACCESS_KEY_ID or not settings.S3_BUCKET_NAME:
        print("\n❌ ERROR: AWS credentials not configured!")
        print("   Please set the following in your .env file:")
        print("   - AWS_ACCESS_KEY_ID")
        print("   - AWS_SECRET_ACCESS_KEY")
        print("   - S3_BUCKET_NAME")
        return False
    
    # Test bucket access
    print("\n2. Testing Bucket Access...")
    try:
        # List bucket (this will fail if credentials are wrong or bucket doesn't exist)
        response = s3_service.s3_client.list_objects_v2(
            Bucket=settings.S3_BUCKET_NAME,
            MaxKeys=1
        )
        print(f"   ✅ Successfully connected to bucket: {settings.S3_BUCKET_NAME}")
    except Exception as e:
        print(f"   ❌ ERROR: Cannot access bucket")
        print(f"   Error: {str(e)}")
        return False
    
    # Test file upload
    print("\n3. Testing File Upload...")
    try:
        test_content = b"This is a test file for S3 connectivity"
        test_filename = "test-connection.txt"
        
        url = s3_service.upload_file(
            file_content=test_content,
            file_name=test_filename,
            content_type="text/plain",
            folder="test"
        )
        
        if url:
            print(f"   ✅ Successfully uploaded test file")
            print(f"   URL: {url}")
        else:
            print(f"   ❌ ERROR: Upload returned None")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: Failed to upload file")
        print(f"   Error: {str(e)}")
        return False
    
    # Test file deletion
    print("\n4. Testing File Deletion...")
    try:
        success = s3_service.delete_file(url)
        if success:
            print(f"   ✅ Successfully deleted test file")
        else:
            print(f"   ⚠️  Warning: Delete returned False (file might not exist)")
    except Exception as e:
        print(f"   ❌ ERROR: Failed to delete file")
        print(f"   Error: {str(e)}")
        return False
    
    # All tests passed
    print("\n" + "=" * 60)
    print("✅ All S3 tests passed!")
    print("=" * 60)
    print("\nYou're ready to upload files!")
    print("\nNext steps:")
    print("1. Start the server: uvicorn app.main:app --reload")
    print("2. Go to: http://127.0.0.1:8000/api/docs")
    print("3. Test the photo upload endpoints")
    
    return True


if __name__ == "__main__":
    try:
        test_s3_connection()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
