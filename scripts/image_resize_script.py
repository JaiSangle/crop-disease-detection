import os
from PIL import Image

# Define paths
dataset_dir = "E:/crop disease detection/dataset"  # Change if needed
save_separately = False  # Set to True if you want to save resized images in a new folder
new_dataset_dir = "E:/crop disease detection/resized_dataset"  # If saving separately
target_size = (224, 224)  # Resize all images to 224x224

def resize_images(directory, save_separately=False):
    """Resizes images in the given directory to the target size."""
    
    # Create new directory if saving separately
    if save_separately and not os.path.exists(new_dataset_dir):
        os.makedirs(new_dataset_dir)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):  # Process only images
                img_path = os.path.join(root, file)
                
                try:
                    # Open and resize image
                    img = Image.open(img_path)
                    img = img.resize(target_size)  # Fixed: Removed ANTIALIAS

                    # Save the image (overwrite or save separately)
                    if save_separately:
                        relative_path = os.path.relpath(root, directory)
                        save_path = os.path.join(new_dataset_dir, relative_path)

                        # Create subdirectories if they don’t exist
                        if not os.path.exists(save_path):
                            os.makedirs(save_path)

                        img.save(os.path.join(save_path, file))
                    else:
                        img.save(img_path)  # Overwrites the original image

                    print(f"Resized: {img_path}")

                except Exception as e:
                    print(f"Error processing {img_path}: {e}")

    print("✅ All images resized successfully!")

# Run the function
resize_images(dataset_dir, save_separately=save_separately)
