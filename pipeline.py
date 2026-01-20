import os
import subprocess
from dagster import op, job, schedule, Definitions, RunConfig
from dotenv import load_dotenv

# --- 1. Define Operations (Ops) ---
# We use inputs/outputs (start_flag) just to enforce execution order (Dependencies)

@op
def scrape_telegram_data():
    """
    Executes the Task 1 Scraper script.
    Extracts messages and images to data/raw/.
    """
    print("🚀 Starting Scraper...")
    # Uses subprocess to run the script as if you typed it in terminal
    result = subprocess.run(["python", "scripts/scrape_data.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Scraper failed: {result.stderr}")
    
    print(result.stdout)
    return "Scraping Completed"

@op
def run_yolo_enrichment(start_flag: str):
    """
    Executes the Task 3 YOLO detection script.
    Depends on Scraper finishing first.
    """
    print("👁️ Starting YOLO Detection...")
    result = subprocess.run(["python", "scripts/detect_objects.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"YOLO failed: {result.stderr}")
        
    print(result.stdout)
    return "Enrichment Completed"

@op
def load_raw_to_postgres(start_flag: str):
    """
    Executes the Task 2 Loading script.
    Depends on YOLO finishing (to get the CSV).
    """
    print("💾 Loading Raw Data to Postgres...")
    result = subprocess.run(["python", "scripts/load_raw.py"], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Loader failed: {result.stderr}")

    print(result.stdout)
    return "Loading Completed"

@op
def run_dbt_transformations(start_flag: str):
    """
    Executes 'dbt build'.
    Passes the loaded environment variables explicitly to the dbt subprocess.
    """
    print("🏗️ Running dbt Transformations...")
    
    # We explicitly pass the current environment (which includes .env vars)
    # This ensures profiles.yml can read {{ env_var('POSTGRES_HOST') }}
    result = subprocess.run(
        ["dbt", "build", "--project-dir", "medical_warehouse"], 
        capture_output=True, 
        text=True,
        env=os.environ.copy() # <--- This ensures dbt sees the variables
    )
    
    if result.returncode != 0:
        raise Exception(f"dbt failed: {result.stderr}")

    print(result.stdout)
    return "dbt Completed"

# --- 2. Define the Job (Graph) ---
@job
def etl_pipeline_job():
    """
    Defines the dependency graph:
    Scrape -> YOLO -> Load -> dbt
    """
    # The output of one function is passed as input to the next
    # This forces Dagster to wait for the previous step to finish
    scraped = scrape_telegram_data()
    enriched = run_yolo_enrichment(scraped)
    loaded = load_raw_to_postgres(enriched)
    run_dbt_transformations(loaded)

# --- 3. Define Schedule ---
@schedule(cron_schedule="0 0 * * *", job=etl_pipeline_job, execution_timezone="UTC")
def daily_pipeline_schedule():
    """Runs the pipeline every day at midnight UTC"""
    return RunConfig()

# --- 4. Export Definitions ---
defs = Definitions(
    jobs=[etl_pipeline_job],
    schedules=[daily_pipeline_schedule]
)