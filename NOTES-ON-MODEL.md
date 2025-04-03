# Notes on Model Deployment

The trained model file (`best_model.keras`) is necessary for the application to function but may be too large to include directly in the GitHub repository. Here are several options for handling the model file:

## Option 1: Git LFS (Recommended for GitHub)

Git Large File Storage (LFS) is designed for handling large files in Git repositories.

1. **Install Git LFS:**
   ```bash
   # For macOS
   brew install git-lfs
   
   # For Ubuntu/Debian
   sudo apt-get install git-lfs
   
   # For Windows (with Chocolatey)
   choco install git-lfs
   ```

2. **Setup in your repository:**
   ```bash
   git lfs install
   git lfs track "models/*.keras"
   git add .gitattributes
   ```

3. **Commit and push as normal:**
   ```bash
   git add models/best_model.keras
   git commit -m "Add model file with Git LFS"
   git push
   ```

## Option 2: Host the Model File Separately

If Git LFS is not an option, you can host the model file elsewhere and download it on application startup or deployment.

1. **Upload the model to a cloud storage service:**
   - Google Drive
   - Dropbox
   - AWS S3
   - Azure Blob Storage

2. **Add a download mechanism to your application:**
   
   Create a script that downloads the model on first startup:
   ```python
   # Example script for downloading from Google Drive
   import os
   import gdown
   
   MODEL_PATH = 'models/best_model.keras'
   
   if not os.path.exists(MODEL_PATH):
       print("Downloading model...")
       os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
       gdown.download('YOUR_GOOGLE_DRIVE_FILE_ID', MODEL_PATH, quiet=False)
   ```

3. **For Render deployment:**
   
   Uncomment the `preDeployCommand` section in `render.yaml` and update the URL to your hosted model file location.

## Option 3: Include Model in Repository (Not recommended for large models)

If your model is under 25MB, you can include it directly in your repository.

1. **Ensure `.gitignore` allows the model file:**
   Edit `.gitignore` and ensure there is no line excluding your model file.

2. **Add and commit the model:**
   ```bash
   git add models/best_model.keras
   git commit -m "Add model file"
   git push
   ```

## Option 4: Model Format Conversion

Convert your model to a smaller format if possible.

1. **Convert to TensorFlow Lite:**
   ```python
   import tensorflow as tf
   
   # Load your Keras model
   model = tf.keras.models.load_model('models/best_model.keras')
   
   # Convert to TFLite
   converter = tf.lite.TFLiteConverter.from_keras_model(model)
   tflite_model = converter.convert()
   
   # Save the TFLite model
   with open('models/model.tflite', 'wb') as f:
       f.write(tflite_model)
   ```

2. **Update your application to use the TFLite model.**

## Checking your model size

```bash
# Check the size of your model file
ls -lh models/best_model.keras
```

If the model is very large (>100MB), consider retraining a smaller version or using a more efficient architecture. 