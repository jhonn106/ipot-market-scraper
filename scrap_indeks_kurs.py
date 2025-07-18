import os
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_CHAT_ID:
        print("Telegram Chat ID belum diatur.")
        return
    url = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    print("Telegram response:", response.text)

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("Membuka halaman IPOT...")
        page.goto("https://www.indopremier.com/#ipot/app/marketlive", timeout=60000)
        page.wait_for_timeout(5000)

        try:
            print("Menunggu elemen IDX COMPOSITE...")
            page.wait_for_selector("div:has-text('IDX COMPOSITE')", timeout=20000)
            indeks = page.locator("div:has-text('IDX COMPOSITE')").first.inner_text()

            print("Menunggu elemen USD/IDR...")
            page.wait_for_selector("text=USD/IDR", timeout=20000)
            kurs_element = page.locator("text=USD/IDR").nth(0)
            kurs_parent = kurs_element.locator("xpath=..")
            kurs = kurs_parent.inner_text()

        except PlaywrightTimeoutError as e:
            browser.close()
            raise Exception(f"Gagal menemukan elemen halaman: {e}")
        
        browser.close()
        return indeks, kurs

# Main process
try:
    indeks, kurs = scrape_indeks_kurs()
    message = f"📊 <b>Data Indeks & Kurs IPOT</b>\n\n<b>{indeks}</b>\n💱 {kurs}"
    send_telegram_message(message)
except Exception as e:
    print("Error:", str(e))
    send_telegram_message(f"❌ Gagal scraping data indeks & kurs:\n{e}")
