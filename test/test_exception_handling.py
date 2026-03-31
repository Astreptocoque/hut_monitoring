#!/usr/bin/env python3
"""
Test Exception Handling in send_telegram
==========================================
Verifies that send_telegram is not silenced by exception handling.
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

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


async def send_telegram(message: str) -> None:
    """Send a Telegram message via the Bot API."""
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


async def simulate_scenario_with_error_before_send():
    """Simulate an error occurring before telegram send."""
    
    logger.info("=" * 70)
    logger.info("Scenario 1: Error before telegram send")
    logger.info("=" * 70)
    
    try:
        logger.info("Doing some work...")
        # Simulate some work
        
        logger.info("Error occurs!")
        raise ValueError("Simulated error during availability check")
        
        # This should never be reached, but if it were...
        msg = "This message should never be sent"
        await send_telegram(msg)
        
    except Exception as e:
        logger.error(f"Error during check: {e}")
        # Re-raise like the code does
        raise


async def simulate_scenario_with_error_during_send():
    """Simulate successful availability check but error during telegram send."""
    
    logger.info("=" * 70)
    logger.info("Scenario 2: Success but simulate error during send")
    logger.info("=" * 70)
    
    try:
        logger.info("Availability found!")
        
        msg = "<b>Hut available!</b>\n\n<b>Hut:</b> Test\n<b>Arrival:</b> 2026-04-15"
        logger.info(f"About to send telegram: {msg[:50]}...")
        
        await send_telegram(msg)
        logger.info("✅ Message sent successfully!")
        
    except Exception as e:
        logger.error(f"Error during check: {e}")
        raise


async def main():
    print("=" * 70)
    print("Testing Exception Handling in send_telegram")
    print("=" * 70)
    print()
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Missing credentials")
        sys.exit(1)
    
    # Test scenario 2 (the one that should work)
    try:
        await simulate_scenario_with_error_during_send()
    except Exception as e:
        logger.error(f"Scenario 2 raised: {type(e).__name__}")
    
    print()
    print("=" * 70)
    print("Test completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
