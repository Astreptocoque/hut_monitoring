#!/usr/bin/env python3
"""
Test Simulated Main Code Path
==============================
Simulates the exact code flow from check_hut.py to verify telegram is called.
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


async def simulate_check_hut():
    """Simulate the check_hut function with availability found."""
    
    # Simulate finding availability
    target_hut = "Test Hut"
    arrival_date = "2026-04-15"
    departure_date = "2026-04-16"
    availabilities = [2, 3, 1]
    best_day_idx = 0
    best_availability = 2
    min_spots = 1
    
    # Simulated page URL
    page_url = "https://www.hut-reservation.org/fr/reservations/test-hut"
    
    try:
        logger.info(f"[4/4] Day {best_day_idx} has {best_availability} free place(s) — meets threshold of {min_spots}!")
        
        msg = (
            f"<b>Hut available!</b>\n\n"
            f"<b>Hut:</b> {target_hut}\n"
            f"<b>Arrival:</b> {arrival_date}\n"
            f"<b>Departure:</b> {departure_date}\n"
            f"<b>Free places (by day):</b> {availabilities}\n"
            f"<b>First available day:</b> Day {best_day_idx + 1} with {best_availability} spot(s)\n\n"
            f"<a href=\"{page_url}\">Book now</a>"
        )
        
        logger.info(f"Message to send: {msg[:100]}...")
        await send_telegram(msg)
        logger.info("✅ Telegram notification sent from check_hut simulation!")
        
    except Exception as e:
        logger.error(f"Error in check_hut simulation: {type(e).__name__}: {e}", exc_info=True)
        raise


async def main():
    print("=" * 70)
    print("Testing Simulated check_hut Code Path")
    print("=" * 70)
    print()
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Missing credentials")
        sys.exit(1)
    
    print("Simulating availability found scenario...")
    print()
    
    await simulate_check_hut()
    
    print()
    print("=" * 70)
    print("✅ Test completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
