"""
OTP Service for MongoDB-based passwordless authentication
"""
import random
import string
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional
import os


def generate_otp_code(length: int = 6) -> str:
    """Generate a random 6-digit OTP code"""
    return ''.join(random.choices(string.digits, k=length))


def get_otp_expiration(minutes: int = 10) -> datetime:
    """Get OTP expiration time (default 10 minutes from now)"""
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


async def send_otp_email(email: str, otp_code: str, name: Optional[str] = None) -> bool:
    """
    Send OTP via email
    For development, prints to console with HTML preview
    For production, can use real email service (SMTP or API)
    """
    debug_mode = os.getenv("DEBUG_MODE", "true").lower() == "true"
    
    # Create HTML email content
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #0066cc; text-align: center;">🔐 Athena AI Login Code</h2>
                
                <p style="color: #666; font-size: 16px; margin: 20px 0;">
                    Hi {name or 'User'},
                </p>
                
                <p style="color: #666; margin: 20px 0;">
                    Your one-time password (OTP) for Athena AI is:
                </p>
                
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 10px; text-align: center; margin: 30px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    <h1 style="color: white; font-size: 48px; letter-spacing: 8px; margin: 0;">{otp_code}</h1>
                </div>
                
                <p style="color: #666; font-size: 14px; margin: 15px 0;">
                    ⏱️ <strong>Valid for 10 minutes only</strong>
                </p>
                
                <p style="color: #999; font-size: 12px; margin: 15px 0;">
                    🔒 Never share this code with anyone
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 25px 0;">
                
                <p style="color: #999; font-size: 11px; text-align: center;">
                    If you didn't request this code, you can safely ignore this email.
                </p>
                
                <p style="color: #999; font-size: 10px; text-align: center; margin-top: 20px;">
                    © 2024 Athena AI. All rights reserved.
                </p>
            </div>
        </body>
    </html>
    """
    
    if debug_mode:
        # Development mode: print to console
        print("\n" + "="*70)
        print("📧 OTP EMAIL SENT (DEBUG MODE)")
        print("="*70)
        print(f"To: {email}")
        print("From: Athena AI Support <noreply@athena.ai>")
        print("Subject: Your Athena AI Login Code")
        print(f"Name: {name or 'User'}")
        print(f"OTP Code: {otp_code}")
        print("Valid for: 10 minutes")
        print("="*70)
        print("[HTML Content Preview]")
        print(html_content)
        print("="*70 + "\n")
        return True
    
    # Production: Send via SMTP
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        sender_email = os.getenv("SMTP_EMAIL", "noreply@athena.ai")
        sender_password = os.getenv("SMTP_PASSWORD", "")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
        if not sender_password:
            print("[OTP] ⚠ SMTP_PASSWORD not set, using DEBUG mode")
            print("\n📧 [OTP EMAIL - DEBUG]")
            print(f"   To: {email}")
            print(f"   Code: {otp_code}\n")
            return True
        
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "Your Athena AI Login Code"
        message["From"] = sender_email
        message["To"] = email
        
        # Plain text version
        text_content = f"Your OTP code is: {otp_code}\nValid for 10 minutes.\n\nIf you didn't request this code, ignore this email."
        part1 = MIMEText(text_content, "plain")
        message.attach(part1)
        
        # HTML version
        part2 = MIMEText(html_content, "html")
        message.attach(part2)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        
        print(f"[OTP] ✓ Email sent successfully to {email}")
        return True
        
    except Exception as e:
        print(f"[OTP] ✗ Failed to send email: {e}")
        # In development, still return True
        if debug_mode:
            return True
        return False


def verify_otp_code(stored_code: Optional[str], stored_expires: Optional[datetime], provided_code: str) -> Tuple[bool, str]:
    """
    Verify OTP code against stored code and expiration
    Returns: (is_valid, message)
    """
    if not stored_code or not stored_expires:
        return False, "No OTP found. Request one first."
    
    # Ensure both datetimes are timezone-aware
    now = datetime.now(timezone.utc)
    expires = stored_expires
    
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    
    # Check expiration
    if now > expires:
        return False, "OTP expired. Please request a new one."
    
    # Check code
    if provided_code.strip() != stored_code.strip():
        return False, "Invalid OTP code. Please try again."
    
    return True, "OTP verified successfully"


def clear_otp(user_data: dict) -> dict:
    """Clear OTP fields from user document"""
    return {
        "otp_code": None,
        "otp_expires_at": None,
    }
