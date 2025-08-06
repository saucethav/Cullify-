import cv2
import os
# Default threshold - Tweak for Accuracy
BLUR_THRESHOLD = 100.0

def is_blurry(image_path, threshold):
    image = cv2.imread(image_path)  # Load the image
    if image is None:
        return False  # Skip if image couldn't be read

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()  # Measure blurriness
    
    print(f"{os.path.basename(image_path)} sharpness: {laplacian_var:.2f}") # Score of the image
    
    return laplacian_var < threshold  # Return True if it's blurry
