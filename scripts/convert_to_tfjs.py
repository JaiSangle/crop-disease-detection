import tensorflow as tf
import os

def convert_model():
    # Create output directory
    output_dir = 'tfjs_model'
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the trained model
    print("Loading the trained model...")
    model = tf.keras.models.load_model('models/best_model.keras')
    
    # Save the model in SavedModel format
    print("Saving model in SavedModel format...")
    saved_model_path = os.path.join(output_dir, 'saved_model')
    tf.saved_model.save(model, saved_model_path)
    
    print(f"\nModel saved successfully at: {saved_model_path}")
    print("\nTo use this model in a web application, you have two options:")
    
    print("\nOption 1: Use TensorFlow Serving (for server-side inference):")
    print("1. Install TensorFlow Serving: https://www.tensorflow.org/tfx/guide/serving")
    print("2. Run the model server: tensorflow_model_server --rest_api_port=8501 --model_name=plant_disease --model_base_path=/path/to/saved_model")
    
    print("\nOption 2: Create a Flask/Django web application (recommended):")
    print("1. Create a web server that loads the SavedModel")
    print("2. Handle image uploads and preprocessing")
    print("3. Run inference on the server")
    print("4. Return results to the client")
    
    print("\nWould you like me to create a Flask web application to serve this model?")
    print("This would be the most straightforward way to deploy your model.")

if __name__ == "__main__":
    convert_model() 