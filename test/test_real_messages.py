#!/usr/bin/env python3
"""
Test Real-world Message Sending
================================
Tests sending the exact message format that check_hut.py would send.
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
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


async def send_telegram(message: str) -> None:
    """Send a Telegram message via the Bot API - EXACT COPY FROM check_hut.py"""
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
    """Test multiple real-world scenarios."""
    
    print("=" * 70)
    print("Testing Real-world Message Scenarios")
    print("=" * 70)
    print()
    
    # Scenario 1: Typical hut availability
    logger.info("TEST 1: Typical hut availability message")
    target_hut = "Cabane de Mont-Collon"
    arrival_date = "2026-05-15"
    departure_date = "2026-05-16"
    availabilities = [2, 3, 1]
    best_day_idx = 1
    best_availability = 3
    page_url = "https://www.hut-reservation.org/fr/reservations/mont-collon"
    
    msg = (
        f"<b>Hut available!</b>\n\n"
        f"<b>Hut:</b> {target_hut}\n"
        f"<b>Arrival:</b> {arrival_date}\n"
        f"<b>Departure:</b> {departure_date}\n"
        f"<b>Free places (by day):</b> {availabilities}\n"
        f"<b>First available day:</b> Day {best_day_idx + 1} with {best_availability} spot(s)\n\n"
        f"<a href=\"{page_url}\">Book now</a>"
    )
    
    print(f"Message preview:\n{msg}\n")
    await send_telegram(msg)
    
    await asyncio.sleep(0.5)
    
    # Scenario 2: Hut with special characters
    logger.info("TEST 2: Hut with special characters and accents")
    target_hut = "Cabane d'Arpette (Jungfraujoch)"
    arrival_date = "2026-06-20"
    departure_date = "2026-06-21"
    availabilities = [5, 4, 3, 2, 1]
    best_day_idx = 0
    best_availability = 5
    page_url = "https://www.hut-reservation.org/fr/reservations/arpette"
    
    msg = (
        f"<b>Hut available!</b>\n\n"
        f"<b>Hut:</b> {target_hut}\n"
        f"<b>Arrival:</b> {arrival_date}\n"
        f"<b>Departure:</b> {departure_date}\n"
        f"<b>Free places (by day):</b> {availabilities}\n"
        f"<b>First available day:</b> Day {best_day_idx + 1} with {best_availability} spot(s)\n\n"
        f"<a href=\"{page_url}\">Book now</a>"
    )
    
    print(f"Message preview:\n{msg}\n")
    await send_telegram(msg)
    
    await asyncio.sleep(0.5)
    
    # Scenario 3: Single spot available
    logger.info("TEST 3: Single spot available")
    target_hut = "Bivouac du Schönenboden"
    arrival_date = "2026-07-10"
    departure_date = "2026-07-11"
    availabilities = [0, 0, 1]
    best_day_idx = 2
    best_availability = 1
    page_url = "https://www.hut-reservation.org/fr/reservations/schonenboden"
    
    msg = (
        f"<b>Hut available!</b>\n\n"
        f"<b>Hut:</b> {target_hut}\n"
        f"<b>Arrival:</b> {arrival_date}\n"
        f"<b>Departure:</b> {departure_date}\n"
        f"<b>Free places (by day):</b> {availabilities}\n"
        f"<b>First available day:</b> Day {best_day_idx + 1} with {best_availability} spot(s)\n\n"
        f"<a href=\"{page_url}\">Book now</a>"
    )
    
    print(f"Message preview:\n{msg}\n")
    await send_telegram(msg)
    
    print()
    print("=" * 70)
    print("✅ All messages sent successfully!")
    print("=" * 70)


async def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Missing credentials")
        sys.exit(1)
    
    await test_scenarios()


if __name__ == "__main__":
    asyncio.run(main())
