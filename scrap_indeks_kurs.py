from playwright.sync_api import sync_playwright, TimeoutError
import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print("🔄 Membuka halaman IPOT Market Live...")
        page.goto("https://indopremier.com/#ipot/app/marketlive", timeout=60000)

        try:
            # Tunggu elemen tabel muncul (berdasarkan teks "Indeks & Kurs")
            print("⏳ Menunggu elemen Indeks & Kurs...")
            page.wait_for_selector("text=Indeks & Kurs", timeout=30000)

            # Ambil semua baris indeks
            indeks_rows = page.locator("div:has-text('Indeks & Kurs')").locator("xpath=..").locator("table tr").all()

            result = "**📊 Indeks & Kurs**\n"
            for row in indeks_rows:
                try:
                    cols = row.locator("td").all_inner_texts()
                    if len(cols) >= 3:
                        nama, last, chg = cols[:3]
                        result += f"• {nama.strip()}: {last.strip()} ({chg.strip()})\n"
                except:
                    continue

            return result.strip()

        except TimeoutError:
            return "❌ Gagal menemukan data Indeks & Kurs (Timeout)"
        finally:
            browser.close()

def send_to_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("❌ Token atau Chat ID kosong!")
        return

    url = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Pesan berhasil dikirim ke Telegram")
        else:
            print(f"❌ Gagal kirim pesan: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    data = scrape_indeks_kurs()
    print("🔍 Hasil Scraping:")
print(data)
if "Indeks" in data:
    send_to_telegram(data)
else:
    print("⚠️ Tidak ada data yang valid untuk dikirim ke Telegram.")
