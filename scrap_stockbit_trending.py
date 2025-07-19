import os
import requests

URL = "https://www.stockbit.com/api/v1/trending/stocks"

def scrape_stockbit_trending():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    try:
        r = requests.get(URL, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return f"❌ Gagal fetch trending: {e}"

    stocks = data.get("data", {}).get("stocks", [])
    if not stocks:
        return "⚠️ Tidak ada saham trending."

    msg = "🔥 *Stockbit Trending Stocks*\n"
    for s in stocks[:10]:
        ticker = s.get("symbol", "")
        last   = s.get("last", "")
        change = s.get("chg", "")
        pct    = s.get("chg_pct", "")
        msg += f"• `{ticker}` {last} ({change:+} {pct:+}%)\n"
    return msg.strip()

def send_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat  = os.getenv("TELEGRAM_CHAT_ID")
    url   = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage"
    r = requests.post(url, json={"chat_id": chat, "text": text, "parse_mode": "Markdown"})
    print("✅ Sent" if r.ok else f"❌ {r.text}")

if __name__ == "__main__":
    text = scrape_stockbit_trending()
    print("DEBUG:", text)
    send_telegram(text)
