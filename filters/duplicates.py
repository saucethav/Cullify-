from PIL import Image
import imagehash
import os

def find_duplicates(folder_path, hash_func=imagehash.phash, threshold=5):
    """
    Finds duplicate or near-duplicate images in the folder.
    Returns a set of filenames that are considered duplicates.
    """
    seen_hashes = {}
    duplicates = set()

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(folder_path, filename)
        try:
            with Image.open(image_path) as img:
                img_hash = hash_func(img)

                # Check for similar existing hash
                for existing_hash, existing_file in seen_hashes.items():
                    if img_hash - existing_hash <= threshold:
                        print(f"{filename} is similar to {existing_file} (diff: {img_hash - existing_hash})")
                        duplicates.add(filename)
                        break
                else:
                    seen_hashes[img_hash] = filename
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    return duplicates
