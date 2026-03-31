"""
Hut Reservation Availability Checker
=====================================
Logs into hut-reservation.org, navigates to a specific hut + date,
checks availability, and sends a Telegram notification if spots are found.

Configuration is done entirely via environment variables (see README.md).
"""

import os
import sys
import asyncio
import httpx
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ── Configuration from environment variables ──────────────────────────────────
HUT_EMAIL    = os.environ["HUT_EMAIL"]        # your login email
HUT_PASSWORD = os.environ["HUT_PASSWORD"]     # your login password
HUT_URL      = os.environ.get("HUT_URL", "https://www.hut-reservation.org")
TARGET_HUT   = os.environ["TARGET_HUT"]       # exact hut name as shown on site, e.g. "Cabane du Mont Blanc"
TARGET_DATE  = os.environ["TARGET_DATE"]      # format: YYYY-MM-DD, e.g. "2025-07-14"
MIN_SPOTS    = int(os.environ.get("MIN_SPOTS", "1"))  # minimum number of spots required

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"  # set to false for local debugging

# ─────────────────────────────────────────────────────────────────────────────


async def send_telegram(message: str) -> None:
    """Send a Telegram message via the Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    print("[Telegram] Notification sent.")


async def check_availability() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )
        page = await context.new_page()

        try:
            # ── 1. Login ───────────────────────────────────────────────────
            print(f"[1/4] Navigating to {HUT_URL}/login ...")
            await page.goto(f"{HUT_URL}/login", wait_until="networkidle")

            print("[1/4] Filling login form ...")
            # Adjust selectors below if the site changes its form field names
            await page.fill('input[type="email"], input[name="email"], input[placeholder*="mail" i]', HUT_EMAIL)
            await page.fill('input[type="password"], input[name="password"]', HUT_PASSWORD)
            await page.click('button[type="submit"], input[type="submit"]')

            # Wait for redirect away from /login
            await page.wait_for_url(lambda url: "/login" not in url, timeout=15_000)
            print("[1/4] Logged in successfully.")

            # ── 2. Search / navigate to hut ────────────────────────────────
            print(f"[2/4] Searching for hut: {TARGET_HUT} ...")
            await page.wait_for_load_state("networkidle")

            # Try a search box first (common pattern)
            search_box = page.locator(
                'input[placeholder*="search" i], input[placeholder*="hut" i], '
                'input[placeholder*="cabin" i], input[placeholder*="refuge" i], '
                'input[aria-label*="search" i]'
            ).first
            if await search_box.count() > 0:
                await search_box.fill(TARGET_HUT)
                await page.wait_for_timeout(1500)  # debounce

            # Click the hut result that matches our target name
            hut_link = page.get_by_text(TARGET_HUT, exact=False).first
            await hut_link.wait_for(timeout=10_000)
            await hut_link.click()
            await page.wait_for_load_state("networkidle")
            print("[2/4] Hut page loaded.")

            # ── 3. Select date ─────────────────────────────────────────────
            print(f"[3/4] Selecting date: {TARGET_DATE} ...")
            # Parse date parts for calendar interaction
            year, month, day = TARGET_DATE.split("-")
            date_display = f"{day}/{month}/{year}"  # localised display format

            # Try a date input field first
            date_input = page.locator('input[type="date"]').first
            if await date_input.count() > 0:
                await date_input.fill(TARGET_DATE)
            else:
                # Fall back: look for a text input and type the date
                date_text_input = page.locator(
                    'input[placeholder*="date" i], input[placeholder*="arrival" i], '
                    'input[placeholder*="check" i]'
                ).first
                if await date_text_input.count() > 0:
                    await date_text_input.fill(date_display)
                else:
                    # Last resort: click a calendar day cell
                    await page.get_by_role("gridcell", name=str(int(day))).click()

            await page.wait_for_timeout(2000)
            print("[3/4] Date selected.")

            # ── 4. Check availability ──────────────────────────────────────
            print("[4/4] Checking availability ...")
            await page.wait_for_load_state("networkidle")

            page_text = await page.inner_text("body")

            # Signals that the site shows when spots are available
            available_keywords = [
                "available", "disponible", "frei", "libero",
                "places", "beds", "betten", "lits",
                "book now", "réserver", "buchen",
            ]
            # Signals of unavailability
            unavailable_keywords = [
                "fully booked", "complet", "ausgebucht", "no availability",
                "not available", "sold out", "no places",
            ]

            page_lower = page_text.lower()
            is_unavailable = any(kw in page_lower for kw in unavailable_keywords)
            is_available   = any(kw in page_lower for kw in available_keywords)

            if is_unavailable:
                print(f"[4/4] ❌ No availability found for {TARGET_HUT} on {TARGET_DATE}.")
                return

            if is_available:
                msg = (
                    f"🏔️ <b>Hut available!</b>\n\n"
                    f"<b>Hut:</b> {TARGET_HUT}\n"
                    f"<b>Date:</b> {TARGET_DATE}\n\n"
                    f"👉 <a href=\"{page.url}\">Book now</a>"
                )
                print(f"[4/4] ✅ Availability found! Sending Telegram notification ...")
                await send_telegram(msg)
            else:
                print("[4/4] ⚠️  Could not determine availability from page text. Manual check recommended.")
                # Optionally take a screenshot for debugging:
                await page.screenshot(path="debug_screenshot.png")

        except PlaywrightTimeout as e:
            print(f"[ERROR] Timeout during check: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(check_availability())
