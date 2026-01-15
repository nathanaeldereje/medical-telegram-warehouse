# 📓 Jupyter Notebooks & Experiments

This directory contains experimental code, Exploratory Data Analysis (EDA), and visual prototyping. These notebooks are used to develop logic before refactoring it into production scripts in `src/`.

## 📂 Contents

| Notebook | Task | Description |
| :--- | :--- | :--- |
| **`01_scraping_prototype.ipynb`** | **Task 1** | Testing Telegram API connection, channel entity extraction, and message format analysis. |
| **`02_yolo_inference.ipynb`** | **Task 3** | Prototyping YOLOv8 object detection on sample images and visualizing bounding boxes. |
| **`03_warehouse_analysis.ipynb`** | **Reporting** | Connecting to the Postgres warehouse to generate charts and insights for the final report. |

## ⚠️ Usage Note
These notebooks are for **development and analysis only**. 
For the production pipeline, please refer to the `scripts/` folder or the `dagster` pipeline definition.