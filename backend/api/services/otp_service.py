"""
OTP (One-Time Password) service for passwordless login.
Generates, sends, and verifies OTP codes via email.
"""

import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from api.core.config import get_settings

settings = get_settings()


def generate_otp_code(length: int = 6) -> str:
    """Generate a random 6-digit OTP code."""
    return ''.join(random.choices(string.digits, k=length))


def get_otp_expiration() -> datetime:
    """Get OTP expiration time (10 minutes from now)."""
    return datetime.now(timezone.utc) + timedelta(minutes=10)


async def send_otp_email(email: str, otp_code: str, name: str = None) -> bool:
    """
    Send OTP to user's email using Gmail SMTP or log for development.
    Returns True if sent successfully, False otherwise.
    """
    try:
        # Email configuration
        sender_email = os.getenv("EMAIL_SENDER", "athena.ai.bot@gmail.com")
        sender_password = os.getenv("EMAIL_PASSWORD", "")  # Use app-specific password
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Create HTML email body
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-bottom: 20px;">🔐 Your Athena AI Login Code</h2>
                    
                    <p style="color: #666; margin-bottom: 20px;">
                        Hi {name or 'User'},
                    </p>
                    
                    <p style="color: #666; margin-bottom: 30px;">
                        Your one-time password (OTP) for login is:
                    </p>
                    
                    <div style="background-color: #f0f0f0; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #0066cc; letter-spacing: 5px; margin: 0;">{otp_code}</h1>
                    </div>
                    
                    <p style="color: #999; font-size: 12px; margin-bottom: 10px;">
                        ⏱️ This code will expire in 10 minutes.
                    </p>
                    
                    <p style="color: #999; font-size: 12px; margin-bottom: 20px;">
                        🔒 Never share this code with anyone.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    
                    <p style="color: #999; font-size: 11px; text-align: center;">
                        If you didn't request this code, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        # For development, log the OTP
        if settings.DEBUG or not sender_password:
            print(f"\n{'='*70}")
            print(f"📧 OTP EMAIL (DEV MODE)")
            print(f"{'='*70}")
            print(f"To: {email}")
            print(f"Name: {name or 'User'}")
            print(f"OTP Code: {otp_code}")
            print(f"Expires: 10 minutes")
            print(f"{'='*70}\n")
            return True
        
        # Production: Send via Gmail SMTP
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Your Athena AI Login Code: {otp_code}"
        msg["From"] = sender_email
        msg["To"] = email
        
        part1 = MIMEText(f"Your OTP code is: {otp_code}. Valid for 10 minutes.", "plain")
        part2 = MIMEText(html_content, "html")
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ OTP sent successfully to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send OTP email: {e}")
        # In development, still return True so user can see OTP in console
        if settings.DEBUG:
            return True
        return False


def verify_otp_code(stored_code: Optional[str], stored_expires: Optional[datetime], provided_code: str) -> Tuple[bool, str]:
    """
    Verify if the provided OTP code is correct.
    
    Returns:
        (is_valid, message)
    """
    if not stored_code:
        return False, "No OTP requested for this email"
    
    if not stored_expires:
        return False, "OTP expired"
    
    # Check if OTP has expired
    # Make both datetimes timezone-aware for comparison
    now = datetime.now(timezone.utc)
    expires = stored_expires
    
    # If stored_expires is naive, make it aware
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    
    if now > expires:
        return False, "OTP has expired. Please request a new one."
    
    # Check if code matches
    if provided_code != stored_code:
        return False, "Invalid OTP code"
    
    return True, "OTP verified successfully"


def clear_otp(user) -> None:
    """Clear OTP from user (after successful verification)."""
    user.otp_code = None
    user.otp_expires_at = None
