import os
import requests
from playwright.sync_api import sync_playwright, TimeoutError

# ------------- helpers -------------
def login_stockbit(page):
    """Login via email/password to Stockbit."""
    login_url = "https://stockbit.com/login"
    page.goto(login_url, timeout=30000)

    # wait and fill form
    page.fill('input[name="username"]', os.getenv("STOCKBIT_EMAIL"))
    page.fill('input[name="password"]', os.getenv("STOCKBIT_PASSWORD"))
    page.click('button[type="submit"]')

    # verify we are logged-in (wait for dashboard/stream)
    try:
        page.wait_for_url("**/stream", timeout=30000)
    except TimeoutError:
        raise RuntimeError("❌ Login failed – check credentials or 2FA.")

def grab_trending(page):
    """Return Markdown-formatted list of trending stocks."""
    page.goto("https://stockbit.com/stream", timeout=30000)

    # wait until the trending table is rendered
    loc = page.locator("table tbody tr")
    loc.first.wait_for(state="visible", timeout=15000)

    rows = loc.all_inner_texts()
    lines = [r.strip() for r in rows if r.strip()]
    if not lines:
        return "⚠️ No trending data found."

    msg = "🔥 *Stockbit Trending Stocks*\n"
    for line in lines[:10]:            # max 10 rows
        msg += f"• `{line}`\n"
    return msg.strip()

def send_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat  = os.getenv("TELEGRAM_CHAT_ID")
    url   = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage"
    r = requests.post(url, json={"chat_id": chat, "text": text, "parse_mode": "Markdown"})
    print("✅ Sent" if r.ok else f"❌ {r.text}")

# ------------- main -------------
if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()

        login_stockbit(page)
        trending = grab_trending(page)
        print("DEBUG:", trending)
        send_telegram(trending)

        browser.close()
