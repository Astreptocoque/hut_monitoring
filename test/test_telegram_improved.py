#!/usr/bin/env python3
"""
Test Fixed Telegram Implementation
==================================
Validates the improved send_telegram function.
"""

import asyncio
import httpx
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
_env_local = Path(__file__).parent.parent / ".env.local"
if _env_local.exists():
    load_dotenv(_env_local)

# Setup logging (same as main script)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


async def send_telegram_improved(message: str) -> None:
    """Improved implementation with better error handling."""
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
            
            # Validate Telegram API response
            try:
                json_response = resp.json()
                if not json_response.get("ok"):
                    error_code = json_response.get("error_code")
                    error_desc = json_response.get("description", "Unknown error")
                    logger.error(f"Telegram API error [{error_code}]: {error_desc}")
                    return
            except ValueError:
                # Response is not JSON, but HTTP status was OK
                logger.warning(f"Telegram response is not JSON: {resp.text}")
                return
            
        logger.info("Telegram notification sent successfully.")
    except asyncio.TimeoutError:
        logger.error("Timeout sending Telegram notification (request exceeded 10 seconds)")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error sending Telegram notification: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {type(e).__name__}: {e}")


async def test_scenarios():
    """Test various scenarios"""
    print("=" * 70)
    print("Testing Improved Telegram Implementation")
    print("=" * 70)
    
    # Test 1: Normal message
    print("\n📤 Test 1: Normal message")
    print("-" * 70)
    await send_telegram_improved("✅ Test 1: Normal message from improved implementation")
    
    # Test 2: HTML formatted message
    print("\n📤 Test 2: HTML formatted message")
    print("-" * 70)
    await send_telegram_improved("✅ <b>Bold</b> <i>Italic</i> <code>Code</code>")
    
    # Test 3: Long message
    print("\n📤 Test 3: Long message")
    print("-" * 70)
    long_msg = "✅ This is a long message. " * 20
    await send_telegram_improved(long_msg)
    
    # Test 4: Message with special characters
    print("\n📤 Test 4: Special characters")
    print("-" * 70)
    await send_telegram_improved("✅ Special chars: émojis 🎉 symbols @#$% quotes \"test\"")
    
    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Missing credentials")
        sys.exit(1)
    
    asyncio.run(test_scenarios())
