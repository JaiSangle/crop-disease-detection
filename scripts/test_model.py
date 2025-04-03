import os
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
from PIL import Image

def load_model_and_mapping():
    """Load the trained model and class mapping"""
    model = tf.keras.models.load_model('models/best_model.keras')
    with open('models/class_mapping.json', 'r') as f:
        class_mapping = json.load(f)
    return model, class_mapping

def preprocess_image(img_path, target_size=(160, 160)):
    """Preprocess image for model input"""
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0  # Normalize
    return img_array

def predict_disease(model, img_array, class_mapping):
    """Make prediction and return top 3 results"""
    predictions = model.predict(img_array)
    top_3_indices = np.argsort(predictions[0])[-3:][::-1]
    top_3_probs = predictions[0][top_3_indices]
    
    results = []
    for idx, prob in zip(top_3_indices, top_3_probs):
        disease_name = class_mapping[str(idx)]
        results.append((disease_name, float(prob)))
    
    return results

def visualize_prediction(img_path, results):
    """Visualize the image with prediction results"""
    img = Image.open(img_path)
    plt.figure(figsize=(10, 5))
    
    # Plot image
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.axis('off')
    plt.title('Input Image')
    
    # Plot predictions
    plt.subplot(1, 2, 2)
    diseases = [r[0] for r in results]
    probs = [r[1] for r in results]
    plt.barh(diseases, probs)
    plt.xlabel('Probability')
    plt.title('Top 3 Predictions')
    plt.xlim(0, 1)
    
    plt.tight_layout()
    plt.savefig('models/prediction_result.png')
    plt.close()

def main():
    # Create results directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Load model and class mapping
    print("Loading model and class mapping...")
    model, class_mapping = load_model_and_mapping()
    
    # Get test image path from user
    test_image_path = input("Enter the path to the test image: ")
    
    if not os.path.exists(test_image_path):
        print(f"Error: File not found at {test_image_path}")
        return
    
    # Preprocess image
    print("Preprocessing image...")
    img_array = preprocess_image(test_image_path)
    
    # Make prediction
    print("Making prediction...")
    results = predict_disease(model, img_array, class_mapping)
    
    # Print results
    print("\nTop 3 Predictions:")
    for disease, prob in results:
        print(f"{disease}: {prob:.2%}")
    
    # Visualize results
    print("\nSaving visualization...")
    visualize_prediction(test_image_path, results)
    print("Results saved to models/prediction_result.png")

if __name__ == "__main__":
    main() 