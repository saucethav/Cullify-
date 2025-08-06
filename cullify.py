#Import libraries
import cv2
import os
import mediapipe as mp
import numpy as np
import zipfile
from datetime import datetime

#Import custom filters
from filters.blur import is_blurry
from filters.eyes import eyes_closed
from filters.duplicates import find_duplicates

# Thresholds for filters
BLUR_THRESHOLD = 100.0
EYES_THRESHOLD = 0.2

# Label input/output folders
input_folder = "images"
output_good = "filtered"
output_bad = "bad"

# Make sure the folders exist
os.makedirs(output_good, exist_ok = True)
os.makedirs(output_bad, exist_ok = True)

#Main Method
def process_images():
    total = 0
    blurry_count = 0
    closed_eyes_count = 0
    duplicate_count = 0
    good_count = 0

    blurry_files = []
    closed_eye_files = []
    duplicate_files = []
    good_files = []


    # Detect duplicates first
    duplicates = find_duplicates(input_folder)
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        total += 1
        file_path = os.path.join(input_folder, filename)
        is_duplicate = filename in duplicates
        is_blur = is_blurry(file_path, threshold=BLUR_THRESHOLD)
        has_closed_eyes = eyes_closed(file_path, eye_threshold=EYES_THRESHOLD)

        if is_duplicate:
            duplicate_count += 1
            duplicate_files.append(filename)
        if is_blur:
            blurry_count += 1
            blurry_files.append(filename)
        if has_closed_eyes:
            closed_eyes_count += 1
            closed_eye_files.append(filename)

        if is_duplicate or is_blur or has_closed_eyes:
            target_path = os.path.join(output_bad, filename)
        else:
            good_count += 1
            good_files.append(filename)
            target_path = os.path.join(output_good, filename)

        cv2.imwrite(target_path, cv2.imread(file_path))
        print(f"Processed: {filename}")

    # Print summary
    summary = (
        f"Cullify Summary:\n"
        f"----------------\n"
        f"Total images: {total}\n"
        f"Blurry: {blurry_count} → {', '.join(blurry_files) or 'None'}\n"
        f"Eyes closed: {closed_eyes_count} → {', '.join(closed_eye_files) or 'None'}\n"
        f"Duplicates: {duplicate_count} → {', '.join(duplicate_files) or 'None'}\n"
        f"Filtered (good): {good_count} → {', '.join(good_files) or 'None'}\n"
    )


    print("\n" + summary)

    with open("summary.txt", "w") as f:
        f.write(summary)

    # Makes a zip file of the filtered images with timestamps
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_filename = f"Cullify_Filtered_{timestamp}.zip"

    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(output_good):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_good)  # preserve folder structure inside zip
                zipf.write(file_path, arcname)

    print(f"\nExported good photos to: {zip_filename}")

    



# Run when the script is executed
if __name__ == "__main__":
    process_images()
