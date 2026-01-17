import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Credentials
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "medical_warehouse")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

# Connection String
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_raw_schema(engine):
    """Creates the 'raw' schema and the telegram_messages table."""
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        
        # Create table with a unique constraint on message_id and channel_name to prevent dupes
        create_table_query = """
        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            id SERIAL PRIMARY KEY,
            message_id BIGINT,
            channel_name TEXT,
            message_date TIMESTAMP,
            message_text TEXT,
            has_media BOOLEAN,
            image_path TEXT,
            views INT,
            forwards INT,
            scraped_at TIMESTAMP,
            CONSTRAINT unique_msg_channel UNIQUE (message_id, channel_name)
        );
        """
        connection.execute(text(create_table_query))
        connection.commit()
        print("Schema 'raw' and table 'telegram_messages' ready.")

def load_json_to_postgres(engine):
    """Iterates over JSON files and loads them into Postgres."""
    base_path = "data/raw/telegram_messages"
    
    all_messages = []
    
    # Walk through the directory structure
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            all_messages.extend(data)
                    except json.JSONDecodeError:
                        print(f"Skipping corrupt file: {file_path}")

    if not all_messages:
        print("No data found to load.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(all_messages)
    
    # Ensure correct types
    df['message_date'] = pd.to_datetime(df['message_date'])
    df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    
    # Upsert Logic using temporary table (standard efficient pattern)
    with engine.connect() as connection:
        # 1. Load data to a temporary table
        df.to_sql('temp_telegram_messages', connection, if_exists='replace', index=False)
        
        # 2. Upsert from temp to raw (Update if exists, Insert if new)
        upsert_query = """
        INSERT INTO raw.telegram_messages (
            message_id, channel_name, message_date, message_text, 
            has_media, image_path, views, forwards, scraped_at
        )
        SELECT 
            message_id, channel_name, message_date, message_text, 
            has_media, image_path, views, forwards, scraped_at
        FROM temp_telegram_messages
        ON CONFLICT (message_id, channel_name) 
        DO UPDATE SET
            views = EXCLUDED.views,
            forwards = EXCLUDED.forwards,
            message_text = EXCLUDED.message_text,
            scraped_at = EXCLUDED.scraped_at;
        """
        connection.execute(text(upsert_query))
        connection.commit()
        
    print(f"Successfully processed {len(df)} records.")

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    create_raw_schema(engine)
    load_json_to_postgres(engine)