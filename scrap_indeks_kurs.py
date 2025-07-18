from playwright.sync_api import sync_playwright
import os, requests
from dotenv import load_dotenv

load_dotenv()

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context()
        page = context.new_page()
        print("🔄 Membuka halaman IPOT Market Live...")
        page.goto("https://indopremier.com/#ipot/app/marketlive", timeout=60000)

        try:
            page.wait_for_selector("text=Indeks & Kurs", timeout=30000)
            page.mouse.wheel(0, 500)
            content = page.locator("body").inner_text()
            start = content.find("Indeks & Kurs")
            if start == -1:
                raise Exception("❌ Tidak menemukan label 'Indeks & Kurs'")

            part = content[start:].split("\n\n")[0]
            result = "📊 *Indeks & Kurs:*\n"
            for line in part.split("\n")[1:]:
                if line.strip():
                    result += f"• {line.strip()}\n"
            return result.strip()

        except Exception as e:
            return f"❌ Error: {e}"
        finally:
            browser.close()

def send_to_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload)
        print("✅ Pesan terkirim" if r.ok else f"❌ Gagal: {r.text}")
    except Exception as e:
        print(f"❌ Error kirim Telegram: {e}")

if __name__ == "__main__":
    data = scrape_indeks_kurs()
    print(data)
    if "Indeks" in data:
        send_to_telegram(data)
