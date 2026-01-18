# src/yolo_detect.py
import torch
from ultralytics import YOLO
import pandas as pd
import os
from pathlib import Path


# --- PATCH START: Fix for PyTorch 2.6+ Security Error ---
# PyTorch 2.6 defaults to weights_only=True, which breaks standard YOLO loading.
# This hack forces torch.load to behave like the older version for this script.
_original_load = torch.load

def strict_load_bypass(*args, **kwargs):
    # If the caller didn't specify weights_only, force it to False
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)

torch.load = strict_load_bypass
# --- PATCH END ---


class ObjectDetector:
    def __init__(self, model_path='yolov8n.pt'):
        """
        Initialize YOLO model. 
        It will download 'yolov8n.pt' automatically if not present.
        """
        self.model = YOLO(model_path)
        
        # Define class IDs (COCO dataset standard indices)
        self.CLASS_PERSON = 0
        # Medical/Cosmetic container-like objects in COCO
        self.CLASS_BOTTLE = 39 
        self.CLASS_CUP = 41
        self.CLASS_BOWL = 45
        self.CLASS_HANDBAG = 26   # Boxes are often misidentified as handbags
        self.CLASS_V67 = 67       # Dining table (sometimes the box itself is seen as a surface)
        self.CLASS_BOOK = 73       # Rectangular boxes are very frequently seen as books
        
    def classify_image(self, detections):
        """
        Applies business logic to categorize the image based on detected objects.
        
        Logic:
        - Person + Product (bottle/cup) = 'promotional'
        - Product only = 'product_display'
        - Person only = 'lifestyle'
        - Neither = 'other'
        """
        has_person = self.CLASS_PERSON in detections
        product_candidates = [
        self.CLASS_BOTTLE, self.CLASS_CUP, self.CLASS_BOWL, 
        self.CLASS_HANDBAG, self.CLASS_BOOK
        ]
        has_product = any(cls in detections for cls in product_candidates)

        if has_person and has_product:
            return 'promotional'
        elif has_product and not has_person:
            return 'product_display'
        elif has_person and not has_product:
            return 'lifestyle'
        else:
            return 'other'

    def process_images(self, images_dir: str):
        """
        Scans the directory, runs inference, and returns a DataFrame of results.
        """
        records = []
        
        # Walk through the directory structure: data/raw/images/{channel}/{msg_id}.jpg
        image_files = []
        for root, _, files in os.walk(images_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_files.append(os.path.join(root, file))

        print(f"Found {len(image_files)} images to process...")

        # Process logic
        for img_path in image_files:
            try:
                # Extract metadata from path
                # Path is usually: .../channel_name/message_id.jpg
                path_obj = Path(img_path)
                message_id = path_obj.stem # filename without extension
                channel_name = path_obj.parent.name
                
                # Run Inference
                # conf=0.5 means we only count things the AI is 50% sure about
                results = self.model(img_path, verbose=False, conf=0.3)[0]
                
                # Extract detected class IDs
                detected_classes = results.boxes.cls.cpu().numpy().astype(int).tolist()
                
                # Get max confidence score (if any objects detected)
                conf_scores = results.boxes.conf.cpu().numpy()
                best_conf = float(conf_scores.max()) if len(conf_scores) > 0 else 0.0
                
                # Determine Category
                category = self.classify_image(detected_classes)
                
                records.append({
                    'message_id': message_id,
                    'channel_name': channel_name,
                    'image_path': img_path,
                    'detected_objects': str(detected_classes), # Store as string for CSV simplicity
                    'best_confidence': best_conf,
                    'image_category': category
                })
                
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                continue

        return pd.DataFrame(records)