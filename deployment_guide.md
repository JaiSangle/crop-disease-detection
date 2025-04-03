# Deployment Guide for Crop Disease Detection Application

This guide provides instructions for deploying the Crop Disease Detection web application to various hosting platforms.

## Prerequisites

- Python 3.8+ installed
- pip package manager
- Git (for version control)
- TensorFlow model exported as .keras format
- Access to a hosting platform of your choice

## Application Structure

```
crop_disease_detection/
├── models/                 # Contains trained ML models
│   └── best_model.keras    # Main prediction model
├── web_app/                # Flask web application
│   ├── app.py              # Main application file
│   ├── static/             # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   ├── uploads/        # Uploaded images
│   │   └── contributions/  # User-contributed images
│   ├── templates/          # HTML templates
│   └── database/           # SQLite database
└── requirements.txt        # Python dependencies
```

## Deployment Options

### 1. Deploy on a VPS (DigitalOcean, AWS EC2, Google Compute Engine)

#### Server Setup

1. Create a new server instance with Ubuntu 20.04+
2. SSH into your server
3. Update the system:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
4. Install required packages:
   ```bash
   sudo apt install python3-pip python3-dev nginx git
   ```
5. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crop-disease-detection.git
   cd crop-disease-detection
   ```
6. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
7. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
8. Create necessary directories:
   ```bash
   mkdir -p web_app/static/uploads web_app/static/contributions web_app/database
   ```
9. Set appropriate permissions:
   ```bash
   chmod -R 755 web_app/static/uploads web_app/static/contributions web_app/database
   ```

#### Configure Gunicorn

1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```
2. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/crop-disease.service
   ```
3. Add the following content (adjust paths as needed):
   ```ini
   [Unit]
   Description=Gunicorn instance to serve Crop Disease Detection
   After=network.target

   [Service]
   User=ubuntu
   Group=www-data
   WorkingDirectory=/home/ubuntu/crop-disease-detection/web_app
   Environment="PATH=/home/ubuntu/crop-disease-detection/venv/bin"
   ExecStart=/home/ubuntu/crop-disease-detection/venv/bin/gunicorn --workers 3 --bind unix:crop-disease.sock -m 007 app:app

   [Install]
   WantedBy=multi-user.target
   ```
4. Start and enable the service:
   ```bash
   sudo systemctl start crop-disease
   sudo systemctl enable crop-disease
   ```

#### Configure Nginx

1. Create an Nginx config file:
   ```bash
   sudo nano /etc/nginx/sites-available/crop-disease
   ```
2. Add the following content:
   ```nginx
   server {
       listen 80;
       server_name your_domain.com www.your_domain.com;

       location / {
           include proxy_params;
           proxy_pass http://unix:/home/ubuntu/crop-disease-detection/web_app/crop-disease.sock;
       }

       location /static {
           alias /home/ubuntu/crop-disease-detection/web_app/static;
       }
   }
   ```
3. Enable the site:
   ```bash
   sudo ln -s /etc/nginx/sites-available/crop-disease /etc/nginx/sites-enabled
   ```
4. Test Nginx configuration:
   ```bash
   sudo nginx -t
   ```
5. Restart Nginx:
   ```bash
   sudo systemctl restart nginx
   ```

### 2. Deploy on Heroku

1. Install Heroku CLI
2. Create `Procfile` in the project root:
   ```
   web: gunicorn --chdir web_app app:app
   ```
3. Add runtime.txt:
   ```
   python-3.9.7
   ```
4. Update requirements.txt:
   ```
   Flask==2.0.1
   tensorflow==2.10.0
   gunicorn==20.1.0
   opencv-python-headless==4.5.3.56
   pillow==8.3.2
   ```
5. Initialize Git repository (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Heroku deployment"
   ```
6. Create Heroku app:
   ```bash
   heroku create crop-disease-detection-app
   ```
7. Deploy to Heroku:
   ```bash
   git push heroku main
   ```
8. Set up Heroku PostgreSQL (optional, for database):
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

### 3. Deploy on Google Cloud Platform with Docker

#### Create Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--chdir", "web_app", "--bind", "0.0.0.0:8080", "app:app"]
```

#### Create a .dockerignore file

```
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.git
.gitignore
.env
```

#### Deploy to Google Cloud Run

1. Build the Docker image:
   ```bash
   docker build -t crop-disease-detection .
   ```
2. Tag the image for Google Container Registry:
   ```bash
   docker tag crop-disease-detection gcr.io/your-project-id/crop-disease-detection
   ```
3. Push to Google Container Registry:
   ```bash
   docker push gcr.io/your-project-id/crop-disease-detection
   ```
4. Deploy to Cloud Run:
   ```bash
   gcloud run deploy crop-disease-detection --image gcr.io/your-project-id/crop-disease-detection --platform managed --region us-central1 --allow-unauthenticated
   ```

## Environment Configuration

For production, consider setting up environment variables:

1. Create a `.env` file in the web_app directory:
   ```
   FLASK_ENV=production
   FLASK_APP=app.py
   SECRET_KEY=your_secure_random_key
   DATABASE_URL=sqlite:///database/crop_disease.db
   ```

2. Update app.py to load environment variables:
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

## Database Configuration

The application uses SQLite by default, which is suitable for small to medium-scale deployments. For larger deployments, consider migrating to PostgreSQL:

1. Update app.py to use PostgreSQL:
   ```python
   import os
   import psycopg2
   
   # Database connection
   DATABASE_URL = os.environ['DATABASE_URL']
   
   def get_db_connection():
       conn = psycopg2.connect(DATABASE_URL)
       conn.autocommit = True
       return conn
   ```

## SSL Configuration

For production, enable HTTPS:

1. Obtain SSL certificates (Let's Encrypt is free):
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your_domain.com -d www.your_domain.com
   ```

2. Set up auto-renewal:
   ```bash
   sudo certbot renew --dry-run
   ```

## Monitoring and Maintenance

1. Set up application logging:
   ```python
   import logging
   logging.basicConfig(
       filename='app.log',
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

2. Set up regular backups for the database:
   ```bash
   # Add to crontab
   0 2 * * * sqlite3 /path/to/crop_disease.db ".backup /path/to/backups/crop_disease_$(date +\%Y\%m\%d).db"
   ```

3. Monitor application health with regular status checks

## Scaling Considerations

1. For high traffic, consider:
   - Increasing Gunicorn workers
   - Using a CDN for static assets
   - Implementing caching for prediction results
   - Optimizing the model for inference speed

2. For improved performance:
   - Convert TensorFlow model to TFLite or ONNX format
   - Consider using TensorFlow Serving for dedicated model serving

## Deployment Checklist

Before deploying to production, make sure to:

- [ ] Update all packages to secure versions
- [ ] Set DEBUG=False in Flask application
- [ ] Use a strong SECRET_KEY
- [ ] Set up proper error handling and logging
- [ ] Enable HTTPS
- [ ] Set up database backups
- [ ] Test the application thoroughly
- [ ] Set up monitoring and alerts
- [ ] Document API endpoints and usage

## Troubleshooting

Common issues and solutions:

1. **Application not starting**:
   - Check application logs
   - Verify permissions on directories and files
   - Ensure all dependencies are installed correctly

2. **Database connection issues**:
   - Check database credentials
   - Verify database service is running
   - Check for database file corruption

3. **Model loading errors**:
   - Verify model file path
   - Check model version compatibility
   - Ensure TensorFlow version matches the one used for training 