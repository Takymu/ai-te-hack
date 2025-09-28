import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import json
from huggingface_hub import hf_hub_download

class AnimeFaceDetector:
    def __init__(self, model_path=None):
        """
        Инициализация детектора
        
        Args:
            model_path: путь к предобученной модели YOLO для лиц
                      если None, будет использована стандартная YOLOv8
        """
        # model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")

        # load model
        self.model = YOLO('/home/ilya/Documents/ai-te-hack/yolov8x6_animeface.pt')
    
    def detect_faces(self, image_path, conf_threshold=0.5):
        """
        Детекция лиц на изображении
        
        Args:
            image_path: путь к изображению
            conf_threshold: порог уверенности
            
        Returns:
            dict: результаты детекции с координатами боксов
        """
        # Загрузка и обработка изображения
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")
        
        # Конвертация BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Детекция с помощью YOLO
        results = self.model(image_rgb, conf=conf_threshold)
        
        # Извлечение результатов
        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Координаты бокса [x1, y1, x2, y2]
                    coords = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    
                    detection = {
                        'bbox': {
                            'x1': float(coords[0]),
                            'y1': float(coords[1]),
                            'x2': float(coords[2]),
                            'y2': float(coords[3])
                        },
                        'confidence': float(confidence),
                        'class': 'face'
                    }
                    detections.append(detection)
        
        return {
            'image_path': image_path,
            'detections': detections,
            'total_faces': len(detections)
        }
    
    def visualize_detections(self, image_path, output_path, detections=None):
        """
        Визуализация результатов детекции
        
        Args:
            image_path: путь к исходному изображению
            output_path: путь для сохранения результата
            detections: результаты детекции (если None, выполняется детекция)
        """
        if detections is None:
            detections = self.detect_faces(image_path)
        
        image = cv2.imread(image_path)
        
        for detection in detections['detections']:
            bbox = detection['bbox']
            confidence = detection['confidence']
            
            # Рисуем прямоугольник
            start_point = (int(bbox['x1']), int(bbox['y1']))
            end_point = (int(bbox['x2']), int(bbox['y2']))
            
            cv2.rectangle(image, start_point, end_point, (0, 255, 0), 2)
            
            # Добавляем текст с уверенностью
            text = f"Face: {confidence:.2f}"
            cv2.putText(image, text, 
                       (int(bbox['x1']), int(bbox['y1'])-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Сохраняем результат
        cv2.imwrite(output_path, image)
        print(f"Результат сохранен в: {output_path}")

def main():
    # Инициализация детектора
    detector = AnimeFaceDetector()
    
    # Путь к вашему изображению
    image_path = "/home/ilya/Documents/ai-te-hack/my_image_0.png"  # Замените на ваш путь
    
    try:
        # Детекция лиц
        results = detector.detect_faces(image_path, conf_threshold=0.5)
        
        # Вывод результатов
        print("=" * 50)
        print(f"РЕЗУЛЬТАТЫ ДЕТЕКЦИИ:")
        print(f"Изображение: {results['image_path']}")
        print(f"Найдено лиц: {results['total_faces']}")
        print("=" * 50)
        
        for i, detection in enumerate(results['detections'], 1):
            bbox = detection['bbox']
            confidence = detection['confidence']
            print(f"Лицо {i}:")
            print(f"  Координаты: ({bbox['x1']:.1f}, {bbox['y1']:.1f}) - ({bbox['x2']:.1f}, {bbox['y2']:.1f})")
            print(f"  Размер: {bbox['x2']-bbox['x1']:.1f}x{bbox['y2']-bbox['y1']:.1f}")
            print(f"  Уверенность: {confidence:.3f}")
            print("-" * 30)
        
        # Сохранение результатов в JSON
        with open('detection_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print("Результаты сохранены в detection_results.json")
        
        # Визуализация результатов
        detector.visualize_detections(image_path, "detection_result.jpg", results)
        
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()