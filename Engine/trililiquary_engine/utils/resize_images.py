from PIL import Image
import os

# Path to the folder containing images
FOLDER_PATH = "templates/test_dataset"  # Change to your target path
TARGET_SIZE = (200, 100)  # (width, height)

def resize_all_images(folder):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(root, file)
                try:
                    img = Image.open(image_path)
                    resized = img.resize(TARGET_SIZE, Image.LANCZOS)
                    resized.save(image_path)
                    print(f"✅ Resized: {image_path}")
                except Exception as e:
                    print(f"❌ Failed to resize {image_path}: {e}")

if __name__ == "__main__":
    resize_all_images(FOLDER_PATH)
