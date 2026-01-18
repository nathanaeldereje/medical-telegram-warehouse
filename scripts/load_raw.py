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
    """Creates the 'raw' schema and tables."""
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        
        # 1. Telegram Messages Table
        connection.execute(text("""
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
        """))

        # 2. YOLO Detections Table (THIS WAS MISSING)
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS raw.yolo_detections (
            message_id BIGINT PRIMARY KEY,
            channel_name TEXT,
            image_path TEXT,
            detected_objects TEXT,
            best_confidence FLOAT,
            image_category TEXT
        );
        """))
        
        connection.commit()
        print("Schema 'raw' and tables ready.")

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
def load_yolo_to_postgres(engine):
    """Loads the YOLO results CSV into Postgres."""
    csv_path = "data/processed/yolo_results.csv"
    
    if not os.path.exists(csv_path):
        print("Skipping YOLO load: CSV not found. Run scripts/detect_objects.py first.")
        return

    print("Loading YOLO results...")
    df = pd.read_csv(csv_path)
    
    # Clean data
    df['message_id'] = pd.to_numeric(df['message_id'], errors='coerce')
    df = df.dropna(subset=['message_id'])
    df['message_id'] = df['message_id'].astype(int)

    with engine.connect() as connection:
        df.to_sql('temp_yolo', connection, if_exists='replace', index=False)
        
        upsert_query = """
        INSERT INTO raw.yolo_detections (message_id, channel_name, image_path, detected_objects, best_confidence, image_category)
        SELECT message_id, channel_name, image_path, detected_objects, best_confidence, image_category
        FROM temp_yolo
        ON CONFLICT (message_id) 
        DO UPDATE SET
            detected_objects = EXCLUDED.detected_objects,
            best_confidence = EXCLUDED.best_confidence,
            image_category = EXCLUDED.image_category;
        """
        connection.execute(text(upsert_query))
        connection.commit()
    
    print(f"Successfully processed {len(df)} YOLO detections.")

if __name__ == "__main__":
    engine = create_engine(DATABASE_URL)
    create_raw_schema(engine)
    load_json_to_postgres(engine)
    load_yolo_to_postgres(engine)