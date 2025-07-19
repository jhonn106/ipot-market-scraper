from playwright.sync_api import sync_playwright
import os
import requests
from dotenv import load_dotenv

load_dotenv()

STOCKBIT_USERNAME = os.getenv("STOCKBIT_USERNAME")
STOCKBIT_PASSWORD = os.getenv("STOCKBIT_PASSWORD")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def scrape_trending_stockbit():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("🔐 Login ke Stockbit...")
        page.goto("https://stockbit.com/login", timeout=60000)

        page.fill("input[name='username']", STOCKBIT_USERNAME)
        page.fill("input[name='password']", STOCKBIT_PASSWORD)
        page.click("button[type='submit']")

        # Tunggu redirect ke halaman stream
        try:
            page.wait_for_url("**/stream", timeout=15000)
        except:
            page.goto("https://stockbit.com/stream")

        print("📥 Mengambil data trending...")
        page.wait_for_selector("div[class*=Trending]", timeout=20000)

        # Temukan elemen Trending
        trending_section = page.locator("div:has-text('Trending')").nth(0).locator("xpath=..")
        trending_items = trending_section.locator("a[class*=stock-link]").all_inner_texts()

        browser.close()

        if not trending_items:
            return "⚠️ Tidak ada data trending ditemukan"

        result = "**🔥 Trending Stock (Stockbit)**\n"
        for i, item in enumerate(trending_items[:10], 1):  # maksimal 10
            result += f"{i}. {item.strip()}\n"

        return result.strip()

def send_to_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram token atau chat_id belum diset.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    try:
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("✅ Data trending dikirim ke Telegram.")
        else:
            print(f"❌ Gagal kirim ke Telegram: {res.text}")
    except Exception as e:
        print(f"❌ Error Telegram: {e}")

if __name__ == "__main__":
    trending = scrape_trending_stockbit()
    print(trending)
    if "Trending Stock" in trending:
        send_to_telegram(trending)
