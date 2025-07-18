import os
import time
import requests
from playwright.sync_api import sync_playwright

def send_to_telegram(message):
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f'https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage'
    data = {'chat_id': chat_id, 'text': message}
    response = requests.post(url, data=data)
    print("Telegram response:", response.text)

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("https://www.indopremier.com/#ipot/app/marketlive")
        time.sleep(10)  # Tambahkan delay agar halaman selesai loading

        # Tunggu elemen indeks muncul
        indeks = page.locator("div:has-text('IDX COMPOSITE')").first.inner_text()

        # Tunggu elemen kurs muncul
        kurs = page.locator("div:has-text('USD/IDR')").first.inner_text()

        browser.close()
        return indeks, kurs

if __name__ == "__main__":
    try:
        indeks, kurs = scrape_indeks_kurs()
        message = f"📈 *Data Indeks & Kurs (IPOT)*\n\n{indeks}\n\n{kurs}"
        send_to_telegram(message)
    except Exception as e:
        send_to_telegram(f"Gagal scrap: {e}")
        raise
