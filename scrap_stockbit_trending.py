from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import requests

# --- Konfigurasi Akun dan Telegram ---
STOCKBIT_EMAIL = 'jhonni.cool@gmail.com'
STOCKBIT_PASSWORD = 'jh0nn10614'
TELEGRAM_BOT_TOKEN = '7249080183:AAEkMHdJ-fL0mI_LRqXT6UtJ2-DS5QI4j8M'
TELEGRAM_CHAT_ID = '178798282'

# --- Setup Selenium (headless browser) ---
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=chrome_options)

try:
    # 1. Login ke Stockbit
    driver.get('https://stockbit.com/login')
    time.sleep(3)

    # Isi email
    email_input = driver.find_element(By.NAME, 'username')
    email_input.send_keys(STOCKBIT_EMAIL)
    time.sleep(1)

    # Isi password
    password_input = driver.find_element(By.NAME, 'password')
    password_input.send_keys(STOCKBIT_PASSWORD)
    time.sleep(1)

    # Klik login
    password_input.send_keys(Keys.RETURN)
    time.sleep(5)  # Tunggu proses login

    # 2. Akses halaman trending stock
    driver.get('https://stockbit.com/stream')
    time.sleep(5)  # Tunggu data termuat

    # 3. Scrape trending stock
    trending_stocks = []
    stocks_elem = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="TrendingStockItem"]')
    for elem in stocks_elem:
        try:
            symbol = elem.find_element(By.CSS_SELECTOR, '.sc-1vyl0yv-5 span').text
            name = elem.find_element(By.CSS_SELECTOR, '.sc-1vyl0yv-7').text
            trending_stocks.append(f"{symbol} - {name}")
        except Exception:
            continue

    # 4. Kirim ke Telegram
    if trending_stocks:
        message = "Trending Stock di Stockbit\n\n" + "\n".join(trending_stocks)
    else:
        message = "Gagal mengambil data trending stock."

    requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        data={'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    )

finally:
    driver.quit()
