from flask import Flask, render_template, request, Response
import cv2
import os
import requests
from playsound import playsound
import threading
import time
import json
import requests
import tensorflow as tf
from PIL import Image
import torch
import numpy as np
from torchvision.ops import nms

app = Flask(__name__)
camera = cv2.VideoCapture(0)

inference_endpoint       = 'https://navai-navai.apps.cluster-q7hm2.q7hm2.sandbox2524.opentlc.com/v2/models/navai/infer'
inference_endpoint_token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IkoxTFFrUTFkRFB6OVpGakE4SEhrLXk0aUUxcGYzVm9YdWtVSmo1SHhCdUkifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJuYXZhaSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJuYXZhaS1uYXZhaS1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJuYXZhaS1zYSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImNkMjIzYjY0LTZlYjMtNGY0My05NDg0LTg4YWVmNTdiZjQ2OSIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpuYXZhaTpuYXZhaS1zYSJ9.0UquI0Hp0GFtYa_W-Xm-fGYRcA2rmhnnueulXKuEmYSzVrHgVk9X212SJtRhhQMAva3nOUGCL0Bzu7Z4GkB3nae8Gvfg2VapY-atx_wlY6Jmpxyptx_dWhhqpLkf-b-U9cayehfXY3d-Pm0VJdv_Udb9uXe7zffNU1tiz21kot4aGB_0K0d1V8YSoPEjKCbd3VO6uXGTkMZQ0J09fFJ_CC-f2cA4-psFcsrqYnnNxBNWowyF-obNzhaewTriDp20oefix6_YRWu91-S67jlAOjGWWNvk_gbCK4WeFU2xL4Ng_tVU0iKmATyvxAyK3EJYl0av5x9J85UV3SqKKrYslR2RFgPkMrk7J1Z_az2PV-YatXBl7LQIP6DUwJKs8uyTbVLCwIobxf5OXM5nM_gJc6exjUGTYGKdXSFLBVIn1amzL6b76hiy4Ot4fSi8OXirSFKrnaP1MmRfD4exzVICyaaEbUMH6iG5LFo7GLn0rPLcq7acMI8m0Ryhg9JidcGp99syPyzIiiP6ycEh27y37aCf9QQrHkeDpkfH0Is6vwQdPVdKOnuaJjNKul2RjoNt9Cw21sjBFJB8kdiQfu3Pnjf5Or0NO4jEQyoInc_g5H6pSu5O4DypN0QoA530MNxelcKqFwacpGhHrsGJVQ-98yhemrrvEzJd02JexEtdr9w'

# Function to capture image
def capture_image():
    while True:
        ret, frame = camera.read()
        if ret:
            #_, buffer = cv2.imencode('.jpg', frame)

            #with open("what-is-seen.jpg", "wb") as file:
            #    file.write(buffer.tobytes())

            img = cv2.imread('./18-bueiro_original.jpg')
            send_image(img)
        time.sleep(3)

# Function to send the image via HTTP request and handle response
def send_image(image):
    try:
        final_boxes_scores = run_inference(image)
        
        for box, score in final_boxes_scores:
            #x_min, y_min, x_max, y_max = map(int, box)
            print(f"Confidence: {score:.2f}")

            print(score)

            if score > 0.9:
                playsound('car-horn-beep.mp3')
    except Exception as e:
        print(f"Error sending image: {e}")

def run_inference(image):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert to RGB
    img = cv2.resize(img, (640, 640))  # Resize to the model's expected size
    img = img.astype(np.float32) / 255.0  # Normalize to [0, 1]
    img = img.transpose(2, 0, 1)  # HWC to CHW format
    img = np.expand_dims(img, axis=0)

    headers = {
        'Content-Type'  : 'application/json',
        'Authorization' : f'Bearer { inference_endpoint_token }'
    }

    payload = json.dumps({
        'inputs' : [
            {
                "name"     : "images",
                "datatype" : "FP32",
                "data"     : img.flatten().tolist(),
                "shape"    : list(img.shape)
            }
        ]
    })

    response = requests.post(url = inference_endpoint, headers = headers, data = payload)
    
    response_data = response.json()

    #print(response_data)
    
    output_data = response_data['outputs'][0]['data']  # Flattened array containing predictions
    output_shape = response_data['outputs'][0]['shape']
    
    # Reshape the flattened output to [1, 5, 8400]
    reshaped_output = np.array(output_data).reshape(output_shape)

    # Extract bounding box attributes
    x_centers = reshaped_output[0, 0, :]
    y_centers = reshaped_output[0, 1, :]
    widths = reshaped_output[0, 2, :]
    heights = reshaped_output[0, 3, :]
    # Extract the confidence scores (5th attribute)
    confidence_scores = reshaped_output[0, 4, :]  # Shape: (8400,)

    # Convert to [x_min, y_min, x_max, y_max] format
    image_height, image_width = 640, 640
    x_mins = (x_centers - widths / 2) * image_width
    y_mins = (y_centers - heights / 2) * image_height
    x_maxs = (x_centers + widths / 2) * image_width
    y_maxs = (y_centers + heights / 2) * image_height
    
    bounding_boxes = np.stack([x_mins, y_mins, x_maxs, y_maxs], axis=1)
    
    # Apply confidence threshold
    confidence_threshold = 0.25
    conf_mask = confidence_scores > confidence_threshold
    filtered_boxes = bounding_boxes[conf_mask]
    filtered_scores = confidence_scores[conf_mask]
    
    # print(filtered_scores)

    # Apply Non-Maximum Suppression (NMS)
    iou_threshold = 0.5
    nms_indices = apply_nms(filtered_boxes, filtered_scores, iou_threshold)
    
    final_boxes = filtered_boxes[nms_indices]
    final_scores = filtered_scores[nms_indices]

    # Visualize the results
    return zip(final_boxes, final_scores)

def apply_nms(boxes, scores, iou_threshold=0.5):
    """
    Applies Non-Maximum Suppression (NMS) to filter out redundant boxes.

    Args:
        boxes (numpy.ndarray): Bounding boxes, shape (N, 4), format [x_min, y_min, x_max, y_max].
        scores (numpy.ndarray): Confidence scores for each box, shape (N,).
        iou_threshold (float): IoU threshold for NMS. Defaults to 0.5.

    Returns:
        numpy.ndarray: Indices of the remaining boxes after NMS.
    """
    boxes_tensor = torch.tensor(boxes, dtype=torch.float32)
    scores_tensor = torch.tensor(scores, dtype=torch.float32)
    keep_indices = nms(boxes_tensor, scores_tensor, iou_threshold)
    return keep_indices.numpy()

#########################################################################################################3

@app.route('/')
def index():
    return render_template('index.html')

# Start the image capture thread
threading.Thread(target=capture_image, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
