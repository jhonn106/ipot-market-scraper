from playwright.sync_api import sync_playwright
import os, requests, re

def scrape_indeks_kurs():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        page = browser.new_page()
        page.goto("https://indopremier.com/#ipot/app/marketlive", timeout=60000)

        # Tunggu sampai minimal satu baris indeks muncul
        page.wait_for_selector('xpath=//div[contains(@class,"index-item") or @data-testid="index-row"]', timeout=30000)

        # Scroll ke bagian indeks agar semua data ter-render
        page.evaluate("window.scrollTo(0, 400)")

        # Ambil text dari setiap baris indeks
        rows = page.locator('xpath=//div[contains(@class,"index-item") or @data-testid="index-row"]').all_inner_texts()

        result = "📊 *Indeks & Kurs:*\n"
        for r in rows:
            # Bersihkan baris yang kosong atau hanya simbol
            r = re.sub(r"\s+", " ", r).strip()
            if r and not re.match(r"^[\W_]+$", r):
                result += f"• {r}\n"

        browser.close()
        return result.strip()

def send_to_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload, timeout=10)
    print("✅ Terkirim" if r.ok else f"❌ Gagal: {r.text}")

if __name__ == "__main__":
    data = scrape_indeks_kurs()
    if "Indeks" in data and len(data) > 50:   # cegah pesan kosong
        send_to_telegram(data)
    else:
        print("⚠️ Tidak ada data indeks yang valid")
