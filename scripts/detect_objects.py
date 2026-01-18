# scripts/detect_objects.py
import sys
import os
import pandas as pd

# Add the project root to the python path so we can import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.yolo_detect import ObjectDetector

def main():
    # Define paths
    project_root = os.path.dirname(os.path.dirname(__file__))
    images_dir = os.path.join(project_root, 'data', 'raw', 'images')
    output_dir = os.path.join(project_root, 'data', 'processed')
    output_file = os.path.join(output_dir, 'yolo_results.csv')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print("--- Starting YOLO Object Detection ---")
    detector = ObjectDetector()
    
    # Run detection
    df = detector.process_images(images_dir)
    
    if not df.empty:
        print(f"\nDetection complete. Processed {len(df)} images.")
        print("Sample results:")
        print(df['image_category'].value_counts())
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"\nResults saved to: {output_file}")
    else:
        print("No images processed. Check your data/raw/images directory.")

if __name__ == "__main__":
    main()