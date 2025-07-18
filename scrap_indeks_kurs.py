import requests, os, datetime

def scrape_indeks_kurs():
    # endpoint internal IPOT (ditemukan lewat DevTools → Network)
    url = "https://www.indopremier.com/ipot-go/api/market/index/list"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return f"❌ Gagal fetch JSON: {e}"

    if not data.get("data"):
        return "⚠️ JSON kosong."

    result = "📊 *Indeks & Kurs*\n"
    for item in data["data"]:
        name   = item.get("name", "")
        last   = item.get("last", "")
        change = item.get("chg", "")
        pct    = item.get("chgPct", "")
        if last:
            result += f"• {name} {last} ({change} {pct}%)\n"
            if len(result) > 1500:
                break
    return result.strip()

def send_to_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8Mk/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    r = requests.post(url, json=payload, timeout=10)
    print("✅ Terkirim" if r.ok else f"❌ Gagal: {r.text}")

if __name__ == "__main__":
    text = scrape_indeks_kurs()
    print("DEBUG:", repr(text))
    if text.count("•") >= 1:
        send_to_telegram(text)
    else:
        send_to_telegram("⚠️ Tidak ada baris data indeks.")
