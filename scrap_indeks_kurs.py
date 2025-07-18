from playwright.sync_api import sync_playwright, TimeoutError
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        print("🔄 Membuka halaman IPOT Market Live...")
        page.goto("https://indopremier.com/#ipot/app/marketlive", timeout=60000)

        try:
            # Tunggu sampai teks 'Indeks & Kurs' muncul
            print("⏳ Menunggu elemen 'Indeks & Kurs'...")
            page.wait_for_selector("text=Indeks & Kurs", timeout=30000)

            # Scroll sedikit untuk memastikan area tampil
            page.mouse.wheel(0, 500)

            # Ambil semua teks halaman
            content = page.locator("body").inner_text()

            # Filter bagian Indeks & Kurs
            start = content.find("Indeks & Kurs")
            if start == -1:
                raise Exception("❌ Tidak menemukan label 'Indeks & Kurs'")

            part = content[start:].split("\n\n")[0]
            result = "📊 *Indeks & Kurs:*\n"
            for line in part.split("\n")[1:]:
                if line.strip():
                    result += f"• {line.strip()}\n"

            return result.strip()

        except TimeoutError:
            return "❌ Gagal menemukan data Indeks & Kurs (Timeout)"
        except Exception as e:
            return f"❌ Error saat scraping: {e}"
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
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Pesan berhasil dikirim ke Telegram")
        else:
            print(f"❌ Gagal kirim pesan: {response.text}")
    except Exception as e:
        print(f"❌ Error kirim ke Telegram: {e}")

if __name__ == "__main__":
    data = scrape_indeks_kurs()
    print("🔍 Hasil Scraping:\n", data)

    if "Indeks" in data or "📊" in data:
        send_to_telegram(data)
    else:
        print("⚠️ Tidak ada data valid untuk dikirim ke Telegram.")
