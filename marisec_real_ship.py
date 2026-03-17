import cv2
import requests
import numpy as np

# A new, very reliable image URL (Unsplash is great for testing)
ship_url = "https://images.unsplash.com/photo-1544094112-9c970422df50?q=80&w=800"

# We add a 'Header' to pretend we are a standard web browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

print("Attempting to download ship image with Browser Headers...")

try:
    response = requests.get(ship_url, headers=headers, timeout=10)
    
    # Check if we actually got a '200 OK' response
    if response.status_code == 200:
        image_array = np.frombuffer(response.content, np.uint8)
        ship_image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if ship_image is not None:
            cv2.putText(ship_image, "MarisecAI: Real Ship Found", (20, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imwrite("real_ship_test.jpg", ship_image)
            print("Success! 'real_ship_test.jpg' is ready.")
        else:
            print("Error: Could not decode the data into an image.")
    else:
        print(f"Error: Website returned status code {response.status_code}")

except Exception as e:
    print(f"An error occurred: {e}")