# scripts\scrape_data.py
import sys
import os
import asyncio
from dotenv import load_dotenv

# Add the project root to system path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scraper import TelegramScraper

# Load secrets
load_dotenv()
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')
PHONE = os.getenv('TG_PHONE')

# List of channels to scrape
CHANNELS = [
    'https://t.me/Lobelia4Cosmetics',
    'https://t.me/tikvahpharma',
    'https://t.me/CheMed123', # Example placeholder, verify exact handle
]

async def main():
    scraper = TelegramScraper(API_ID, API_HASH, PHONE)
    
    try:
        await scraper.connect()
        
        for channel in CHANNELS:
            # Extract username from URL if necessary
            handle = channel.split('/')[-1]
            await scraper.scrape_channel(handle, limit=300) # Start small with 200
            
    finally:
        scraper.close()

if __name__ == "__main__":
    asyncio.run(main())