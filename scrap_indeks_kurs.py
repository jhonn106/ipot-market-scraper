from playwright.sync_api import sync_playwright
import os, requests, re

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto("https://indopremier.com/#ipot/app/marketlive", timeout=60000)

        # 1. Tunggu sampai menu “Indeks & Kurs” bisa diklik
        idx_tab = page.get_by_text("Indeks & Kurs")
        idx_tab.wait_for(state="visible", timeout=30000)
        idx_tab.click()

        # 2. Tunggu tabel indeks tampil (ambil semua baris teks)
        page.wait_for_timeout(3000)  # jeda loading
        rows = page.locator("css=ion-grid >> ion-row").all_inner_texts()

        result = "📊 *Indeks & Kurs:*\n"
        for r in rows:
            r = re.sub(r"\s+", " ", r).strip()
            if r and re.search(r"\d", r):   # pastikan ada angka
                result += f"• {r}\n"
                if len(result) > 1500:      # batasi panjang
                    break

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
    if data.count("•") >= 2:        # minimal 2 baris data
        send_to_telegram(data)
    else:
        print("⚠️ Tidak ada data indeks yang valid")
