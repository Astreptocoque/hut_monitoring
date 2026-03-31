#!/usr/bin/env python3
"""
Telegram Bot Diagnostic Tool
============================
Comprehensive debugging to identify Telegram bot issues.
"""

import asyncio
import httpx
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
_env_local = Path(__file__).parent.parent / ".env.local"
if _env_local.exists():
    load_dotenv(_env_local)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


async def get_bot_info() -> dict:
    """Get information about the bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    
    print("\n📋 Getting bot info...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"✓ Bot is configured correctly")
                print(f"   Bot ID: {bot_info.get('id')}")
                print(f"   Bot username: @{bot_info.get('username')}")
                print(f"   Bot name: {bot_info.get('first_name')}")
                return bot_info
            else:
                print(f"✗ Invalid bot token: {data.get('description')}")
                return None
    except Exception as e:
        print(f"✗ Failed to get bot info: {e}")
        return None


async def test_chat_id_formats() -> None:
    """Test different chat ID formats"""
    chat_id = TELEGRAM_CHAT_ID
    
    print("\n🔍 Testing chat ID formats...")
    print(f"   Original: {chat_id}")
    print(f"   Type: {type(chat_id)}")
    
    # Test with different formats
    test_ids = [
        chat_id,  # Original
        str(chat_id),  # As string
        int(chat_id),  # As int
        f"-{chat_id}",  # Negative (for groups)
        f"-100{chat_id}",  # Group format with 100 prefix
    ]
    
    url_base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for test_id in test_ids:
        try:
            payload = {
                "chat_id": test_id,
                "text": "🔧 Test message",
                "parse_mode": "HTML",
            }
            
            async with httpx.AsyncClient() as client:
                resp = await client.post(url_base, json=payload, timeout=5)
                data = resp.json()
                
                if data.get("ok"):
                    print(f"   ✓ Chat ID {test_id} works!")
                else:
                    error_desc = data.get("description", "Unknown error")
                    print(f"   ✗ Chat ID {test_id}: {error_desc}")
                    
        except Exception as e:
            print(f"   ✗ Chat ID {test_id}: {type(e).__name__}")


async def get_updates() -> None:
    """Get recent updates to identify the correct chat ID"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    
    print("\n📬 Getting recent updates (to find correct chat ID)...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("ok"):
                updates = data.get("result", [])
                
                if not updates:
                    print("   ℹ No recent updates found")
                    print("   💡 Try sending a message to the bot in Telegram first!")
                    return
                
                print(f"   ✓ Found {len(updates)} recent updates:")
                
                for update in updates[-5:]:  # Last 5 updates
                    update_id = update.get("update_id")
                    
                    # Check for message
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg.get("chat", {}).get("id")
                        chat_type = msg.get("chat", {}).get("type")
                        text = msg.get("text", "[no text]")[:50]
                        
                        print(f"   - Update {update_id}:")
                        print(f"     Chat ID: {chat_id}")
                        print(f"     Chat type: {chat_type}")
                        print(f"     Text: {text}")
                    
                    # Check for callback query
                    elif "callback_query" in update:
                        cbq = update["callback_query"]
                        chat_id = cbq.get("from", {}).get("id")
                        print(f"   - Update {update_id}: Callback query from user {chat_id}")
                    
                    # Check for channel post
                    elif "channel_post" in update:
                        post = update["channel_post"]
                        chat_id = post.get("chat", {}).get("id")
                        print(f"   - Update {update_id}: Channel post in {chat_id}")
            else:
                print(f"✗ Failed to get updates: {data.get('description')}")
                
    except Exception as e:
        print(f"✗ Failed to get updates: {e}")


async def validate_current_setup() -> None:
    """Validate the current setup"""
    print("\n✔️ Validating current setup...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": "🔧 Test message to validate setup",
        "parse_mode": "HTML",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10)
            data = resp.json()
            
            if data.get("ok"):
                print(f"✓ Setup is valid! Message sent successfully.")
                return True
            else:
                print(f"✗ Setup is invalid:")
                print(f"   Error code: {data.get('error_code')}")
                print(f"   Description: {data.get('description')}")
                return False
                
    except Exception as e:
        print(f"✗ Setup validation failed: {e}")
        return False


async def main():
    print("=" * 70)
    print("Telegram Bot Diagnostic Tool")
    print("=" * 70)
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("✗ Missing credentials")
        sys.exit(1)
    
    print(f"\n🔐 Bot token: {TELEGRAM_BOT_TOKEN[:10]}...{TELEGRAM_BOT_TOKEN[-5:]}")
    print(f"💬 Chat ID: {TELEGRAM_CHAT_ID}")
    
    # Run diagnostics
    await get_bot_info()
    await validate_current_setup()
    await test_chat_id_formats()
    await get_updates()
    
    print("\n" + "=" * 70)
    print("Diagnosis Complete")
    print("=" * 70)
    print("\n💡 Next steps:")
    print("   1. If bot info is ✗ - check your TELEGRAM_BOT_TOKEN")
    print("   2. If chat ID test is ✗ - check your TELEGRAM_CHAT_ID")
    print("   3. If 'chat not found' - the bot may not be in that chat")
    print("      - Add the bot to your chat and try again")
    print("      - See the 'Getting recent updates' section for the correct chat ID")


if __name__ == "__main__":
    asyncio.run(main())
