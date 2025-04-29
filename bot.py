#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import smtplib
from email.message import EmailMessage
import schedule
import time
import os

# ========== CONFIGURATION ==========
AUTOTRADER_URL = "https://www.autotrader.co.uk/car-search?advertising-location=at_cars&aggregatedTrim=GTI%20Performance&colour=Black&homeDeliveryAdverts=include&make=Volkswagen&maximum-mileage=60000&model=Golf&moreOptions=visible&postcode=ha7%202sa&quantity-of-https://www.autotrader.co.uk/car-search?advertising-location=at_cars&aggregatedTrim=GTI%20Performance&colour=Black&homeDeliveryAdverts=include&make=Volkswagen&maximum-mileage=60000&model=Golf&moreOptions=visible&postcode=ha7%202sa&quantity-of-doors=5&sort=relevance&transmission=Manual&year-from=2017"
STATE_FILE = "seen_listings.json"

# Email settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "donovanh59@gmail.com"
SMTP_PASSWORD = "shar rspm ewxw golu"
EMAIL_FROM = "donovanh59@gmail.com"
EMAIL_TO = "donovanh59@gmail.com"

# How often to check (in minutes)
CHECK_INTERVAL = 10
# ===================================

def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen(seen_ids):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen_ids), f)

def fetch_listing_ids():
    resp = requests.get(AUTOTRADER_URL, headers={
        "User-Agent": "Mozilla/5.0 (compatible; AutoTraderBot/1.0)"
    })
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    # Inspect the page’s HTML: each result has a data-listing-id, or link href with unique ID
    ids = set()
    for tag in soup.select("[data-listing-id]"):
        ids.add(tag["data-listing-id"])
    # Fallback: parse from URLs  
    # for a in soup.select("a[href*='/listing/']"):
    #     ids.add(a['href'].split('/')[-1].split('?')[0])
    return ids

def send_email(new_ids):
    msg = EmailMessage()
    msg["Subject"] = f"New AutoTrader listings: {len(new_ids)} found"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    body = "New listings matching your criteria:\n\n"
    for listing_id in new_ids:
        url = f"https://www.autotrader.co.uk/car-details/{listing_id}"
        body += f"- {url}\n"
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(msg)

def job():
    print("Checking for new listings…")
    seen = load_seen()
    current = fetch_listing_ids()

    new = current - seen
    if new:
        print(f"Found {len(new)} new listings: {new}")
        send_email(new)
        seen.update(new)
        save_seen(seen)
    else:
        print("No new listings at this time.")

if __name__ == "__main__":
    # Run immediately, then schedule
    job()
    schedule.every(CHECK_INTERVAL).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
