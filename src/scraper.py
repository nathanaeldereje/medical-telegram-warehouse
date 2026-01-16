# src\scraper.py
import os
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
import asyncio
from tqdm import tqdm

# Configure Logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TelegramScraper:
    def __init__(self, api_id, api_hash, phone_number):
        self.client = TelegramClient('medical_scraper_session', api_id, api_hash)
        self.phone_number = phone_number
        self.raw_data_path = 'data/raw/telegram_messages'
        self.images_path = 'data/raw/images'

    async def connect(self):
        """Connect to the Telegram Client."""
        # 'start' returns the client itself, which is awaitable for the login flow.
        # We add 'type: ignore' to silence Pylance's strict warning.
        await self.client.start(phone=self.phone_number) # type: ignore
        logging.info("Successfully connected to Telegram API")

    def _get_json_path(self, date_str, channel_name):
        """Generate path for JSON storage: data/raw/telegram_messages/YYYY-MM-DD/channel.json"""
        dir_path = os.path.join(self.raw_data_path, date_str)
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, f"{channel_name}.json")

    def _get_image_path(self, channel_name, message_id):
        """Generate path for image storage: data/raw/images/channel/msg_id.jpg"""
        dir_path = os.path.join(self.images_path, channel_name)
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, f"{message_id}.jpg")

    async def scrape_channel(self, channel_handle, limit=1000):
        """
        Scrape messages from a specific channel.
        :param channel_handle: The telegram handle (e.g., 'tikvahpharma')
        :param limit: Max messages to scrape (None for all)
        """
        logging.info(f"Starting scrape for {channel_handle}")
        print(f"Scraping {channel_handle}...")

        # Dictionary to group messages by date for batch saving
        # Structure: { '2024-01-14': [msg1, msg2], ... }
        data_by_date = {}

        try:
            entity = await self.client.get_entity(channel_handle)
            # Iterate through messages
            async for message in self.client.iter_messages(entity, limit=limit):
                if not message.date:
                    continue

                msg_date_str = message.date.strftime('%Y-%m-%d')
                
                # extracting media
                image_path = None
                if message.photo:
                    # Download image
                    img_save_path = self._get_image_path(channel_handle, message.id)
                    # Check if exists to skip re-downloading
                    if not os.path.exists(img_save_path):
                        await self.client.download_media(message.photo, img_save_path)
                    image_path = img_save_path

                # Construct Data Object
                msg_data = {
                    "message_id": message.id,
                    "channel_name": channel_handle,
                    "message_date": message.date.isoformat(),
                    "message_text": message.text,
                    "has_media": bool(message.media),
                    "image_path": image_path,
                    "views": message.views if message.views else 0,
                    "forwards": message.forwards if message.forwards else 0,
                    "scraped_at": datetime.now().isoformat(),

                }

                # Group by date
                if msg_date_str not in data_by_date:
                    data_by_date[msg_date_str] = []
                data_by_date[msg_date_str].append(msg_data)

            # Save Data to JSON files
            self._save_data(data_by_date, channel_handle)
            logging.info(f"Finished scraping {channel_handle}")

        except Exception as e:
            logging.error(f"Error scraping {channel_handle}: {str(e)}")
            print(f"Error: {e}")



    def _save_data(self, data_by_date, channel_handle):
        """Saves grouped data to respective JSON files."""
        for date_str, messages in data_by_date.items():
            file_path = self._get_json_path(date_str, channel_handle)
            
            existing_data = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        pass # File corrupted or empty
            
            # --- CHANGE STARTED HERE ---
            
            # 1. Convert existing list to a dictionary keyed by message_id
            # This makes looking up old messages instant (O(1))
            data_map = {msg['message_id']: msg for msg in existing_data}
            
            # 2. Update the map with the new messages
            # If the ID exists, it gets OVERWRITTEN (updating views, forwards, text)
            # If the ID is new, it gets ADDED
            for msg in messages:
                data_map[msg['message_id']] = msg
                
            # 3. Convert back to list
            final_data = list(data_map.values())
            
            # 4. Optional: Sort by message_id to keep JSON tidy
            final_data.sort(key=lambda x: x['message_id'])
            
            # --- CHANGE ENDED HERE ---

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=4, ensure_ascii=False)

    def close(self):
        self.client.disconnect()