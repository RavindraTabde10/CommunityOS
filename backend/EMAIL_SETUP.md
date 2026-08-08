# Email Service Setup Guide

## Overview

The password reset feature now sends emails via **Resend** API. Follow these steps to configure email sending.

---

## Quick Setup

### Step 1: Get Resend API Key

1. Go to [Resend.com](https://resend.com)
2. Sign up for a free account (100 emails/day free)
3. Go to **API Keys** section
4. Create a new API key
5. Copy the API key (starts with `re_`)

### Step 2: Configure Domain (Optional but Recommended)

**For Production:**
1. In Resend dashboard, go to **Domains**
2. Add your domain (e.g., `communityos.ai`)
3. Add DNS records as shown
4. Verify domain

**For Testing:**
- You can use Resend's test domain (`onboarding@resend.dev`)
- Or use your verified domain

### Step 3: Update `.env` File

Add these lines to your `backend/.env`:

```env
# Email Configuration
RESEND_API_KEY=re_your_actual_api_key_here
FROM_EMAIL=noreply@yourdomain.com
```

**Example:**
```env
RESEND_API_KEY=re_AbCdEf123456_your_actual_key
FROM_EMAIL=noreply@communityos.ai
```

**For Testing (using Resend's test domain):**
```env
RESEND_API_KEY=re_AbCdEf123456_your_actual_key
FROM_EMAIL=onboarding@resend.dev
```

### Step 4: Restart Backend Server

```bash
# Stop the current server (Ctrl+C)
# Restart it
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Testing

### Test Password Reset

1. Go to frontend forgot password page
2. Enter a valid email: `ravindra.tabde10@gmail.com`
3. Click "Send Reset Link"
4. Check the email inbox

**Expected Email:**
- Subject: "Reset Your Password - CommunityOS.ai"
- Contains reset link with token
- Link expires in 1 hour

### Test Without Email Configuration

If `RESEND_API_KEY` is not configured:
- Backend will print warning: `⚠️ Email service not configured`
- Response will include `reset_token` for manual testing
- Use the token to test password reset functionality

---

## Email Templates

### Password Reset Email

Features:
- ✅ Professional HTML design
- ✅ Clickable reset button
- ✅ Plain text alternative
- ✅ 1-hour expiration notice
- ✅ Security notice

Preview:
```
🔐 Password Reset Request

Hi [Name],

We received a request to reset your password...

[Reset Password Button]

This link will expire in 1 hour.
```

### Welcome Email (Future)

Sent when new users register:
```
🎉 Welcome to CommunityOS.ai!

Hi [Name],

Welcome to CommunityOS.ai! Your account has been created...
```

---

## Troubleshooting

### Email Not Received

**Check 1: API Key Configured**
```bash
# In backend folder
.venv\Scripts\python.exe -c "from app.core.config import Settings; s = Settings(); print(f'API Key: {s.RESEND_API_KEY[:10]}...' if s.RESEND_API_KEY else 'Not configured')"
```

**Check 2: FROM_EMAIL Set**
```bash
.venv\Scripts\python.exe -c "from app.core.config import Settings; s = Settings(); print(f'From: {s.FROM_EMAIL}')"
```

**Check 3: User Exists**
```bash
.venv\Scripts\python.exe check_user.py user@example.com
```

**Check 4: Backend Logs**
Look for:
- ✓ `Password reset email sent to user@example.com`
- ✗ `Failed to send password reset email: [error]`
- ⚠️ `Email service not configured`

**Check 5: Spam Folder**
Check recipient's spam/junk folder

### Common Errors

**Error: `Authentication required`**
- API key is invalid or not set
- Solution: Check `RESEND_API_KEY` in `.env`

**Error: `Invalid from address`**
- `FROM_EMAIL` domain not verified
- Solution: Verify domain in Resend or use `onboarding@resend.dev`

**Error: `Rate limit exceeded`**
- Free tier limit reached (100/day)
- Solution: Upgrade plan or wait 24 hours

---

## Security Notes

### Email Enumeration Prevention

The endpoint **always returns success**, even if:
- ❌ Email doesn't exist
- ❌ Email service fails
- ✅ Email sent successfully

**Why?** To prevent attackers from discovering registered emails.

**User Experience:**
```
"If the email is registered, a password reset link has been sent to your inbox"
```

### Token Security

- ✅ Tokens expire in 1 hour
- ✅ One-time use (deleted after use)
- ✅ JWT-signed with secret key
- ✅ Contains user ID + type flag

---

## API Response Examples

### When Email Service Configured

```json
{
  "message": "If the email is registered, a password reset link has been sent to your inbox"
}
```

### When Email Service NOT Configured (Development)

```json
{
  "message": "If the email is registered, a password reset link has been sent to your inbox",
  "reset_token": "eyJhbGc...",
  "note": "Email service not configured. Use the token above for testing."
}
```

---

## Cost & Limits

### Resend Free Tier
- ✅ 100 emails/day
- ✅ 3,000 emails/month
- ✅ API access
- ✅ Email logs

### Paid Plans
- Pro: $20/month (50,000 emails)
- Enterprise: Custom pricing

---

## Next Steps

1. ✅ Configure Resend API key
2. ✅ Test password reset
3. 🔄 Add welcome emails on registration
4. 🔄 Add notification emails for issues
5. 🔄 Add weekly report emails

---

## Support

**Resend Documentation:**
- [Getting Started](https://resend.com/docs/send-with-python)
- [API Reference](https://resend.com/docs/api-reference/emails/send-email)

**Project Issues:**
Contact the development team
