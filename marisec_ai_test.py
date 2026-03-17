import os
import cv2
from datetime import datetime
from ultralytics import YOLO

# 1. Housekeeping
output_dir = "outputs"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. Setup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
save_filename = os.path.join(output_dir, f"detection_{timestamp}.jpg")

# 3. AI Logic
print("AI is thinking...")
model = YOLO('yolov8n.pt') 
results = model('ship.jpg', device='cuda')

# 4. DIAGNOSTICS: Let's see what it found
found_something = False
for r in results:
    # This prints the names of objects found (e.g., 'boat', 'person')
    names = r.names
    for box in r.boxes:
        label = names[int(box.cls[0])]
        conf = float(box.conf[0])
        print(f"Detected: {label} with {conf:.2f} confidence")
        found_something = True
    
    # 5. SAVE
    r.save(filename=save_filename)

if found_something:
    print(f"Success! Saved to: {save_filename}")
else:
    print("The AI didn't find any objects. Check if 'ship.jpg' is a clear photo!")
    