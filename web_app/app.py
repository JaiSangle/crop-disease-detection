import os
import numpy as np
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import tensorflow as tf
from PIL import Image, ImageEnhance
import json
import cv2
import uuid
import sqlite3
import datetime
from pathlib import Path
import logging
from dotenv import load_dotenv
import secrets

# Load environment variables from .env file if it exists
load_dotenv()

app = Flask(__name__)

# Configure from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # Default to 16MB
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'static/uploads')
app.config['PROCESSED_FOLDER'] = os.environ.get('PROCESSED_FOLDER', 'static/processed')
app.config['CONTRIBUTIONS_FOLDER'] = os.environ.get('CONTRIBUTIONS_FOLDER', 'static/contributions')
app.config['ALLOWED_EXTENSIONS'] = os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg').split(',')

# Get the absolute path to the parent directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'best_model.keras')
CLASS_MAPPING_PATH = os.path.join(BASE_DIR, 'models', 'class_mapping.json')

# Create directory for storing uploaded images
uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
contributions_dir = os.path.join(app.root_path, 'static', 'contributions')
db_path = os.path.join(app.root_path, 'database', 'crop_disease.db')

# Create directories if they don't exist
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(contributions_dir, exist_ok=True)
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT,
        prediction TEXT,
        confidence REAL,
        timestamp DATETIME,
        location_name TEXT,
        latitude REAL,
        longitude REAL
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction_id INTEGER,
        is_correct BOOLEAN,
        corrected_disease TEXT,
        timestamp DATETIME,
        FOREIGN KEY (prediction_id) REFERENCES predictions(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contributions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT,
        disease TEXT,
        contributor_ip TEXT,
        timestamp DATETIME,
        location_name TEXT,
        latitude REAL,
        longitude REAL,
        verified BOOLEAN DEFAULT 0
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Load the model and class mapping
print(f"Loading model from: {MODEL_PATH}")
model = tf.keras.models.load_model(MODEL_PATH)
print(f"Loading class mapping from: {CLASS_MAPPING_PATH}")
with open(CLASS_MAPPING_PATH, 'r') as f:
    class_mapping = json.load(f)

# Disease prevention information
disease_info = {
    "Potato__early_blight": {
        "prevention": {
            "en": [
            "Use disease-free seed potatoes",
            "Practice crop rotation",
            "Remove and destroy infected plants",
            "Apply fungicides preventively",
            "Maintain proper plant spacing"
            ],
            "es": [
                "Utilizar papas de siembra libres de enfermedades",
                "Practicar rotación de cultivos",
                "Eliminar y destruir plantas infectadas",
                "Aplicar fungicidas de manera preventiva",
                "Mantener un espaciado adecuado entre plantas"
            ],
            "hi": [
                "रोगमुक्त आलू के बीज का उपयोग करें",
                "फसल चक्र का अभ्यास करें",
                "संक्रमित पौधों को हटाएं और नष्ट करें",
                "निवारक रूप से फफूंदनाशक का प्रयोग करें",
                "उचित पौधों की दूरी बनाए रखें"
            ]
        },
        "name": {
            "en": "Potato Early Blight",
            "es": "Tizón Temprano de la Papa",
            "hi": "आलू का अगेती झुलसा"
        }
    },
    "Potato__late_blight": {
        "prevention": {
            "en": [
            "Plant resistant varieties",
            "Avoid overhead irrigation",
            "Remove infected plants immediately",
            "Apply fungicides before infection",
            "Harvest potatoes in dry weather"
            ],
            "es": [
                "Plantar variedades resistentes",
                "Evitar el riego por aspersión",
                "Eliminar plantas infectadas inmediatamente",
                "Aplicar fungicidas antes de la infección",
                "Cosechar papas en clima seco"
            ],
            "hi": [
                "प्रतिरोधी किस्मों को लगाएं",
                "ऊपरी सिंचाई से बचें",
                "संक्रमित पौधों को तुरंत हटा दें",
                "संक्रमण से पहले फफूंदनाशक लगाएं",
                "शुष्क मौसम में आलू की फसल काटें"
            ]
        },
        "name": {
            "en": "Potato Late Blight",
            "es": "Tizón Tardío de la Papa",
            "hi": "आलू का पछेती झुलसा"
        }
    },
    "Potato__healthy": {
        "prevention": {
            "en": [
            "Continue good cultural practices",
            "Monitor for early signs of disease",
            "Maintain proper soil moisture",
            "Use balanced fertilization",
            "Practice regular crop rotation"
            ],
            "es": [
                "Continuar con buenas prácticas de cultivo",
                "Monitorear por signos tempranos de enfermedad",
                "Mantener la humedad adecuada del suelo",
                "Usar fertilización equilibrada",
                "Practicar rotación regular de cultivos"
            ],
            "hi": [
                "अच्छी कृषि पद्धतियां जारी रखें",
                "रोग के शुरुआती लक्षणों की निगरानी करें",
                "मिट्टी की उचित नमी बनाए रखें",
                "संतुलित उर्वरक का उपयोग करें",
                "नियमित फसल चक्र का अभ्यास करें"
            ]
        },
        "name": {
            "en": "Healthy Potato Plant",
            "es": "Planta de Papa Sana",
            "hi": "स्वस्थ आलू का पौधा"
        }
    },
    "Tomato__bacterial_spot": {
        "prevention": {
            "en": [
            "Use disease-free seeds",
            "Avoid overhead watering",
            "Remove infected plants",
            "Practice crop rotation",
            "Apply copper-based fungicides"
            ],
            "es": [
                "Usar semillas libres de enfermedades",
                "Evitar el riego por encima",
                "Eliminar plantas infectadas",
                "Practicar rotación de cultivos",
                "Aplicar fungicidas a base de cobre"
            ],
            "hi": [
                "रोगमुक्त बीजों का उपयोग करें",
                "ऊपर से पानी देने से बचें",
                "संक्रमित पौधों को हटा दें",
                "फसल चक्र का अभ्यास करें",
                "तांबे-आधारित फफूंदनाशक लगाएं"
            ]
        },
        "name": {
            "en": "Tomato Bacterial Spot",
            "es": "Mancha Bacteriana del Tomate",
            "hi": "टमाटर का बैक्टीरियल स्पॉट"
        }
    },
    "Tomato__early_blight": {
        "prevention": {
            "en": [
            "Remove infected leaves",
            "Improve air circulation",
            "Water at the base of plants",
            "Apply fungicides preventively",
            "Practice crop rotation"
            ],
            "es": [
                "Eliminar hojas infectadas",
                "Mejorar la circulación de aire",
                "Regar en la base de las plantas",
                "Aplicar fungicidas preventivamente",
                "Practicar rotación de cultivos"
            ],
            "hi": [
                "संक्रमित पत्तियों को हटा दें",
                "हवा का संचार बेहतर करें",
                "पौधों के आधार पर पानी दें",
                "निवारक रूप से फफूंदनाशक लगाएं",
                "फसल चक्र का अभ्यास करें"
            ]
        },
        "name": {
            "en": "Tomato Early Blight",
            "es": "Tizón Temprano del Tomate",
            "hi": "टमाटर का अगेती झुलसा"
        }
    },
    "Tomato__late_blight": {
        "prevention": {
            "en": [
            "Plant resistant varieties",
            "Avoid overhead watering",
            "Remove infected plants",
            "Apply fungicides before infection",
            "Maintain proper plant spacing"
            ],
            "es": [
                "Plantar variedades resistentes",
                "Evitar el riego por encima",
                "Eliminar plantas infectadas",
                "Aplicar fungicidas antes de la infección",
                "Mantener un espaciado adecuado entre plantas"
            ],
            "hi": [
                "प्रतिरोधी किस्मों को लगाएं",
                "ऊपर से पानी देने से बचें",
                "संक्रमित पौधों को हटा दें",
                "संक्रमण से पहले फफूंदनाशक लगाएं",
                "उचित पौधों की दूरी बनाए रखें"
            ]
        },
        "name": {
            "en": "Tomato Late Blight",
            "es": "Tizón Tardío del Tomate",
            "hi": "टमाटर का पछेती झुलसा"
        }
    },
    "Tomato__leaf_mold": {
        "prevention": {
            "en": [
            "Improve air circulation",
            "Reduce humidity",
            "Water in the morning",
            "Remove infected leaves",
            "Use resistant varieties"
            ],
            "es": [
                "Mejorar la circulación de aire",
                "Reducir la humedad",
                "Regar por la mañana",
                "Eliminar hojas infectadas",
                "Usar variedades resistentes"
            ],
            "hi": [
                "हवा का संचार बेहतर करें",
                "नमी कम करें",
                "सुबह पानी दें",
                "संक्रमित पत्तियों को हटा दें",
                "प्रतिरोधी किस्मों का उपयोग करें"
            ]
        },
        "name": {
            "en": "Tomato Leaf Mold",
            "es": "Moho de la Hoja del Tomate",
            "hi": "टमाटर की पत्ती का फफूंद"
        }
    },
    "Tomato__mosaic_virus": {
        "prevention": {
            "en": [
            "Use disease-free seeds",
            "Control aphid populations",
            "Remove infected plants",
            "Disinfect tools regularly",
            "Practice crop rotation"
            ],
            "es": [
                "Usar semillas libres de enfermedades",
                "Controlar poblaciones de áfidos",
                "Eliminar plantas infectadas",
                "Desinfectar herramientas regularmente",
                "Practicar rotación de cultivos"
            ],
            "hi": [
                "रोगमुक्त बीजों का उपयोग करें",
                "एफिड आबादी को नियंत्रित करें",
                "संक्रमित पौधों को हटा दें",
                "उपकरणों को नियमित रूप से कीटाणुरहित करें",
                "फसल चक्र का अभ्यास करें"
            ]
        },
        "name": {
            "en": "Tomato Mosaic Virus",
            "es": "Virus del Mosaico del Tomate",
            "hi": "टमाटर का मोज़ेक वायरस"
        }
    },
    "Tomato__septoria_leaf_spot": {
        "prevention": {
            "en": [
            "Remove infected leaves",
            "Improve air circulation",
            "Water at the base of plants",
            "Apply fungicides preventively",
            "Practice crop rotation"
            ],
            "es": [
                "Eliminar hojas infectadas",
                "Mejorar la circulación de aire",
                "Regar en la base de las plantas",
                "Aplicar fungicidas preventivamente",
                "Practicar rotación de cultivos"
            ],
            "hi": [
                "संक्रमित पत्तियों को हटा दें",
                "हवा का संचार बेहतर करें",
                "पौधों के आधार पर पानी दें",
                "निवारक रूप से फफूंदनाशक लगाएं",
                "फसल चक्र का अभ्यास करें"
            ]
        },
        "name": {
            "en": "Tomato Septoria Leaf Spot",
            "es": "Mancha Foliar por Septoria en Tomate",
            "hi": "टमाटर का सेप्टोरिया लीफ स्पॉट"
        }
    },
    "Tomato__spider_mites_(two_spotted_spider_mite)": {
        "prevention": {
            "en": [
            "Maintain proper humidity",
            "Remove heavily infested leaves",
            "Use insecticidal soap",
            "Introduce natural predators",
            "Keep plants well-watered"
            ],
            "es": [
                "Mantener una humedad adecuada",
                "Eliminar hojas muy infestadas",
                "Usar jabón insecticida",
                "Introducir depredadores naturales",
                "Mantener las plantas bien regadas"
            ],
            "hi": [
                "उचित नमी बनाए रखें",
                "अत्यधिक संक्रमित पत्तियों को हटा दें",
                "कीटनाशक साबुन का उपयोग करें",
                "प्राकृतिक शिकारियों को परिचित कराएं",
                "पौधों को अच्छी तरह से पानी दें"
            ]
        },
        "name": {
            "en": "Tomato Spider Mites",
            "es": "Ácaros en Tomate",
            "hi": "टमाटर का स्पाइडर माइट्स"
        }
    },
    "Tomato__target_spot": {
        "prevention": {
            "en": [
            "Remove infected leaves",
            "Improve air circulation",
            "Water at the base of plants",
            "Apply fungicides preventively",
            "Practice crop rotation"
            ],
            "es": [
                "Eliminar hojas infectadas",
                "Mejorar la circulación de aire",
                "Regar en la base de las plantas",
                "Aplicar fungicidas preventivamente",
                "Practicar rotación de cultivos"
            ],
            "hi": [
                "संक्रमित पत्तियों को हटा दें",
                "हवा का संचार बेहतर करें",
                "पौधों के आधार पर पानी दें",
                "निवारक रूप से फफूंदनाशक लगाएं",
                "फसल चक्र का अभ्यास करें"
            ]
        },
        "name": {
            "en": "Tomato Target Spot",
            "es": "Mancha de Objetivo en Tomate",
            "hi": "टमाटर का टारगेट स्पॉट"
        }
    },
    "Tomato__yellow_leaf_curl_virus": {
        "prevention": {
            "en": [
            "Use resistant varieties",
            "Control whitefly populations",
            "Remove infected plants",
            "Use reflective mulches",
            "Practice crop rotation"
            ],
            "es": [
                "Usar variedades resistentes",
                "Controlar poblaciones de mosca blanca",
                "Eliminar plantas infectadas",
                "Usar mantillos reflectantes",
                "Practicar rotación de cultivos"
            ],
            "hi": [
                "प्रतिरोधी किस्मों का उपयोग करें",
                "सफेदमक्खी की आबादी को नियंत्रित करें",
                "संक्रमित पौधों को हटा दें",
                "परावर्तक मल्च का उपयोग करें",
                "फसल चक्र का अभ्यास करें"
            ]
        },
        "name": {
            "en": "Tomato Yellow Leaf Curl Virus",
            "es": "Virus del Rizado Amarillo del Tomate",
            "hi": "टमाटर का पीला पत्ता कर्ल वायरस"
        }
    },
    "Tomato__healthy": {
        "prevention": {
            "en": [
            "Continue good cultural practices",
            "Monitor for early signs of disease",
            "Maintain proper soil moisture",
            "Use balanced fertilization",
            "Practice regular crop rotation"
            ],
            "es": [
                "Continuar con buenas prácticas de cultivo",
                "Monitorear por signos tempranos de enfermedad",
                "Mantener la humedad adecuada del suelo",
                "Usar fertilización equilibrada",
                "Practicar rotación regular de cultivos"
            ],
            "hi": [
                "अच्छी कृषि पद्धतियां जारी रखें",
                "रोग के शुरुआती लक्षणों की निगरानी करें",
                "मिट्टी की उचित नमी बनाए रखें",
                "संतुलित उर्वरक का उपयोग करें",
                "नियमित फसल चक्र का अभ्यास करें"
            ]
        },
        "name": {
            "en": "Healthy Tomato Plant",
            "es": "Planta de Tomate Sana",
            "hi": "स्वस्थ टमाटर का पौधा"
        }
    }
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path, enhance_contrast=False, auto_crop=False):
    """Preprocess image with options for enhancement and cropping"""
    img = Image.open(image_path)
    
    # Create a processed image with a unique name
    processed_filename = f"processed_{uuid.uuid4().hex}.jpg"
    processed_path = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
    
    # Apply image processing techniques if requested
    if enhance_contrast or auto_crop:
        if enhance_contrast:
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)  # Increase contrast by 50%
            
            # Enhance brightness
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.2)  # Increase brightness by 20%
        
        if auto_crop:
            # Convert to OpenCV format for processing
            img_array = np.array(img)
            img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Threshold to get a binary image
            _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest contour (assuming it's the leaf)
                largest_contour = max(contours, key=cv2.contourArea)
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Add some padding
                padding = 20
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img_cv.shape[1] - x, w + 2 * padding)
                h = min(img_cv.shape[0] - y, h + 2 * padding)
                
                # Crop the image
                img_cv = img_cv[y:y+h, x:x+w]
                
                # Convert back to PIL Image
                img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))
        
        # Save the processed image
        img.save(processed_path)
        
        # Resize for model input
        img = img.resize((160, 160))
        img_array = np.array(img)
    else:
        # Just resize to model's expected input size
        img = img.resize((160, 160))
        img_array = np.array(img)
        
        # Save a copy of the resized image
        img.save(processed_path)
    
    # Normalize
    img_array = img_array / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    return img_array, processed_path

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    language = request.form.get('language', 'en')  # Default to English if not specified
    
    if file and allowed_file(file.filename):
        # Get processing options
        enhance_contrast = request.form.get('enhance_contrast', 'false').lower() == 'true'
        auto_crop = request.form.get('auto_crop', 'false').lower() == 'true'
        
        # Save the original file
        filename = secure_filename(file.filename)
        original_filename = f"original_{uuid.uuid4().hex}_{filename}"
        original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
        file.save(original_path)
        
        # Preprocess the image
        img_array, processed_path = preprocess_image(original_path, enhance_contrast, auto_crop)
        
        # Make prediction
        prediction = model.predict(img_array)
        
        # Get the top 3 predictions
        top_indices = np.argsort(prediction[0])[-3:][::-1]
        top_predictions = prediction[0][top_indices]
        
        # Map to class names and format results
        results = []
        for idx, confidence in zip(top_indices, top_predictions):
            class_idx = str(idx)
            if class_idx in class_mapping:
                class_name = class_mapping[class_idx]
                
                # Format disease info
                disease_data = {
                    'class': class_name,
                    'probability': float(confidence) * 100
                }
                
                # Add disease name and prevention steps in the requested language
                if class_name in disease_info:
                    disease_data['name'] = disease_info[class_name]['name'].get(language, disease_info[class_name]['name']['en'])
                    disease_data['prevention'] = disease_info[class_name]['prevention'].get(language, disease_info[class_name]['prevention']['en'])
                
                results.append(disease_data)
        
        # Check confidence level - convert numpy bool to Python bool
        low_confidence = bool(top_predictions[0] < 0.7)
        
        # Get paths to serve to client
        relative_image_path = f"/{app.config['UPLOAD_FOLDER']}/{original_filename}"
        relative_processed_path = f"/{app.config['PROCESSED_FOLDER']}/{os.path.basename(processed_path)}"
        
        # Store prediction in database
        store_prediction(results, relative_image_path, float(top_predictions[0]), request)
        
        # Return results
        return jsonify({
            'results': results,
            'low_confidence': low_confidence,
            'image_path': relative_image_path,
            'processed_image_path': relative_processed_path
        })
    
    return jsonify({'error': 'Invalid file type. Please upload an image (PNG, JPG, JPEG).'}), 400

# Store prediction in database
def store_prediction(prediction_result, image_path, confidence, request):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get location data if available
        location_name = request.form.get('location_name', None)
        latitude = request.form.get('latitude', None)
        longitude = request.form.get('longitude', None)
        
        # Insert prediction
        cursor.execute('''
            INSERT INTO predictions (
                image_path, prediction, confidence, timestamp, 
                location_name, latitude, longitude
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            image_path, 
            prediction_result[0]['class'], 
            confidence,
            datetime.datetime.now(),
            location_name,
            latitude,
            longitude
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error storing prediction: {e}")

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        # Get feedback data
        original_prediction = request.form.get('original_prediction')
        confidence = float(request.form.get('confidence'))
        is_correct = request.form.get('is_correct') == 'true'
        corrected_disease = request.form.get('corrected_disease')
        contribute_to_dataset = request.form.get('contribute_to_dataset') == 'true'
        
        # Location data
        location_name = request.form.get('location_name')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        
        # Get the image file if contributing to dataset
        image_file = None
        image_path = None
        if contribute_to_dataset and 'image' in request.files:
            image_file = request.files['image']
            
            # Generate a unique filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"contribution_{timestamp}_{corrected_disease}.jpg"
            image_path = os.path.join(contributions_dir, filename)
            
            # Save the image
            image_file.save(image_path)
        
        # Store feedback in database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get the latest prediction for this disease
        cursor.execute('''
            SELECT id FROM predictions 
            WHERE prediction = ? 
            ORDER BY timestamp DESC LIMIT 1
        ''', (original_prediction,))
        
        prediction_id = cursor.fetchone()
        
        if prediction_id:
            # Insert feedback
            cursor.execute('''
                INSERT INTO feedback (
                    prediction_id, is_correct, corrected_disease, timestamp
                ) VALUES (?, ?, ?, ?)
            ''', (
                prediction_id[0],
                is_correct,
                corrected_disease if not is_correct else None,
                datetime.datetime.now()
            ))
        
        # If contributing to dataset, store contribution
        if contribute_to_dataset and image_path:
            cursor.execute('''
                INSERT INTO contributions (
                    image_path, disease, contributor_ip, timestamp,
                    location_name, latitude, longitude
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                image_path,
                corrected_disease,
                request.remote_addr,
                datetime.datetime.now(),
                location_name,
                latitude,
                longitude
            ))
        
        conn.commit()
        
        # Generate insights to return
        insights = generate_insights(cursor)
        
        conn.close()
        
        # Return success response with insights
        return jsonify({
            'success': True,
            'message': 'Feedback submitted successfully',
            'insights': insights
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error submitting feedback: {str(e)}'
        })

# Generate insights from the database
def generate_insights(cursor):
    try:
        insights = {}
        
        # Get region diseases (most common diseases in the user's region)
        cursor.execute('''
            SELECT prediction, COUNT(*) as count
            FROM predictions
            GROUP BY prediction
            ORDER BY count DESC
            LIMIT 10
        ''')
        
        region_diseases = []
        for row in cursor.fetchall():
            disease, count = row
            region_diseases.append({
                'name': disease,
                'count': count
            })
        
        insights['regionDiseases'] = region_diseases
        
        # Get seasonal trends
        # Get current month
        current_month = datetime.datetime.now().month
        
        # Define seasons
        if 3 <= current_month <= 5:
            season = 'Spring'
        elif 6 <= current_month <= 8:
            season = 'Summer'
        elif 9 <= current_month <= 11:
            season = 'Fall'
        else:
            season = 'Winter'
        
        # Get counts by season (simplified - just use current season)
        cursor.execute('''
            SELECT prediction, COUNT(*) as count
            FROM predictions
            GROUP BY prediction
            ORDER BY count DESC
            LIMIT 5
        ''')
        
        seasonal_trends = []
        for row in cursor.fetchall():
            disease, count = row
            seasonal_trends.append({
                'season': season,
                'disease': disease,
                'count': count
            })
        
        insights['seasonalTrends'] = seasonal_trends
        
        # Get recent community submissions
        cursor.execute('''
            SELECT c.disease, c.image_path, c.timestamp, c.location_name
            FROM contributions c
            WHERE c.verified = 1
            ORDER BY c.timestamp DESC
            LIMIT 5
        ''')
        
        recent_submissions = []
        for row in cursor.fetchall():
            disease, image_path, timestamp, location = row
            
            # Create a relative path for the image
            if image_path:
                image_path = image_path.replace(app.root_path, '')
                if image_path.startswith('/'):
                    image_path = image_path[1:]
                image_path = '/' + image_path
            
            recent_submissions.append({
                'disease': disease,
                'thumbnail': image_path,
                'timestamp': timestamp,
                'location': location
            })
        
        insights['recentSubmissions'] = recent_submissions
        
        return insights
    
    except Exception as e:
        print(f"Error generating insights: {e}")
        return {
            'regionDiseases': [],
            'seasonalTrends': [],
            'recentSubmissions': []
        }

if __name__ == '__main__':
    # Create upload and processed folders if they don't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    
    # Run the app
    app.run(debug=True) 