import os
import sys 
import subprocess
from dagster import op, job, schedule, Definitions, RunConfig
from dotenv import load_dotenv

# --- CRITICAL: Execute this function to load variables ---
load_dotenv() 

@op
def scrape_telegram_data():
    """
    Executes the Task 1 Scraper script.
    """
    print(f"🚀 Starting Scraper using: {sys.executable}")
    result = subprocess.run([sys.executable, "scripts/scrape_data.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Scraper failed: {result.stderr}")
    
    print(result.stdout)
    return "Scraping Completed"

@op
def run_yolo_enrichment(start_flag: str):
    """
    Executes the Task 3 YOLO detection script.
    """
    print("👁️ Starting YOLO Detection...")
    result = subprocess.run(
        [sys.executable, "scripts/detect_objects.py"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        raise Exception(f"YOLO failed: {result.stderr}")
        
    print(result.stdout)
    return "Enrichment Completed"

@op
def load_raw_to_postgres(start_flag: str):
    """
    Executes the Task 2 Loading script.
    """
    print("💾 Loading Raw Data to Postgres...")
    result = subprocess.run([sys.executable, "scripts/load_raw.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Loader failed: {result.stderr}")

    print(result.stdout)
    return "Loading Completed"

@op
def run_dbt_transformations(start_flag: str):
    """
    Executes 'dbt build'.
    """
    print("🏗️ Running dbt Transformations...")
    
    # FIX: Added "--profiles-dir", "medical_warehouse"
    # This tells dbt to look for profiles.yml in the local folder, not the user home folder.
    result = subprocess.run(
        [
            "dbt", "build", 
            "--project-dir", "medical_warehouse", 
            "--profiles-dir", "medical_warehouse"
        ], 
        capture_output=True, 
        text=True,
        env=os.environ.copy()
    )
    
    if result.returncode != 0:
        raise Exception(f"dbt failed: {result.stderr}")

    print(result.stdout)
    return "dbt Completed"

# --- Define the Job ---
@job
def etl_pipeline_job():
    scraped = scrape_telegram_data()
    enriched = run_yolo_enrichment(scraped)
    loaded = load_raw_to_postgres(enriched)
    run_dbt_transformations(loaded)

# --- Define Schedule ---
@schedule(cron_schedule="0 0 * * *", job=etl_pipeline_job, execution_timezone="UTC")
def daily_pipeline_schedule():
    return RunConfig()

# --- Export Definitions ---
defs = Definitions(
    jobs=[etl_pipeline_job],
    schedules=[daily_pipeline_schedule]
)