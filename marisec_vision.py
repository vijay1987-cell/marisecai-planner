import cv2
import numpy as np

# 1. Create a blank "Ocean" (a 500x500 blue image)
# Colors are in BGR (Blue, Green, Red) - [255, 0, 0] is solid Blue
ocean = np.zeros((500, 500, 3), dtype="uint8")
ocean[:] = [255, 0, 0] 

# 2. Draw a white box (representing a ship)
# cv2.rectangle(image, top_left, bottom_right, color, thickness)
cv2.rectangle(ocean, (200, 200), (300, 300), (255, 255, 255), -1)

# 3. Add text labels
cv2.putText(ocean, "MarisecAI: Simulating Ship", (50, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

# 4. Save the image to your NVMe folder
filename = "simulated_ocean.jpg"
cv2.imwrite(filename, ocean)

print(f"Success! Image created and saved as: {filename}")