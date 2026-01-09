import os
import requests
from bs4 import BeautifulSoup
import schedule
import time
import datetime
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events

 
api_id = int(os.getenv("API_ID", "0"))
api_hash = os.getenv("API_HASH", "")
token = os.getenv("BOT_TOKEN", "")
bot_username = os.getenv("BOT_USERNAME", "")

phone_number = os.getenv("PHONE_NUMBER", "")

URL = "https://apnews.com/search?q=iran&s=3"
printed_headlines = set()

just_started = True
chat_id = int(os.getenv("CHAT_ID", "0"))

bot = telebot.TeleBot(token)

def get_headlines():
    global just_started

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    response = requests.get(URL, headers=headers, timeout=30)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return
    
    soup = BeautifulSoup(response.content, "html.parser")
    promos = soup.select("div.PagePromo")
    for promo in promos:
        title_el = promo.select_one("div.PagePromo-title a, div.PagePromo-title span.PagePromoContentIcons-text")
        link_el = promo.select_one("div.PagePromo-title a")
        desc_el = promo.select_one("div.PagePromo-description a, div.PagePromo-description span.PagePromoContentIcons-text")
        if title_el:
            title_text = title_el.get_text(" ", strip=True)
        else:
            title_text = (promo.get("data-gtm-region") or "").strip()
        if not title_text:
            continue
        headline_key = title_text.lower()
        if headline_key and headline_key not in printed_headlines:
            printed_headlines.add(headline_key)
            print("TITLE: ", title_text)
            p_text = desc_el.get_text(" ", strip=True) if desc_el else ""
            link = link_el.get("href", "").strip() if link_el else ""
            if p_text:
                print("DESCRIPTION: ", p_text)
            if link:
                print("LINK: ", link)
            print()  
            if not just_started:
                print("===================================================")
                send_telegram_message(title_text, p_text, link)
    if just_started:
        send_telegram_message("start", "start")
    just_started = False

def send_telegram_message(title, description, link=""):  
    global chat_id
    
    try:
        message = f"<b>{title}</b>\n\n{description}\n\n{link}"
        bot.send_message(chat_id, message, parse_mode='HTML')
        print(f"Message sent successfully")
    except Exception as e:
        print(f"Error sending message: {e}")


def run():
    schedule.every(0.1).minutes.do(get_headlines)
    print("Scheduler started. Running every 6 seconds.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run()
