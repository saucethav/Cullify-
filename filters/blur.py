import cv2
import os

# efault threshold for blur

BLUR_THRESHOLD = 100.0

def is_blurry(image_path, threshold = BLUR_THRESHOLD):
    """
    Checks if the image is blurry bosed on the Laplacian 
    
    Parameter: image_path (str): Path to the image file.
    threshold (float): Threshold value below which the image is considered blurry

    Returns:
        boolean: True if the image is deemed blurry, False otherwise.

    """

    # Load the image

    image = cv2.imread(image.path)
    if image is None:
        print(f"Warning: Unable to lead image {image_path}")
        return "image unreadable" \
        
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate the Laplacian variance (measure of sharpness)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    #Print sharpness score for debugging
    print(f"{os.path.basename(image_path)} sharpness: {laplacian_var:.2f}")

    # Compare against threshold
    return laplacian_var < threshold
