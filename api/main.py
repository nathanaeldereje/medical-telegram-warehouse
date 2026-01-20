# api\main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from . import database, schemas

app = FastAPI(
    title="Ethiopian Medical BizOps API",
    description="Analytics API for Kara Solutions, powered by Telegram Data & YOLOv8",
    version="1.0.0"
)

# --- Endpoint 1: Top Frequently Mentioned Terms (Proxy for Products) ---
@app.get("/api/reports/top-products", response_model=List[schemas.TrendingTerm])
def get_top_products(limit: int = 10, db: Session = Depends(database.get_db)):
    """
    Returns the most frequent words in messages (excluding common stop words).
    Acts as a proxy for 'Top Products' mentioned.
    """
    # Note: In a real production scenario, we would use a dedicated pre-computed table 
    # or a Postgres Full Text Search (tsvector) column for this.
    # This query splits text into words and counts them.
    # FIX 1: Added 'r' before the string to make it a raw string (fixes \s warning)
    # FIX 2: Renamed 'count' to 'frequency' to avoid conflict with Python's .count() method
    query = text(r"""
        SELECT 
            word as term, 
            COUNT(*) as frequency
        FROM (
            SELECT regexp_split_to_table(lower(message_text), '\s+') as word
            FROM public_marts.fct_messages
            WHERE message_text IS NOT NULL
        ) t
        WHERE length(word) > 4 
          AND word NOT IN ('price', 'please', 'admin', 'telegram', 'contact', 'channel') 
        GROUP BY word
        ORDER BY frequency DESC
        LIMIT :limit;
    """)
    
    result = db.execute(query, {"limit": limit}).fetchall()
    
    # Map 'frequency' from DB to 'count' in Pydantic schema
    return [schemas.TrendingTerm(term=row.term, count=row.frequency) for row in result]

# --- Endpoint 2: Channel Activity Over Time ---
@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivity])
def get_channel_activity(channel_name: str, db: Session = Depends(database.get_db)):
    """
    Returns daily posting volume for a specific channel.
    """
    query = text("""
        SELECT 
            d.full_date as date,
            c.channel_name,
            COUNT(f.message_id) as post_count
        FROM public_marts.fct_messages f
        JOIN public_marts.dim_dates d ON f.date_key = d.date_key
        JOIN public_marts.dim_channels c ON f.channel_key = c.channel_key
        WHERE c.channel_name = :channel_name
        GROUP BY d.full_date, c.channel_name
        ORDER BY d.full_date DESC;
    """)
    
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    
    if not result:
        raise HTTPException(status_code=404, detail="Channel not found or no data available")
        
    return [
        schemas.ChannelActivity(date=row.date, channel_name=row.channel_name, post_count=row.post_count) 
        for row in result
    ]


# --- Endpoint 3: Message Search ---
@app.get("/api/search/messages", response_model=List[schemas.MessageResponse])
def search_messages(keyword: str, limit: int = 20, db: Session = Depends(database.get_db)):
    """
    Full-text search for messages containing specific keywords (e.g., 'Paracetamol').
    """
    query = text("""
        SELECT 
            f.message_id,
            c.channel_name,
            f.message_text,
            f.view_count,
            d.full_date as message_date -- Simplified for demo, ideally reconstruct timestamp
        FROM public_marts.fct_messages f
        JOIN public_marts.dim_channels c ON f.channel_key = c.channel_key
        JOIN public_marts.dim_dates d ON f.date_key = d.date_key
        WHERE f.message_text ILIKE :keyword
        ORDER BY f.view_count DESC
        LIMIT :limit;
    """)
    
    # Add wildcards for ILIKE
    search_term = f"%{keyword}%"
    result = db.execute(query, {"keyword": search_term, "limit": limit}).fetchall()
    
    return [
        schemas.MessageResponse(
            message_id=row.message_id,
            channel_name=row.channel_name,
            message_date=row.message_date,
            message_text=row.message_text,
            view_count=row.view_count
        )
        for row in result
    ]


# --- Endpoint 4: Visual Content Statistics (YOLO) ---
@app.get("/api/reports/visual-content", response_model=List[schemas.VisualStat])
def get_visual_stats(db: Session = Depends(database.get_db)):
    """
    Returns distribution of image categories detected by YOLO.
    """
    # FIX: Renamed 'count' to 'img_count' here as well to be safe
    query = text("""
        SELECT 
            image_category,
            COUNT(*) as img_count,
            AVG(confidence_score) as avg_confidence
        FROM public_marts.fct_image_detections
        GROUP BY image_category
        ORDER BY img_count DESC;
    """)
    
    result = db.execute(query).fetchall()
    
    return [
        schemas.VisualStat(
            image_category=row.image_category, 
            count=row.img_count, 
            avg_confidence=round(row.avg_confidence, 2)
        ) 
        for row in result
    ]

# --- Root ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the Medical Warehouse API. Visit /docs for documentation."}