# Crop Disease Detection Web Application

A comprehensive web application that detects diseases in crop leaves using machine learning, helping farmers identify plant diseases early and take preventive measures.

## 🌱 Features

- **Disease Detection**: Upload leaf images or take photos to identify crop diseases
- **Prevention Steps**: Get detailed prevention measures for identified diseases
- **Multilingual Support**: Available in English, Spanish, and Hindi
- **Feedback System**: Report incorrect predictions to improve the model
- **Crowdsourced Data**: Contribute labeled images to enhance the dataset
- **Community Insights**: View disease trends and statistics based on user submissions
- **Voice Assistance**: Listen to results through text-to-speech
- **Dark Mode**: Comfortable viewing experience in all lighting conditions
- **Mobile Friendly**: Responsive design works on all devices

## 🔧 Technologies Used

- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Backend**: Flask (Python)
- **Machine Learning**: TensorFlow, OpenCV
- **Database**: SQLite (with upgrade path to PostgreSQL)
- **Image Processing**: PIL, OpenCV

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip package manager
- Git (for version control)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/crop-disease-detection.git
   cd crop-disease-detection
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp web_app/.env.example web_app/.env
   # Edit .env file with your settings
   ```

5. Run the application:
   ```bash
   cd web_app
   python app.py
   ```

6. Access the application at `http://localhost:5000`

## 📊 Model Information

The application uses a deep learning model trained on thousands of images of healthy and diseased crop leaves. The model can currently detect:

- Potato: Early Blight, Late Blight, Healthy
- Tomato: Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Mosaic Virus, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Healthy

## 🌍 Deployment

For deployment instructions, see [deployment_guide.md](deployment_guide.md).

## 📱 Mobile Compatibility

The application is fully responsive and works on mobile devices. You can use your phone's camera to take photos directly for disease detection.

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [PlantVillage Dataset](https://plantvillage.psu.edu/) for the initial training data
- [TensorFlow](https://www.tensorflow.org/) for the machine learning framework
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Bootstrap](https://getbootstrap.com/) for the frontend design 