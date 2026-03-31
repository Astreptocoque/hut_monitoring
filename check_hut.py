"""
Hut Reservation Availability Checker
=====================================
Logs into hut-reservation.org, navigates to a specific hut + date range,
checks availability, and sends a Telegram notification if spots are found.

Credentials are supplied via environment variables (GitHub Secrets).
Hut targets (name, date, min_spots) live in config/huts.yaml.

Date handling
─────────────
The site's date picker is a range input (arrival → departure).
Each entry in huts.yaml supplies an `arrival_date` (YYYY-MM-DD).
The `departure_date` defaults to arrival + 1 night but can be overridden
with an explicit `departure_date` key in the YAML.

Language
────────
The site is navigated in French (/fr/ paths). After login the OAuth
callback may land on any locale; we immediately redirect to the French
home before proceeding.
"""

import os
import sys
import asyncio
import httpx
import yaml
from datetime import date, timedelta
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ── Credentials from environment variables (GitHub Secrets) ──────────────────
HUT_EMAIL          = os.environ["HUT_EMAIL"]
HUT_PASSWORD       = os.environ["HUT_PASSWORD"]
HUT_BASE_URL       = os.environ.get("HUT_URL", "https://www.hut-reservation.org")
# French home page — all navigation uses /fr/ to keep the UI in French
HUT_FR_HOME        = f"{HUT_BASE_URL}/fr/reservations"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"

# ── Load hut targets from YAML ────────────────────────────────────────────────
_config_path = Path(__file__).parent / "config" / "huts.yaml"


def load_hut_targets() -> list[dict]:
    with open(_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    targets = config.get("huts", [])
    if not targets:
        print("[Config] No huts defined in config/huts.yaml. Exiting.")
        sys.exit(0)
    return targets


def _departure_for(arrival_str: str, departure_str: str | None) -> str:
    """
    Return the departure date string (YYYY-MM-DD).
    If departure_str is supplied in the YAML, use it directly.
    Otherwise default to arrival + 1 night.
    """
    if departure_str:
        return str(departure_str)
    arr = date.fromisoformat(str(arrival_str))
    return (arr + timedelta(days=1)).isoformat()


def _to_display(iso_date: str) -> str:
    """Convert YYYY-MM-DD → DD.MM.YYYY (format expected by the Angular date input)."""
    year, month, day = iso_date.split("-")
    return f"{day}.{month}.{year}"

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


async def check_hut(
    page,
    target_hut: str,
    arrival_date: str,
    departure_date: str,
    min_spots: int,
) -> None:
    """
    Check availability for a single hut / date-range combination.
    The page is assumed to already be on the French home dashboard.
    """
    arrival_display   = _to_display(arrival_date)
    departure_display = _to_display(departure_date)

    print(
        f"\n─── Checking: {target_hut} | "
        f"{arrival_display} → {departure_display} | "
        f"min {min_spots} spot(s) ───"
    )

    # ── 1. Click "NOUVELLE RÉSERVATION" ───────────────────────────────────────
    print("[1/4] Opening new reservation dialog ...")
    new_booking_btn = page.locator(
        "button.add_button span.mdc-button__label",
        has_text="NOUVELLE RÉSERVATION",
    )
    await new_booking_btn.wait_for(timeout=15_000)
    await new_booking_btn.click()

    # ── 2. Select hut in the autocomplete popup ────────────────────────────────
    print(f"[2/4] Selecting hut: {target_hut} ...")
    hut_input = page.locator("input#hutInput")
    await hut_input.wait_for(timeout=10_000)
    await hut_input.fill(target_hut)
    await page.wait_for_timeout(1_500)  # debounce for autocomplete

    hut_option = page.get_by_role("option", name=target_hut)
    await hut_option.wait_for(timeout=10_000)
    await hut_option.click()

    ok_btn = page.locator("button span.mdc-button__label", has_text="OK")
    await ok_btn.wait_for(timeout=10_000)
    await ok_btn.click()
    await page.wait_for_load_state("networkidle")
    print("[2/4] Hut selected.")

    # ── 3. Fill the date range (arrival then departure) ────────────────────────
    print(f"[3/4] Entering dates: {arrival_display} → {departure_display} ...")

    # Arrival (start date)
    arrival_input = page.locator("input#cy-arrivalDate__input")
    await arrival_input.wait_for(timeout=10_000)
    await arrival_input.fill(arrival_display)
    await arrival_input.press("Tab")   # move focus to departure input

    # Departure (end date) — identified by its data-test attribute
    departure_input = page.locator("input[data-test='input-departure-date-reservation']")
    await departure_input.wait_for(timeout=10_000)
    await departure_input.fill(departure_display)
    await departure_input.press("Tab")  # trigger Angular validation + availability fetch

    await page.wait_for_timeout(2_000)
    await page.wait_for_load_state("networkidle")
    print("[3/4] Dates entered.")

    # ── 4. Read the availability table ────────────────────────────────────────
    print("[4/4] Reading availability table ...")

    # Each data row carries aria-label="<day name> <DD Month YYYY>. <N> places libres"
    # The second <span> inside td.table_row_date holds the DD.MM.YYYY text.
    rows = page.locator("mat-row[role='row'][aria-label]")
    row_count = await rows.count()

    free_places: int | None = None

    for i in range(row_count):
        row = rows.nth(i)
        date_cell = row.locator("td.table_row_date span").nth(1)  # "11.04.2026"
        try:
            cell_text = (await date_cell.inner_text(timeout=2_000)).strip()
        except PlaywrightTimeout:
            continue

        if cell_text == arrival_display:
            places_cell = row.locator("td.table_row_places")
            raw = (await places_cell.inner_text()).strip().split()[0]
            free_places = int(raw)
            break

    if free_places is None:
        print(
            f"[4/4] ⚠️  Arrival date {arrival_date} not found in the availability table. "
            "It may be outside the bookable window."
        )
        safe_name = target_hut.replace(" ", "_")
        await page.screenshot(path=f"debug_{safe_name}_{arrival_date}.png")
        return

    if free_places < min_spots:
        print(f"[4/4] ❌ Only {free_places} place(s) free — below threshold of {min_spots}.")
        return

    # ── Spots available — notify! ──────────────────────────────────────────────
    print(f"[4/4] ✅ {free_places} place(s) free. Sending notification ...")
    msg = (
        f"🏔️ <b>Hut available!</b>\n\n"
        f"<b>Hut:</b> {target_hut}\n"
        f"<b>Arrival:</b> {arrival_date}\n"
        f"<b>Departure:</b> {departure_date}\n"
        f"<b>Free places:</b> {free_places}\n\n"
        f"👉 <a href=\"{page.url}\">Book now</a>"
    )
    await send_telegram(msg)


async def run() -> None:
    targets = load_hut_targets()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            locale="fr-CH",   # keeps Angular i18n in French from the start
        )
        page = await context.new_page()

        try:
            # ── Login flow ─────────────────────────────────────────────────────
            # Navigate directly to the French login entry point so the site
            # renders in French regardless of browser/OS locale detection.
            print(f"[Login] Navigating to {HUT_BASE_URL} ...")
            await page.goto(HUT_BASE_URL, wait_until="networkidle")

            # Step 1 — choose "Continuer avec compte CAS"
            cas_btn = page.locator("button#sacButton")
            await cas_btn.wait_for(timeout=15_000)
            await cas_btn.click()
            await page.wait_for_load_state("networkidle")

            # Step 2 — fill the SAC/CAS credentials
            print("[Login] Filling credentials ...")
            await page.fill("input#person_login_identity", HUT_EMAIL)
            await page.fill("input#person_password", HUT_PASSWORD)
            await page.click("button[type='submit']")

            # Wait for the OAuth redirect back to hut-reservation.org
            await page.wait_for_url(
                lambda url: "hut-reservation.org" in url and "/fr/users/sign_in" not in url,
                timeout=20_000,
            )
            await page.wait_for_load_state("networkidle")
            print("[Login] Logged in successfully.")

            # Force navigation to the French home so the UI is in French,
            # regardless of which locale the OAuth callback landed on.
            if "/fr/" not in page.url:
                print(f"[Login] Redirecting to French home: {HUT_FR_HOME}")
                await page.goto(HUT_FR_HOME, wait_until="networkidle")

            # ── Check each hut/date range ──────────────────────────────────────
            for target in targets:
                arrival   = str(target["date"])
                departure = _departure_for(arrival, target.get("departure_date"))
                try:
                    await check_hut(
                        page=page,
                        target_hut=str(target["name"]),
                        arrival_date=arrival,
                        departure_date=departure,
                        min_spots=int(target.get("min_spots", 1)),
                    )
                    # Return to French home for the next iteration
                    await page.goto(HUT_FR_HOME, wait_until="networkidle")
                except PlaywrightTimeout as e:
                    print(f"[ERROR] Timeout for {target['name']} / {arrival}: {e}")
                except Exception as e:
                    print(f"[ERROR] Unexpected error for {target['name']} / {arrival}: {e}")
                    raise

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(run())