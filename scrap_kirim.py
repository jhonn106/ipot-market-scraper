# scrap_indeks_kurs.py
import asyncio
import os
import requests
from playwright.async_api import async_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

async def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.indopremier.com/#ipot/app/marketlive", timeout=60000)
        await page.wait_for_timeout(6000)  # delay render
        
        content = await page.content()
        
        # Ambil semua elemen yang terlihat di tab Indeks & Kurs
        # Catatan: kamu bisa adjust selector ini sesuai hasil inspect
        data = await page.locator("div.MuiBox-root").all_inner_texts()
        
        # Filter data yang berkaitan dengan indeks/kurs
        result = "\n".join([line for line in data if "USD" in line or "Index" in line or "%" in line])

        message = f"*📈 Indeks & Kurs IPOT Live:*\n\n```\n{result}\n```"
        print(message)
        await send_to_telegram(message)
        await browser.close()

asyncio.run(main())
