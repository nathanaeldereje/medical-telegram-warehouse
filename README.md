# Ethiopian Medical Business Intelligence Warehouse 🏥
### **Project:** Kara Solutions Data Platform
**Role:** Data Engineer  
**Status:** 🚧 In Progress  

## 📖 Project Overview
This project builds a robust, end-to-end **ELT (Extract, Load, Transform)** data pipeline for **Kara Solutions**, a leading data science consultancy in Ethiopia.

The goal is to centralize and analyze scattered data from Ethiopian medical Telegram channels (e.g., CheMed, Tikvah Pharma). By scraping raw messages and images, transforming them into a structured **Data Warehouse**, and enriching them with **Object Detection (YOLO)**, this platform generates actionable insights on pharmaceutical market trends.

The system answers critical questions such as:
*   *What are the top 10 most mentioned medical products?*
*   *How do prices vary across different channels?*
*   *What is the ratio of promotional (images) vs. informational content?*

## 🎯 Business Objective
**The Problem:**
Ethiopian medical businesses rely heavily on Telegram for marketing and distribution. However, this data is unstructured, ephemeral, and scattered across dozens of channels. Stakeholders cannot easily track product availability, pricing trends, or competitor activity without manual monitoring.

**The Solution:**
Develop a scalable data pipeline that:
1.  **Extracts** real-time data from Telegram.
2.  **Cleans & Models** it into a Star Schema for high-performance analytics.
3.  **Enriches** it by detecting objects in product images (e.g., medicines, cosmetics).
4.  **Serves** insights via a REST API for downstream applications.

**Key Performance Indicators (KPIs):**
*   **Data Reliability:** Single Source of Truth via dimensional modeling (Star Schema).
*   **Latency:** Automated pipelines reducing data lag from days to hours.
*   **Enrichment:** Adding computer vision context to 100% of collected images.

## 🛠️ Tech Stack
*   **Extraction:** Telethon (Telegram API)
*   **Orchestration:** Dagster
*   **Transformation:** dbt (Data Build Tool)
*   **Data Warehouse:** PostgreSQL
*   **Computer Vision:** YOLOv8 (Object Detection)
*   **API Layer:** FastAPI
*   **Containerization:** Docker

## 📦 Key Deliverables
*   **`data/raw/`**: A Data Lake containing raw JSON messages and downloaded images.
*   **`medical_warehouse/`**: A dbt project containing the Star Schema (Fact/Dimension tables).
*   **`src/yolo_detect.py`**: A computer vision module for image classification.
*   **`api/`**: A FastAPI application serving analytical endpoints.
*   **Dagster Pipeline**: A fully orchestrated workflow graph.

## 📂 Repository Structure
```text
medical-telegram-warehouse/
├── .github/workflows/    # CI/CD for automated testing
├── .vscode/              # Editor settings
├── api/                  # FastAPI application for data access
├── data/                 # Data Lake (Raw JSON & Images) - Not tracked in Git
├── medical_warehouse/    # dbt project (Models, Tests, Snapshots)
├── notebooks/            # Jupyter Notebooks for Scraping/YOLO prototyping
├── scripts/              # Executable scripts for individual pipeline tasks
├── src/                  # Source code (Scraper logic, Utils)
├── tests/                # Unit tests
├── .env                  # Environment variables (API Keys, DB Creds)
├── docker-compose.yml    # Database & Service orchestration
└── requirements.txt      # Python dependencies
```

## 🛠️ Getting Started

### Prerequisites
*   Python 3.10+
*   Docker & Docker Compose
*   Telegram API Credentials (obtain from `my.telegram.org`)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/nathanaeldereje/medical-telegram-warehouse.git
    cd medical-telegram-warehouse
    ```

2.  **Set up the environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a `.env` file in the root directory:
    ```ini
    TG_API_ID=123456
    TG_API_HASH=your_hash_here
    TG_PHONE=+251911223344
    DB_NAME=medical_warehouse
    DB_USER=postgres
    DB_PASSWORD=password
    DB_HOST=localhost
    ```

5.  **Start the Database**
    ```bash
    docker-compose up -d postgres
    ```

## 🔄 Recommended Workflow

### 1. Data Collection (Extract)
Run the scraper to populate the Data Lake (`data/raw`).
```bash
python scripts/scrape_data.py
```

### 2. Object Detection (Enrich)
Runs YOLOv8 on downloaded images to generate classification data (`yolo_results.csv`).
```bash
python scripts/detect_objects.py
```



### 3. Data Loading (Load)
Syncs both the JSON messages and the YOLO CSV results into PostgreSQL (`raw` schema).
```bash
python scripts/load_raw.py
```

### 4. Data Transformation (Transform)
Use dbt to clean data and build the Star Schema.

**Note for Windows Users:**
I have included a helper script to inject `.env` variables into the terminal for dbt.
```powershell
# 1. Set Environment Variables
./medical_warehouse/set-dbt-env.ps1

# 2. Run dbt
cd medical_warehouse
dbt debug --profiles-dir .       #(If you get "All checks passed", proceed. If not, check credentials).
dbt deps    # Install dependencies (dbt_utils)
dbt build   # Run models and tests
```



### 5. Serve Insights (API)
*Coming Soon:* Launch the FastAPI server to access the analytical endpoints.
```bash
uvicorn api.main:app --reload
```
*Access docs at: `http://localhost:8000/docs`*

## 🚀 Project Roadmap(As of Jan 18)

| Phase | Task Description | Status |
| :--- | :--- | :--- |
| **0. Setup** | Project Structure, Docker DB, Git Setup | ✅ Completed |
| **1. Scraping** | Extract text/images from Telegram channels | ✅ Completed |
| **2. Modeling** | Load data to Postgres & build Star Schema with dbt | ✅ Completed |
| **3. Enrichment** | Integrate YOLOv8 for image classification | ✅ Completed |
| **4. API** | Build FastAPI endpoints for analytics | 🚧 In Progress |
| **5. Orchestration** | Automate workflow with Dagster | ⏳ Pending |

## 📸 Dashboard / API Preview
*(Screenshots of dbt docs, API Swagger UI, and Dagster Graph will be added here upon completion)*

---
**Author:** Nathanael Dereje  
**Date:** January 2026