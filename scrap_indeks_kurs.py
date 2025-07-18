from playwright.sync_api import sync_playwright
import os, requests, re

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto("https://indopremier.com/#ipot/app/marketlive", timeout=60000)

        # Tutup modal kalau ada
        for _ in range(3):
            if page.locator(".modal-in, .popover-info, .popup-backdrop").count():
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
            else:
                break

        # Klik tab "Indeks & Kurs"
        idx_tab = page.get_by_text("Indeks & Kurs")
        idx_tab.wait_for(state="visible", timeout=10000)
        idx_tab.click(force=True)
        page.wait_for_timeout(4000)

        # Ambil seluruh teks halaman
        full_text = page.locator("body").inner_text(timeout=15000)

        # Ekstrak bagian mulai dari "Indeks & Kurs"
        start = full_text.find("Indeks & Kurs")
        if start == -1:
            return "❌ Label 'Indeks & Kurs' tidak ditemukan."

        # Ambil ~30 baris setelah label
        slice_text = full_text[start:start+2500]
        lines = [ln.strip() for ln in slice_text.splitlines() if ln.strip()]

        result = "📊 *Indeks & Kurs:*\n"
        for ln in lines[1:]:                # skip judul
            if re.search(r"\d", ln):
                result += f"• {ln}\n"
                if len(result) > 1500:
                    break

        # Screenshot debug
        os.makedirs("debug", exist_ok=True)
        page.screenshot(path="debug/page.png", full_page=True)

        browser.close()
        return result.strip()

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
    if data.count("•") >= 1:
        send_to_telegram(data)
    else:
        send_to_telegram("⚠️ Scraping selesai, tapi tidak ada baris data yang memuat angka.")
