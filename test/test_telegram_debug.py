#!/usr/bin/env python3
"""
Telegram Bot Debug Test
=======================
Isolated test to debug Telegram bot message sending.
"""

import asyncio
import httpx
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
_env_local = Path(__file__).parent.parent / ".env.local"
if _env_local.exists():
    load_dotenv(_env_local)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


async def send_telegram_original(message: str) -> None:
    """Original implementation from check_hut.py"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10)
            resp.raise_for_status()
        print("✓ Telegram notification sent successfully.")
    except Exception as e:
        print(f"✗ Failed to send Telegram notification: {e}")


async def send_telegram_debug(message: str) -> None:
    """Debug version with detailed logging"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    
    print(f"📤 Sending to Telegram...")
    print(f"   URL: {url}")
    print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
    print(f"   Message: {message[:50]}...")
    
    try:
        async with httpx.AsyncClient() as client:
            print(f"   Making POST request...")
            resp = await client.post(url, json=payload, timeout=10)
            
            print(f"   Status Code: {resp.status_code}")
            print(f"   Response Text: {resp.text}")
            
            resp.raise_for_status()
            
            # Parse and validate response
            try:
                json_response = resp.json()
                print(f"   JSON Response: {json_response}")
                
                if json_response.get("ok"):
                    print("✓ Telegram notification sent successfully.")
                else:
                    error_code = json_response.get("error_code")
                    error_desc = json_response.get("description")
                    print(f"✗ Telegram API returned error: [{error_code}] {error_desc}")
            except ValueError:
                print(f"⚠ Response is not JSON: {resp.text}")
                
    except httpx.HTTPStatusError as e:
        print(f"✗ HTTP Error {e.response.status_code}: {e.response.text}")
    except asyncio.TimeoutError:
        print(f"✗ Timeout: Request took longer than 10 seconds")
    except Exception as e:
        print(f"✗ Unexpected error: {type(e).__name__}: {e}")


async def test_credentials():
    """Test that credentials are properly loaded"""
    print("=" * 60)
    print("Checking Credentials")
    print("=" * 60)
    
    if not TELEGRAM_BOT_TOKEN:
        print("✗ TELEGRAM_BOT_TOKEN not set")
        return False
    if not TELEGRAM_CHAT_ID:
        print("✗ TELEGRAM_CHAT_ID not set")
        return False
    
    print(f"✓ TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-5:]}")
    print(f"✓ TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
    return True


async def main():
    print("=" * 60)
    print("Telegram Bot Debug Test")
    print("=" * 60)
    print()
    
    # Check credentials
    if not await test_credentials():
        print("\n✗ Cannot proceed without credentials")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Testing Original Implementation")
    print("=" * 60)
    await send_telegram_original("🔧 Test message from original implementation")
    
    print()
    print("=" * 60)
    print("Testing Debug Implementation")
    print("=" * 60)
    await send_telegram_debug("🔍 Test message from debug implementation")


if __name__ == "__main__":
    asyncio.run(main())
