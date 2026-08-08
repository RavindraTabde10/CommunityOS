"""
Email Service
Handles sending emails using Resend API
"""

import resend
import requests
import ssl
import os
from typing import Optional
from app.core.config import Settings

settings = Settings()

# Configure Resend API
if settings.RESEND_API_KEY and settings.RESEND_API_KEY != "your-resend-api-key":
    resend.api_key = settings.RESEND_API_KEY

# Disable SSL verification warnings for corporate environments
# Note: This is for development/corporate proxy environments only
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class EmailService:
    """Email service for sending notifications"""
    
    @staticmethod
    def is_configured() -> bool:
        """Check if email service is properly configured"""
        return (
            settings.RESEND_API_KEY is not None 
            and settings.RESEND_API_KEY != "your-resend-api-key"
            and settings.FROM_EMAIL is not None
        )
    
    @staticmethod
    async def send_password_reset_email(
        to_email: str,
        reset_token: str,
        user_name: str
    ) -> bool:
        """
        Send password reset email
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            user_name: User's name
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not EmailService.is_configured():
            print("⚠️  Email service not configured. Reset token:", reset_token)
            return False
        
        try:
            # Generate reset link (update with your frontend URL)
            frontend_url = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:5173"
            reset_link = f"{frontend_url}/reset-password?token={reset_token}"
            
            # HTML email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #1976d2;
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: #f9f9f9;
                        padding: 30px;
                        border-radius: 0 0 5px 5px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 30px;
                        background-color: #1976d2;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        font-size: 12px;
                        color: #666;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user_name},</p>
                        
                        <p>We received a request to reset your password for your CommunityOS.ai account.</p>
                        
                        <p>Click the button below to reset your password:</p>
                        
                        <a href="{reset_link}" class="button">Reset Password</a>
                        
                        <p>Or copy and paste this link into your browser:</p>
                        <p style="word-break: break-all; color: #1976d2;">{reset_link}</p>
                        
                        <p><strong>This link will expire in 1 hour.</strong></p>
                        
                        <p>If you didn't request a password reset, you can safely ignore this email. Your password will remain unchanged.</p>
                        
                        <p>Best regards,<br>The CommunityOS.ai Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message from CommunityOS.ai</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text alternative
            text_content = f"""
            Password Reset Request
            
            Hi {user_name},
            
            We received a request to reset your password for your CommunityOS.ai account.
            
            Click the link below to reset your password:
            {reset_link}
            
            This link will expire in 1 hour.
            
            If you didn't request a password reset, you can safely ignore this email.
            
            Best regards,
            The CommunityOS.ai Team
            """
            
            # Send email using Resend API (direct HTTP call for SSL flexibility)
            params = {
                "from": settings.FROM_EMAIL,
                "to": [to_email],
                "subject": "Reset Your Password - CommunityOS.ai",
                "html": html_content,
                "text": text_content,
            }
            
            # Use requests directly to handle SSL verification in corporate environments
            headers = {
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Disable SSL verification for corporate proxy environments
            # Set VERIFY_SSL=false in .env to disable verification
            verify_ssl = os.getenv("VERIFY_SSL", "false").lower() != "false"
            
            response = requests.post(
                "https://api.resend.com/emails",
                json=params,
                headers=headers,
                verify=verify_ssl  # Allows working through corporate proxies
            )
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✓ Password reset email sent to {to_email}")
                print(f"  Email ID: {response_data.get('id', 'N/A')}")
                return True
            else:
                print(f"✗ Failed to send email: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            print(f"✗ Failed to send password reset email: {str(e)}")
            return False
    
    @staticmethod
    async def send_welcome_email(
        to_email: str,
        user_name: str
    ) -> bool:
        """
        Send welcome email to new user
        
        Args:
            to_email: Recipient email address
            user_name: User's name
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not EmailService.is_configured():
            print("⚠️  Email service not configured. Welcome email not sent.")
            return False
        
        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #1976d2;
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: #f9f9f9;
                        padding: 30px;
                        border-radius: 0 0 5px 5px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to CommunityOS.ai!</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user_name},</p>
                        
                        <p>Welcome to CommunityOS.ai! Your account has been successfully created.</p>
                        
                        <p>You can now log in and start managing your community.</p>
                        
                        <p>Best regards,<br>The CommunityOS.ai Team</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            params = {
                "from": settings.FROM_EMAIL,
                "to": [to_email],
                "subject": "Welcome to CommunityOS.ai",
                "html": html_content,
            }
            
            # Use requests directly to handle SSL verification in corporate environments
            headers = {
                "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                "Content-Type": "application/json"
            }
            
            verify_ssl = os.getenv("VERIFY_SSL", "false").lower() != "false"
            
            response = requests.post(
                "https://api.resend.com/emails",
                json=params,
                headers=headers,
                verify=verify_ssl
            )
            
            if response.status_code == 200:
                print(f"✓ Welcome email sent to {to_email}")
                return True
            else:
                print(f"✗ Failed to send email: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            print(f"✗ Failed to send welcome email: {str(e)}")
            return False
