import time
import re
import requests
from bs4 import BeautifulSoup

# --- BİLGİLERİNİZ ---
TELEGRAM_TOKEN = "8592671406:AAFFIYhPN9wxb3ExApalQhALB6FST5iu9Ks"
CHAT_ID = "8936110690"
TARGET_PRICE = 150000.0  # Target price in TL

# Takip edilecek linkler (Gerekli ürün linklerini buraya ekleyin)
URLS = {
    "Amazon": "https://www.amazon.com.tr",
    "Hepsiburada": "https://www.hepsiburada.com",
    "Trendyol": "https://www.trendyol.com"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
}

def send_telegram_alert(site, current_price, url):
    message = (
        f"🚨 **FİYAT DÜŞTÜ / STOK YAKALANDI!** 🚨\n\n"
        f"📱 **Ürün:** iPhone 18 Pro Max 256 GB Burgonya\n"
        f"🛒 **Site:** {site}\n"
        f"💰 **Yeni Fiyat:** {current_price:,.2f} TL\n"
        f"🎯 **Hedef Fiyat:** {TARGET_PRICE:,.2f} TL\n\n"
        f"🔗 [Ürüne Gitmek İçin Tıklayın]({url})"
    )
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    api_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(api_url, data=payload)
    except Exception as e:
        print(f"Telegram bildirim hatası: {e}")

def parse_price(price_str):
    if not price_str:
        return None
    clean = re.sub(r"[^\d,\.]", "", price_str)
    if not clean:
        return None
    clean = clean.replace(".", "").replace(",", ".")
    try:
        return float(clean)
    except ValueError:
        return None

def check_prices():
    print("Fiyatlar kontrol ediliyor...")
    for site, url in URLS.items():
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            price = None

            if "amazon" in site.lower():
                price_element = soup.find("span", {"class": "a-price-whole"})
                if price_element:
                    price = parse_price(price_element.text)
            elif "hepsiburada" in site.lower():
                price_element = soup.find("span", {"id": "offering-price"}) or soup.find("span", {"class": "price"})
                if price_element:
                    price = parse_price(price_element.text)
            elif "trendyol" in site.lower():
                price_element = soup.find("span", {"class": "prc-dsc"})
                if price_element:
                    price = parse_price(price_element.text)

            if price and price <= TARGET_PRICE:
                print(f"[{site}] Fiyat şartı sağlandı: {price} TL")
                send_telegram_alert(site, price, url)
            else:
                print(f"[{site}] Kontrol yapıldı.")

        except Exception as e:
            print(f"[{site}] Taramada hata oluştu: {e}")

if __name__ == "__main__":
    print("Fiyat Takip Botu Başlatıldı!")
    while True:
        check_prices()
        time.sleep(60)  # Her 60 saniyede bir kontrol eder
