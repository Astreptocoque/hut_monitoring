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
import logging
from datetime import date, timedelta
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

# ── Load .env.local for local development (will not affect GitHub Actions) ────
_env_local = Path(__file__).parent.parent / ".env.local"
if _env_local.exists():
    load_dotenv(_env_local)

# ── Setup logging and screenshot directories ──────────────────────────────────
_log_dir = Path(__file__).parent.parent / "log"
_log_dir.mkdir(exist_ok=True)
_screenshots_dir = _log_dir / "screenshots"
_screenshots_dir.mkdir(exist_ok=True)

# Configure logging
_log_file = _log_dir / "hut_checker.log"
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(_log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# ── Credentials from environment variables (GitHub Secrets) ──────────────────
HUT_EMAIL          = os.environ["HUT_EMAIL"]
HUT_PASSWORD       = os.environ["HUT_PASSWORD"]
HUT_BASE_URL       = os.environ.get("HUT_URL", "https://www.hut-reservation.org")
# French home page — all navigation uses /fr/ to keep the UI in French
HUT_FR_HOME        = f"{HUT_BASE_URL}/fr/reservations"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"

# Detect if running in GitHub Actions (production)
IS_GITHUB_ACTIONS = os.environ.get("GITHUB_ACTIONS", "false").lower() == "true"

# Flag to enable/disable screenshots
# Defaults to False in GitHub Actions (production), True elsewhere
ENABLE_SCREENSHOTS = False
ENABLE_SCREENSHOTS = False if IS_GITHUB_ACTIONS else ENABLE_SCREENSHOTS

logger.info(f"Headless mode: {HEADLESS}")
logger.info(f"GitHub Actions (production): {IS_GITHUB_ACTIONS}")
logger.info(f"Screenshots enabled: {ENABLE_SCREENSHOTS}")
logger.info(f"Screenshots and logs will be saved to: {_log_dir.absolute()}")

# ── Load hut targets from YAML ────────────────────────────────────────────────
_config_path = Path(__file__).parent.parent / "config" / "huts.yaml"


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


async def _take_screenshot(page, step_name: str, context_info: str = "") -> None:
    """
    Take a screenshot with a descriptive filename.
    
    Only takes screenshots if ENABLE_SCREENSHOTS is True.
    Screenshots are disabled by default in GitHub Actions (production).
    
    Args:
        page: Playwright page object
        step_name: Name of the step/stage (e.g., "login", "hut_selection")
        context_info: Additional context (e.g., hut name, date) to include in filename
    """
    if not ENABLE_SCREENSHOTS:
        logger.debug(f"Screenshot skipped (disabled): {step_name}")
        return
    
    import time
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    safe_context = context_info.replace(" ", "_").replace("/", "_") if context_info else ""
    filename = f"{timestamp}_{step_name}"
    if safe_context:
        filename += f"_{safe_context}"
    filename += ".png"
    
    screenshot_path = _screenshots_dir / filename
    try:
        await page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"Screenshot saved: {screenshot_path.relative_to(_log_dir.parent)}")
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")

# ─────────────────────────────────────────────────────────────────────────────


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
    context_str = f"{target_hut}_{arrival_date}_{departure_date}"

    logger.info(
        f"Checking: {target_hut} | "
        f"{arrival_display} to {departure_display} | "
        f"min {min_spots} spot(s)"
    )

    try:
        # ── 1. Click "NOUVELLE RÉSERVATION" ───────────────────────────────────────
        logger.info(f"[1/4] Opening new reservation dialog for {target_hut}...")
        await _take_screenshot(page, "01_home", context_str)
        
        new_booking_btn = page.locator(
            "button.add_button span.mdc-button__label",
            has_text="NOUVELLE RÉSERVATION",
        )
        await new_booking_btn.wait_for(timeout=15_000)
        await new_booking_btn.click()
        await _take_screenshot(page, "02_new_reservation_clicked", context_str)

        # ── 2. Select hut in the autocomplete popup ────────────────────────────────
        logger.info(f"[2/4] Selecting hut: {target_hut}...")

        # Wait for the Angular Material dialog to be fully rendered.
        # The dialog host is <app-add-reservation-modal> inside .mat-mdc-dialog-surface.
        dialog = page.locator("app-add-reservation-modal")
        await dialog.wait_for(state="visible", timeout=10_000)
        logger.debug("Dialog element found and visible")
        await _take_screenshot(page, "02b_dialog_opened", context_str)

        # The autocomplete input has a stable id="hutInput" scoped inside the dialog.
        hut_input = dialog.locator("input#hutInput")
        await hut_input.wait_for(state="visible", timeout=10_000)
        logger.debug("Input field #hutInput found and visible")
        await _take_screenshot(page, "02c_input_field_visible", context_str)

        # Click first to ensure the field is focused (required for Angular CDK
        # autocomplete to start listening for input events).
        await hut_input.click()
        logger.debug("Input field clicked")
        await page.wait_for_timeout(300)
        await _take_screenshot(page, "02d_input_clicked", context_str)

        # Type the hut name character-by-character so Angular's reactive forms
        # and the autocomplete debounce fire correctly.
        logger.debug(f"Typing hut name: '{target_hut}'")
        await hut_input.type(target_hut, delay=50)
        await page.wait_for_timeout(1_500)  # wait for debounce + API call
        logger.debug("Typing completed, waiting for autocomplete panel")
        await _take_screenshot(page, "03_hut_input_filled", context_str)

        # The autocomplete options are rendered in the global cdk-overlay-container
        # (outside the dialog DOM), but Playwright's role-based locator still finds
        # them because it searches the full page.
        # We wait for the listbox to appear and contain at least one option.
        await page.wait_for_timeout(500)
        await _take_screenshot(page, "03a_before_autocomplete_search", context_str)
        
        autocomplete_panel = page.locator(
            ".mat-mdc-autocomplete-panel.mdc-menu-surface--open"
        )
        panel_count = await autocomplete_panel.count()
        logger.debug(f"Autocomplete panels found: {panel_count}")
        
        try:
            await autocomplete_panel.wait_for(state="attached", timeout=10_000)
            logger.debug("Autocomplete panel is attached")
        except PlaywrightTimeout:
            logger.warning("Autocomplete panel not found (attached). Taking screenshot for debugging...")
            await _take_screenshot(page, "03a_autocomplete_panel_missing", context_str)
            # Try alternative: check for any visible popup or dropdown
            all_panels = page.locator(".mdc-menu-surface--open")
            panel_alt_count = await all_panels.count()
            logger.debug(f"Alternative menu-surface panels found: {panel_alt_count}")
            raise
        
        await _take_screenshot(page, "03a_autocomplete_panel_attached", context_str)

        # Wait for an option whose full visible text matches the hut name.
        logger.debug(f"Looking for option with text: '{target_hut}'")
        hut_option = page.get_by_role("option", name=target_hut, exact=False)
        option_count = await hut_option.count()
        logger.debug(f"Options found with name '{target_hut}': {option_count}")
        
        try:
            await hut_option.first.wait_for(state="visible", timeout=10_000)
            logger.debug("First option is visible")
        except PlaywrightTimeout:
            logger.warning(f"No visible option found for '{target_hut}'. Taking screenshot...")
            await _take_screenshot(page, "03b_option_not_found", context_str)
            # Debug: list all available options
            all_options = page.get_by_role("option")
            all_opts_count = await all_options.count()
            logger.debug(f"Total options in page: {all_opts_count}")
            for i in range(min(5, all_opts_count)):
                try:
                    opt_text = await all_options.nth(i).inner_text()
                    logger.debug(f"  Option {i}: {opt_text}")
                except:
                    pass
            raise
        
        await _take_screenshot(page, "03b_autocomplete_options", context_str)
        await hut_option.first.click()
        logger.debug("Option clicked")
        await _take_screenshot(page, "04_hut_selected", context_str)

        # Click OK — scope the locator strictly inside the dialog to avoid
        # accidentally hitting other "OK" / "OK"-labelled buttons on the page.
        logger.debug("Looking for OK button inside dialog")
        ok_btn = dialog.locator("button span.mdc-button__label", has_text="OK").first
        await ok_btn.wait_for(state="visible", timeout=10_000)
        logger.debug("OK button found and visible")
        await _take_screenshot(page, "04b_ok_button_ready", context_str)
        await ok_btn.click()
        logger.debug("OK button clicked, waiting for network idle")
        await page.wait_for_load_state("networkidle")
        logger.info(f"[2/4] Hut selected successfully.")
        await _take_screenshot(page, "05_hut_confirmed", context_str)

        # ── 3. Fill the date range (arrival then departure) ────────────────────────
        logger.info(f"[3/4] Entering dates: {arrival_display} to {departure_display}...")

        # Arrival (start date)
        arrival_input = page.locator("input#cy-arrivalDate__input")
        await arrival_input.wait_for(timeout=10_000)
        await arrival_input.fill(arrival_display)
        await arrival_input.press("Tab")   # move focus to departure input
        await _take_screenshot(page, "06_arrival_date_entered", context_str)

        # Departure (end date) — identified by its data-test attribute
        departure_input = page.locator("input[data-test='input-departure-date-reservation']")
        await departure_input.wait_for(timeout=10_000)
        await departure_input.fill(departure_display)
        await departure_input.press("Tab")  # trigger Angular validation + availability fetch

        await page.wait_for_timeout(2_000)
        await page.wait_for_load_state("networkidle")
        logger.info(f"[3/4] Dates entered successfully.")
        await _take_screenshot(page, "07_dates_confirmed", context_str)

        # ── 4. Read the availability table ────────────────────────────────────────
        logger.info(f"[4/4] Reading availability table...")

        # The table is rendered as an Angular Material DataTable inside an
        # <app-availability-table> component with Shadow DOM.
        # Data rows have class "mat-mdc-row" and role="row" with aria-expanded="false"
        # (they are followed by expansion rows with class "expand_row").
        # We only want the data rows (not the expansion rows).
        
        # Wait for the availability table component to be visible
        await page.wait_for_selector("app-availability-table", timeout=10_000)
        logger.debug("Availability table component found")
        
        # The table is inside a <div class="dateTab"> within the shadow DOM
        # We need to target specifically the data rows which have the actual availability data
        # Pattern: <mat-row ... aria-label="..."> with date and places info
        
        # Using a more specific selector: data rows with aria-expanded attribute
        # (to exclude expansion rows which don't have this attribute)
        rows = page.locator("mat-row[aria-expanded]")
        row_count = await rows.count()
        logger.debug(f"Found {row_count} data rows in availability table")

        if row_count == 0:
            # Fallback: try to find rows using the table selector more broadly
            logger.warning("No rows with aria-expanded found, trying fallback selector...")
            rows = page.locator("table.mat-mdc-table tbody tr.mat-mdc-row[role='row']")
            row_count = await rows.count()
            logger.debug(f"Fallback search found {row_count} rows")

        if row_count == 0:
            logger.error("Could not locate any availability table rows")
            await _take_screenshot(page, "08_availability_table_debug", context_str)
            await page.wait_for_timeout(500)
            await _take_screenshot(page, "08a_availability_table_debug2", context_str)
            return

        availabilities = []  # List of free places for each day in order

        for i in range(row_count):
            row = rows.nth(i)
            
            try:
                # The row structure within the mat-row is:
                # <td class="...table_row_places..."> NUMBER <span>!</span></td>
                # We need to find the cell with class containing "table_row_places"
                places_cells = row.locator("td[class*='table_row_places']")
                places_count = await places_cells.count()
                
                if places_count == 0:
                    logger.debug(f"Row {i}: No places cell found, trying alternative selector...")
                    places_cells = row.locator("td.mat-mdc-cell")
                    # The places cell is typically the second td element
                    if await places_cells.count() >= 2:
                        places_cell = places_cells.nth(1)
                    else:
                        logger.warning(f"Row {i}: Could not find enough cells")
                        continue
                else:
                    places_cell = places_cells.first
                
                places_text = await places_cell.inner_text(timeout=2_000)
                logger.debug(f"Row {i}: Raw places text: '{places_text}'")
                
                # Extract the number (first token should be the number)
                # Clean whitespace and get the first part
                cleaned = places_text.strip()
                parts = cleaned.split()
                
                if parts:
                    # Try to parse the first part as integer
                    try:
                        free_places = int(parts[0])
                        availabilities.append(free_places)
                        logger.debug(f"  -> Extracted {free_places} free places")
                    except ValueError:
                        logger.warning(f"Row {i}: First part '{parts[0]}' is not a number")
                        continue
                else:
                    logger.warning(f"Row {i}: Could not extract any text from '{places_text}'")
                    continue
                    
            except (ValueError, IndexError) as e:
                logger.warning(f"Row {i}: Could not parse places text: {e}")
                continue
            except Exception as e:
                logger.warning(f"Row {i}: Error reading places: {e}")
                continue

        await _take_screenshot(page, "08_availability_table", context_str)

        if not availabilities:
            logger.warning(
                f"[4/4] Could not extract any availability data from the table."
            )
            await _take_screenshot(page, "09_no_availability_data", context_str)
            return

        logger.info(f"[4/4] Available places by day: {availabilities}")

        # Check if any day has enough spots
        best_day_idx = None
        best_availability = 0
        
        for idx, available in enumerate(availabilities):
            if available >= min_spots:
                best_day_idx = idx
                best_availability = available
                break

        if best_day_idx is None:
            logger.info(f"[4/4] No day has {min_spots}+ spot(s). Best available: {max(availabilities) if availabilities else 0} spot(s).")

            # send a message of failure only in case of dev environment            
            if not IS_GITHUB_ACTIONS:
                msg = (
                f"<b>Hut has no availability yet 🥺!</b>\n\n"
                f"<b>Hut:</b> {target_hut}\n"
                f"<b>Arrival:</b> {arrival_date}\n"
                f"<b>Departure:</b> {departure_date}\n"
                )
                logger.debug(f"Message preview:\n{msg}\n")
                await send_telegram(msg)
            return

        logger.info(f"[4/4] Day {best_day_idx} has {best_availability} free place(s) — meets threshold of {min_spots}!")
        await _take_screenshot(page, "10_availability_found", context_str)
        
        msg = (
            f"<b>Hut available!</b>\n\n"
            f"<b>Hut:</b> {target_hut}\n"
            f"<b>Arrival:</b> {arrival_date}\n"
            f"<b>Departure:</b> {departure_date}\n"
            f"<b>Free places (by day):</b> {availabilities}\n"
            f"<b>First available day:</b> Day {best_day_idx + 1} with {best_availability} spot(s)\n\n"
            f"<a href=\"{page.url}\">Book now</a>"
        )
        logger.debug(f"Message preview:\n{msg}\n")
        await send_telegram(msg)

    except PlaywrightTimeout as e:
        logger.error(f"Timeout error for {target_hut} / {arrival_date}: {e}")
        await _take_screenshot(page, "ERROR_timeout", context_str)
        raise
    except Exception as e:
        logger.error(f"Unexpected error for {target_hut} / {arrival_date}: {e}", exc_info=True)
        await _take_screenshot(page, "ERROR_unexpected", context_str)
        raise


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
            logger.info(f"Navigating to {HUT_BASE_URL}...")
            await page.goto(HUT_BASE_URL, wait_until="networkidle")
            await _take_screenshot(page, "00_landing_page")

            # Step 1 — choose "Continuer avec compte CAS"
            logger.info("Clicking CAS login button...")
            cas_btn = page.locator("button#sacButton")
            await cas_btn.wait_for(timeout=15_000)
            await cas_btn.click()
            await page.wait_for_load_state("networkidle")
            await _take_screenshot(page, "01_cas_login_page")

            # Step 2 — fill the SAC/CAS credentials
            logger.info("Filling credentials...")
            await page.fill("input#person_login_identity", HUT_EMAIL)
            await page.fill("input#person_password", HUT_PASSWORD)
            await page.click("button[type='submit']")
            await _take_screenshot(page, "02_credentials_submitted")

            # Wait for the OAuth redirect back to hut-reservation.org
            logger.info("Waiting for OAuth redirect...")
            await page.wait_for_url(
                lambda url: "hut-reservation.org" in url and "/fr/users/sign_in" not in url,
                timeout=20_000,
            )
            await page.wait_for_load_state("networkidle")
            logger.info("Logged in successfully.")
            await _take_screenshot(page, "03_logged_in")

            # The language is controlled by the browser context locale (fr-CH),
            # not by the URL path. The Angular app uses this locale setting
            # to determine which language to display.
            logger.info(f"Current URL: {page.url}")
            logger.debug(f"Language should be French based on browser context locale='fr-CH'")

            # ── Check each hut/date range ──────────────────────────────────────
            logger.info(f"Starting checks for {len(targets)} hut(s)...")
            for idx, target in enumerate(targets, 1):
                arrival   = str(target["date"])
                departure = _departure_for(arrival, target.get("departure_date"))
                logger.info(f"[{idx}/{len(targets)}] Processing {target['name']}...")
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
                    logger.error(f"Timeout for {target['name']} / {arrival}: {e}")
                    raise
                except Exception as e:
                    logger.error(f"Error for {target['name']} / {arrival}: {e}", exc_info=True)
                    raise
            
            logger.info("All checks completed successfully!")

        except Exception as e:
            logger.error(f"Fatal error during run: {e}", exc_info=True)
            await _take_screenshot(page, "FATAL_ERROR")
            raise
        finally:
            await browser.close()
            logger.info("Browser closed.")


if __name__ == "__main__":
    logger.info("=" * 80)
    logger.info("HUT MONITORING - Starting execution")
    logger.info("=" * 80)
    try:
        asyncio.run(run())
        logger.info("=" * 80)
        logger.info("HUT MONITORING - Execution completed successfully")
        logger.info("=" * 80)
    except Exception as e:
        logger.critical(f"HUT MONITORING - Execution failed: {e}", exc_info=True)
        logger.critical("=" * 80)
        sys.exit(1)