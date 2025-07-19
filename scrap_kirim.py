import asyncio
from playwright.async_api import async_playwright
import requests
import os
import re

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def kirim_telegram(pesan):
    url = f"https://api.telegram.org/bot7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M/sendMessage"
    data = {
        "chat_id": 7249080183,
        "text": pesan,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

async def scrape():
    hasil = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.indopremier.com/#ipot/app/marketlive", wait_until="networkidle")
        await page.wait_for_timeout(10000)

        rows = await page.locator("css=table >> tbody >> tr").all()
        for row in rows:
            text = await row.inner_text()
            match = re.search(r"(\d{2}:\d{2}:\d{2})\s+(\w+)\s+([\d\.]+)\s+[-\d\.]+\s+[-\d\.%]+\s+([\d\.]+)", text)
            if match:
                time, kode, harga, lot = match.groups()
                lot = float(lot.replace('.', '').replace(',', ''))
                if lot > 1:
                    hasil.append(f"{time} | <b>{kode}</b> | Rp{harga} | Lot: {int(lot)}")
        await browser.close()

    if hasil:
        return "📊 <b>Running Trade > 1000 Lot</b>\n" + "\n".join(hasil)
    else:
        return "❌ Tidak ada transaksi dengan volume > 1000 saat ini."

async def main():
    pesan = await scrape()
    kirim_telegram(pesan)

if __name__ == "__main__":
    asyncio.run(main())
