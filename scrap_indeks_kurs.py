from playwright.sync_api import sync_playwright
import os, requests, re

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto("https://indopremier.com/#ipot/app/marketlive", timeout=60000)

        # --- 1. Tutup modal / backdrop kalau ada ---
        for _ in range(3):
            if page.locator(".modal-in, .popover-info, .popup-backdrop").count():
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
            else:
                break

        # --- 2. Klik tab "Indeks & Kurs" ---
        idx_tab = page.get_by_text("Indeks & Kurs")
        idx_tab.wait_for(state="visible", timeout=10000)
        idx_tab.click(force=True)               # force=true lewati cek overlap

        # --- 3. Tunggu tabel muncul lalu ambil text ---
        page.wait_for_timeout(3000)             # tunggu render
        rows = page.locator("ion-grid ion-row").all_inner_texts()

        result = "📊 *Indeks & Kurs:*\n"
        for r in rows:
            clean = re.sub(r"\s+", " ", r).strip()
            if clean and re.search(r"\d", clean):
                result += f"• {clean}\n"
                if len(result) > 1500:
                    break

        browser.close()
        return result.strip()
print("DEBUG raw data:")
print(repr(data))          # tampilkan semua karakter termasuk \n

def send_to_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload, timeout=10)
    print("✅ Terkirim" if r.ok else f"❌ Gagal: {r.text}")

if __name__ == "__main__":
    data = scrape_indeks_kurs()
    print("DEBUG raw data:")
    print(repr(data))

    # Kirim selama tidak kosong
    if data and "Indeks" in data:
        send_to_telegram(data)
    else:
        # Tetap kirim pesan error supaya kamu tahu
        send_to_telegram("⚠️ Scraping selesai, tapi tidak ada data indeks yang terdeteksi.")
