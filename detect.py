#Prerequisites:
#
#Install OpenCV: pip install opencv-python
#
#Download these files and place them in the same directory:
#
#YOLOv3 weights: yolov3.weights  https://pjreddie.com/media/files/yolov3.weights
#
#YOLOv3 config: yolov3.cfg  https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg
# 
#COCO class names: coco.names  https://github.com/pjreddie/darknet/blob/master/data/coco.names

import cv2
import numpy as np

def count_objects(image_path, conf_threshold=0.5, nms_threshold=0.4):
    # Load YOLOv3 model
    try:
        net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    except Exception as e:
        print("Error loading YOLOv3 model:", e)
        return 0, 0

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]

    # Load image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found")
        return 0, 0

    height, width = image.shape[:2]

    # Create blob and perform forward pass
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Load COCO class names
    try:
        with open("coco.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        print("Error: coco.names file not found")
        return 0, 0

    # Process detections
    boxes = []
    confidences = []
    class_ids = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = detection[4] * scores[class_id]
            
            if confidence > conf_threshold:
                # Scale box coordinates to original image size
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                
                # Convert to top-left coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Apply non-maximum suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # Count objects
    person_count = 0
    bicycle_count = 0

    if len(indices) > 0:
        for i in indices.flatten():
            class_name = classes[class_ids[i]]
            if class_name == 'person':
                person_count += 1
            elif class_name == 'bicycle':
                bicycle_count += 1

    return person_count, bicycle_count

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python object_counter.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    people, bicycles = count_objects(image_path)
    print(f"Persons detected: {people}")
    print(f"Bicycles detected: {bicycles}")