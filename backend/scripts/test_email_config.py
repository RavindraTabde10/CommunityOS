"""
Test Email Service Configuration
Checks if email service is properly configured and can send test emails
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import asyncio
from app.services.email_service import EmailService
from app.core.config import Settings

async def test_email_config():
    """Test email service configuration"""
    settings = Settings()
    
    print("=" * 60)
    print("EMAIL SERVICE CONFIGURATION CHECK")
    print("=" * 60)
    
    # Check configuration
    print("\n📋 Configuration:")
    print(f"   RESEND_API_KEY: {'✓ Set' if settings.RESEND_API_KEY and settings.RESEND_API_KEY != 'your-resend-api-key' else '✗ Not configured'}")
    if settings.RESEND_API_KEY and settings.RESEND_API_KEY != 'your-resend-api-key':
        print(f"   API Key Preview: {settings.RESEND_API_KEY[:10]}...")
    
    print(f"   FROM_EMAIL: {settings.FROM_EMAIL if settings.FROM_EMAIL else '✗ Not configured'}")
    print(f"   Email Service Ready: {'✓ Yes' if EmailService.is_configured() else '✗ No'}")
    
    # Test email sending (optional)
    if EmailService.is_configured():
        print("\n" + "=" * 60)
        print("SEND TEST EMAIL")
        print("=" * 60)
        
        test_email = input("\nEnter email to send test to (or press Enter to skip): ").strip()
        
        if test_email:
            print(f"\n📧 Sending test email to {test_email}...")
            success = await EmailService.send_password_reset_email(
                to_email=test_email,
                reset_token="test_token_123456789",
                user_name="Test User"
            )
            
            if success:
                print("\n✓ Test email sent successfully!")
                print("  Check your inbox (and spam folder)")
            else:
                print("\n✗ Failed to send test email")
                print("  Check the error message above")
        else:
            print("\nSkipping test email send.")
    else:
        print("\n⚠️  Email service not configured.")
        print("\nTo configure:")
        print("1. Get API key from https://resend.com")
        print("2. Add to .env file:")
        print("   RESEND_API_KEY=re_your_api_key")
        print("   FROM_EMAIL=noreply@yourdomain.com")
        print("3. Restart backend server")
        print("\nSee backend/EMAIL_SETUP.md for detailed instructions")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_email_config())
