# Feedback System & Data Collection Documentation

## Overview

The Crop Disease Detection application now includes a comprehensive feedback system that allows users to report incorrect classifications and contribute labeled images to improve the model's performance. This system serves multiple purposes:

1. **Model Improvement**: Collecting feedback on prediction accuracy helps identify areas where the model needs improvement.
2. **Dataset Enrichment**: User-contributed images expand the training dataset with real-world examples.
3. **Community Insights**: Aggregated data provides valuable trends and insights about crop diseases across different regions and seasons.

## Features

### 1. Feedback System

After receiving a prediction, users can indicate whether the prediction is correct or incorrect:

- **Correct Prediction**: Simple confirmation that improves confidence metrics
- **Incorrect Prediction**: 
  - Users select the correct disease from a dropdown
  - Option to contribute the image to improve the dataset
  - All feedback is stored for model evaluation

### 2. Crowdsourced Data Collection

- Users can contribute labeled images when reporting incorrect predictions
- Contributed images are stored separately from standard uploads
- All contributions include:
  - The image itself
  - Correct disease classification
  - Timestamp
  - Location data (if permitted by the user)
  - Contributor's IP address (for management purposes)

### 3. Database Storage

All data is stored in a SQLite database with the following tables:

- **predictions**: Stores all disease predictions made by the model
  - Image path
  - Predicted disease
  - Confidence level
  - Timestamp
  - Location data (if available)

- **feedback**: Records user feedback on predictions
  - Reference to the prediction
  - Whether the prediction was correct
  - Corrected disease (if applicable)
  - Timestamp

- **contributions**: Stores user-contributed images
  - Image path
  - Correct disease
  - Contributor information
  - Timestamp
  - Location data
  - Verification status

### 4. Disease Trends & Insights

The application generates insights based on the collected data:

- **Regional Disease Prevalence**: Shows the most common diseases in the user's geographic region
- **Seasonal Trends**: Displays disease occurrence patterns based on seasons
- **Recent Community Submissions**: Showcases recently contributed images from the community

## Technical Implementation

### Feedback Collection

1. User provides feedback via the UI ("Correct" or "Incorrect" buttons)
2. For incorrect predictions, a form allows users to select the correct disease
3. The feedback is sent to the `/feedback` endpoint
4. Data is stored in the database

### Data Storage

- Images are stored in separate directories:
  - `static/uploads/`: Regular prediction uploads
  - `static/contributions/`: User-contributed images
  
- Database location: `database/crop_disease.db`

### Insights Generation

- Insights are generated dynamically based on collected data
- Charts display aggregated statistics about disease occurrence
- Location data enables regional analysis

## Privacy Considerations

- User location is only collected with explicit permission
- Contributions are anonymized in public displays
- IP addresses are stored only for administrative purposes
- Users can contribute images without sharing location data

## Future Enhancements

- Automated verification of user contributions
- More sophisticated regional analysis with heat maps
- Seasonal prediction adjustments based on historical data
- User authentication system for contribution tracking
- Expanded analytics with crop-specific insights 