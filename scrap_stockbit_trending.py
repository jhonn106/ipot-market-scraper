from playwright.sync_api import sync_playwright
import os, requests

def scrape_trending():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto("https://stockbit.com/stream", timeout=30000)

        # Wait for the trending table
        rows = page.locator("table tbody tr").all_inner_texts()
        if not rows:
            return "⚠️ No trending data found."

        msg = "🔥 *Stockbit Trending*\n"
        for r in rows[:10]:
            msg += f"• `{r.strip()}`\n"
        return msg.strip()

def send_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat  = os.getenv("TELEGRAM_CHAT_ID")
    url   = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage"
    r = requests.post(url, json={"chat_id": chat, "text": text, "parse_mode": "Markdown"})
    print("✅ Sent" if r.ok else f"❌ {r.text}")

if __name__ == "__main__":
    trending = scrape_trending()
    send_telegram(trending)
