# Pipeline Scripts & Utilities

This directory contains executable scripts for running individual components of the data pipeline manually. These scripts import core logic from the `src/` module and execute specific tasks.

## 📂 Contents

| Script Name | Task | Description |
| :--- | :--- | :--- |
| **`scrape_data.py`** | **Extract** | Connects to Telegram API, downloads messages/images, and saves raw JSON to `data/raw/`. |
| **`load_raw.py`** | **Load** | Reads JSON files from the data lake and inserts them into the `raw.telegram_messages` table in PostgreSQL. |
| **`detect_objects.py`** | **Enrich** | Scans downloaded images, runs YOLOv8 inference, and saves detection results to CSV/DB. |
| **`cleanup.py`** | **Maintenance** | Utility to clear logs or temporary files (optional). |

## 🚀 Usage

Run these scripts from the **root** of the project to ensure file paths and imports work correctly.

### 1. Run the Scraper
```bash
python scripts/scrape.py
```

### 2. Load Raw Data to DB
```bash
python scripts/load_raw.py
```

### 3. Run Object Detection
```bash
python scripts/detect_objects.py
```

## ⚠️ Note on Imports
These scripts rely on the `src` package. If you encounter `ModuleNotFoundError`, make sure you are running the command from the project root, or set your python path:

```bash
export PYTHONPATH=$PYTHONPATH:.
python scripts/scrape.py
```
