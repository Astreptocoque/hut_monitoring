# 🏔️ Hut Availability Checker

Automatically checks [hut-reservation.org](https://www.hut-reservation.org) for available spots
at a specific mountain hut on a specific date, and notifies you via **Telegram** the moment something opens up.

Runs for **free** on **GitHub Actions** — no server, no Raspberry Pi needed.

---

## How it works

```
GitHub Actions (cron every 30 min)
    └── Launches a headless Chromium browser
        └── Logs in with your credentials
            └── Navigates to your target hut + date
                └── Detects availability
                    └── Sends you a Telegram message 🎉
```

---

## Setup (one-time, ~20 minutes)

### Step 1 — Create a Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts (pick any name/username)
3. BotFather will give you a **token** like `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxx` — save it

4. Now get your **Chat ID**:
   - Search for **@userinfobot** in Telegram
   - Send it any message
   - It will reply with your Chat ID (a number like `123456789`) — save it

---

### Step 2 — Create a GitHub repository

1. Go to [github.com](https://github.com) and create a **free account** if you don't have one
2. Click **New repository**, name it `hut-checker`, set it to **Private**, click **Create**
3. Upload the three files from this folder:
   - `check_hut.py`
   - `requirements.txt`
   - `.github/workflows/check_hut.yml` ← make sure to keep the folder structure

   The easiest way is to use the GitHub web interface:
   - Click **Add file → Upload files** for `check_hut.py` and `requirements.txt`
   - For the workflow, click **Add file → Create new file**, type `.github/workflows/check_hut.yml` as the filename, and paste its content

---

### Step 3 — Add your secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions → New repository secret**

Add each of these secrets:

| Secret name          | Value / example                              |
|----------------------|----------------------------------------------|
| `HUT_EMAIL`          | `you@example.com`                            |
| `HUT_PASSWORD`       | `yourpassword`                               |
| `TARGET_HUT`         | `Cabane du Mont Blanc` (exact name on site)  |
| `TARGET_DATE`        | `2025-07-14`                                 |
| `MIN_SPOTS`          | `1`                                          |
| `TELEGRAM_BOT_TOKEN` | `7123456789:AAFxxxxxxxxxxxxxxxxxxxxxx`        |
| `TELEGRAM_CHAT_ID`   | `123456789`                                  |

---

### Step 4 — Enable Actions and do a manual test run

1. Go to the **Actions** tab in your repository
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. Click on **"Hut Availability Checker"** in the left sidebar
4. Click **"Run workflow"** → **"Run workflow"** (green button)
5. Watch the run — it should complete in ~2 minutes
6. If it fails, click the failed job → download the **debug-screenshot** artifact to see what the browser saw

---

## Customisation

### Change the check frequency

Edit `.github/workflows/check_hut.yml`, line:
```yaml
- cron: "*/30 * * * *"
```

| Cron expression      | Meaning                            |
|----------------------|------------------------------------|
| `*/15 * * * *`       | Every 15 minutes                   |
| `*/30 * * * *`       | Every 30 minutes (default)         |
| `0 * * * *`          | Every hour                         |
| `0 6,12,18 * * *`    | At 6am, noon, and 6pm UTC          |

> ⚠️ GitHub Actions has a minimum interval of ~5 minutes in practice, and may delay jobs by a few minutes under load. For a booking checker this is perfectly fine.

### Check multiple huts or dates

Duplicate the secret + workflow pattern, or modify `check_hut.py` to loop over a list of huts/dates stored in a JSON config file.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Login fails | Check `HUT_EMAIL` / `HUT_PASSWORD` secrets for typos |
| Hut not found | Make sure `TARGET_HUT` exactly matches the name on the website |
| No notification received | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`; make sure you started a conversation with your bot |
| Workflow not running | Check **Actions** tab is enabled; GitHub may pause scheduled workflows on inactive repos after 60 days — just re-enable manually |
| Debug screenshot | Downloaded from the failed run's **Artifacts** section |

---

## Security notes

- Your credentials are stored as **GitHub Encrypted Secrets** — they are never visible in logs or to other users
- The repository is **private** — only you can see the code and run history
- The script does **not** automatically complete a booking — it only notifies you, so you confirm the booking yourself
