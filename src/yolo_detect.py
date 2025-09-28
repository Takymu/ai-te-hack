import cv2
import numpy as np
from ultralytics import YOLO
import os

def detect_faces(image_bytes):
    current_dir = os.path.dirname(__file__)
    weights_path = os.path.abspath(os.path.join(current_dir, '..', 'yolov8x6_animeface.pt'))
    model = YOLO(weights_path)

    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    results = model(image_rgb, conf=0.5)
    coords = []
    
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                xyxy = box.xyxy[0].cpu().numpy()
                x_center = (xyxy[0] + xyxy[2]) / 2
                y_center = (xyxy[1] + xyxy[3]) / 2
                coords.append((x_center, y_center))
    
    return coords