document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const uploadForm = document.getElementById('upload-form');
    const imageUpload = document.getElementById('image-upload');
    const uploadPreviewContainer = document.getElementById('upload-preview-container');
    const uploadThumbnail = document.getElementById('upload-thumbnail');
    const fileName = document.getElementById('file-name');
    const zoomBtn = document.getElementById('zoom-btn');
    const removeImageBtn = document.getElementById('remove-image-btn');
    const zoomedImage = document.getElementById('zoomed-image');
    
    const previewImage = document.getElementById('preview-image');
    const resultContainer = document.getElementById('result-container');
    const lowConfidenceWarning = document.getElementById('low-confidence-warning');
    const errorMessage = document.getElementById('error-message');
    const loading = document.getElementById('loading');
    const processingOptions = document.getElementById('processing-options');
    
    // Feedback elements
    const correctPredictionBtn = document.getElementById('correct-prediction-btn');
    const incorrectPredictionBtn = document.getElementById('incorrect-prediction-btn');
    const correctionForm = document.getElementById('correction-form');
    const correctDiseaseSelect = document.getElementById('correct-disease');
    const contributeToDatasetCheckbox = document.getElementById('contribute-to-dataset');
    const submitCorrectionBtn = document.getElementById('submit-correction-btn');
    const feedbackSuccess = document.getElementById('feedback-success');
    
    // Insights elements
    const insightsContainer = document.getElementById('insights-container');
    const regionDiseasesChart = document.getElementById('region-diseases-chart');
    const seasonalTrendsChart = document.getElementById('seasonal-trends-chart');
    const recentSubmissions = document.getElementById('recent-submissions');
    
    // Theme toggle
    const themeToggle = document.getElementById('theme-toggle');
    
    // Camera elements
    const cameraTab = document.getElementById('camera-tab');
    const cameraStream = document.getElementById('camera-stream');
    const cameraSwitchBtn = document.getElementById('camera-switch-btn');
    const cameraCaptureBtn = document.getElementById('camera-capture-btn');
    const capturedImage = document.getElementById('captured-image');
    const previewContainer = document.querySelector('.preview-container');
    const retakeBtn = document.getElementById('retake-btn');
    const cameraPredictBtn = document.getElementById('camera-predict-btn');
    
    // Image processing options
    const enhanceContrastCheckbox = document.getElementById('enhance-contrast');
    const autoCropCheckbox = document.getElementById('auto-crop');
    
    // Language and voice elements
    const languageSelect = document.getElementById('language-select');
    const speakResultsBtn = document.getElementById('speak-results-btn');
    
    // Initialize Bootstrap modal
    const zoomModal = new bootstrap.Modal(document.getElementById('image-zoom-modal'));
    
    // Current language and speech synthesis variables
    let currentLanguage = 'en';
    let isSpeaking = false;
    const speechSynthesis = window.speechSynthesis;
    
    // User data for insights
    let userLocation = null;
    let isLoadingLocation = false;
    
    // Initialize language
    initializeLanguage();
    
    // Initialize theme
    initializeTheme();
    
    // Try to get user's location for insights
    initializeUserLocation();
    
    // Camera variables
    let stream = null;
    let facingMode = 'environment'; // Start with rear camera
    let availableCameras = [];
    
    // Current prediction results
    let currentResults = null;
    
    // Current selected file
    let selectedFile = null;

    // Initialize feedback system
    initializeFeedbackSystem();

    // Language change handler
    languageSelect.addEventListener('change', function() {
        currentLanguage = this.value;
        updatePageLanguage();
        // If results are displayed, update them with the new language
        if (currentResults) {
            updateResultsUI(currentResults);
        }
    });
    
    // Initialize language settings
    function initializeLanguage() {
        // Check for saved language preference
        const savedLanguage = localStorage.getItem('preferredLanguage');
        if (savedLanguage) {
            currentLanguage = savedLanguage;
            languageSelect.value = currentLanguage;
        }
        
        // Apply initial language
        updatePageLanguage();
        
        // Save language preference when changed
        languageSelect.addEventListener('change', function() {
            localStorage.setItem('preferredLanguage', this.value);
        });
    }
    
    // Update all text elements on the page with the current language
    function updatePageLanguage() {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[currentLanguage] && translations[currentLanguage][key]) {
                // If it's a form element like input, textarea, etc.
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.value = translations[currentLanguage][key];
                    element.placeholder = translations[currentLanguage][key];
                } 
                // If it's a heading element
                else if (element.tagName.match(/^H[1-6]$/)) {
                    element.innerText = translations[currentLanguage][key];
                }
                // Otherwise, assume it's a regular element with innerHTML
                else {
                    element.innerText = translations[currentLanguage][key];
                }
            }
        });
    }
    
    // Text-to-speech functionality
    speakResultsBtn.addEventListener('click', function() {
        if (isSpeaking) {
            stopSpeaking();
        } else {
            speakResults();
        }
    });
    
    function speakResults() {
        if (!currentResults || !currentResults.results || currentResults.results.length === 0) {
            return;
        }
        
        // Stop any existing speech
        stopSpeaking();
        
        // Create the spoken text
        const result = currentResults.results[0];
        let text = '';
        
        // Add the disease name
        if (result.name) {
            text += result.name + '. ';
        } else {
            text += result.class + '. ';
        }
        
        // Add confidence level
        text += translations[currentLanguage]['predictionResult'] + ': ' + 
                Math.round(result.probability) + '%. ';
        
        // Add prevention steps
        if (result.prevention && result.prevention.length > 0) {
            text += translations[currentLanguage]['preventionSteps'] + ': ';
            result.prevention.forEach((step, index) => {
                text += (index + 1) + '. ' + step + '. ';
            });
        }
        
        // Create speech utterance
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set language
        switch(currentLanguage) {
            case 'es':
                utterance.lang = 'es-ES';
                break;
            case 'hi':
                utterance.lang = 'hi-IN';
                break;
            default:
                utterance.lang = 'en-US';
        }
        
        // Update button text and state
        isSpeaking = true;
        speakResultsBtn.innerHTML = `<i class="fas fa-volume-mute"></i> <span>${translations[currentLanguage]['stopSpeaking']}</span>`;
        
        // Handle speech end
        utterance.onend = function() {
            isSpeaking = false;
            speakResultsBtn.innerHTML = `<i class="fas fa-volume-up"></i> <span>${translations[currentLanguage]['speakResults']}</span>`;
        };
        
        // Start speaking
        speechSynthesis.speak(utterance);
    }
    
    function stopSpeaking() {
        if (speechSynthesis) {
            speechSynthesis.cancel();
            isSpeaking = false;
            speakResultsBtn.innerHTML = `<i class="fas fa-volume-up"></i> <span>${translations[currentLanguage]['speakResults']}</span>`;
        }
    }

    // Handle file selection via input
    imageUpload.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFiles(e.target.files[0]);
        }
    });

    // Process selected file
    function handleFiles(file) {
        if (!file || !file.type.match('image.*')) {
            showError(translations[currentLanguage]['selectImage']);
            return;
        }
        
        selectedFile = file;
        
        // Display thumbnail preview
            const reader = new FileReader();
            reader.onload = function(e) {
            // Set thumbnail image
            uploadThumbnail.src = e.target.result;
            // Also set preview image for later use
                previewImage.src = e.target.result;
            
            // Show thumbnail container
            uploadPreviewContainer.classList.remove('d-none');
            
            // Set file name
            fileName.textContent = file.name;
            
            // Show processing options
                resultContainer.classList.add('d-none');
                errorMessage.classList.add('d-none');
                processingOptions.classList.remove('d-none');
            
            // Add animation
            uploadThumbnail.classList.add('animate-pulse');
            setTimeout(() => {
                uploadThumbnail.classList.remove('animate-pulse');
            }, 500);
            };
            reader.readAsDataURL(file);
    }

    // Remove selected image
    removeImageBtn.addEventListener('click', function() {
        resetUploadArea();
    });

    function resetUploadArea() {
        // Clear file input
        imageUpload.value = '';
        selectedFile = null;
        
        // Reset UI
        uploadPreviewContainer.classList.add('d-none');
        processingOptions.classList.add('d-none');
    }
    
    // Zoom functionality
    zoomBtn.addEventListener('click', function() {
        if (uploadThumbnail.src) {
            zoomedImage.src = uploadThumbnail.src;
            zoomModal.show();
        }
    });

    // Handle file upload form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!selectedFile) {
            showError(translations[currentLanguage]['selectImage']);
            return;
        }

        // Get processing options
        const enhanceContrast = enhanceContrastCheckbox.checked;
        const autoCrop = autoCropCheckbox.checked;

        // Create form data
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('enhance_contrast', enhanceContrast);
        formData.append('auto_crop', autoCrop);
        formData.append('language', currentLanguage);

        // Submit the image for prediction
        submitImageForPrediction(formData);
    });

    // Initialize camera when the camera tab is clicked
    cameraTab.addEventListener('click', initializeCamera);

    // Switch camera button functionality
    cameraSwitchBtn.addEventListener('click', switchCamera);

    // Capture button functionality
    cameraCaptureBtn.addEventListener('click', captureImage);

    // Retake button functionality
    retakeBtn.addEventListener('click', function() {
        previewContainer.classList.add('d-none');
        cameraCaptureBtn.disabled = false;
        cameraSwitchBtn.disabled = false;
    });

    // Predict from captured image
    cameraPredictBtn.addEventListener('click', function() {
        // Convert canvas to blob
        capturedImage.toBlob(function(blob) {
            // Create file-like object
            const imageFile = new File([blob], "captured-image.jpg", { type: "image/jpeg" });
            
            // Get processing options
            const enhanceContrast = enhanceContrastCheckbox.checked;
            const autoCrop = autoCropCheckbox.checked;

            // Create form data
            const formData = new FormData();
            formData.append('file', imageFile);
            formData.append('enhance_contrast', enhanceContrast);
            formData.append('auto_crop', autoCrop);
            formData.append('language', currentLanguage);

            // Submit the image for prediction
            submitImageForPrediction(formData);
        }, 'image/jpeg', 0.9);
    });

    // Initialize camera
    async function initializeCamera() {
        try {
            // Show processing options
            processingOptions.classList.remove('d-none');
            
            // Check if we already have a stream
            if (stream) {
                return;
            }

            // Get available cameras
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                const devices = await navigator.mediaDevices.enumerateDevices();
                availableCameras = devices.filter(device => device.kind === 'videoinput');
                
                // Enable camera switch button if more than one camera is available
                if (availableCameras.length > 1) {
                    cameraSwitchBtn.disabled = false;
                }
            }

            // Get camera stream
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: facingMode },
                audio: false
            });
            
            // Attach stream to video element
            cameraStream.srcObject = stream;
        } catch (error) {
            showError(translations[currentLanguage]['cameraError'] + error.message);
            console.error('Camera error:', error);
        }
    }

    // Switch between front and rear cameras
    async function switchCamera() {
        // Stop current stream
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }

        // Toggle facing mode
        facingMode = facingMode === 'environment' ? 'user' : 'environment';

        try {
            // Get new stream with different camera
            stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: facingMode },
                audio: false
            });
            
            // Attach new stream
            cameraStream.srcObject = stream;
        } catch (error) {
            showError(translations[currentLanguage]['cameraSwitchError'] + error.message);
            console.error('Camera switch error:', error);
        }
    }

    // Capture image from camera
    function captureImage() {
        // Create canvas with same dimensions as video
        const canvas = capturedImage;
        const context = canvas.getContext('2d');
        
        // Set canvas dimensions
        canvas.width = cameraStream.videoWidth;
        canvas.height = cameraStream.videoHeight;
        
        // Draw video frame on canvas
        context.drawImage(cameraStream, 0, 0, canvas.width, canvas.height);
        
        // Show preview
        previewContainer.classList.remove('d-none');
        
        // Disable capture and switch buttons while in preview
        cameraCaptureBtn.disabled = true;
        cameraSwitchBtn.disabled = true;
    }

    // Submit image for prediction
    function submitImageForPrediction(formData) {
        // Stop any speaking
        stopSpeaking();
        
        // Show loading spinner
        loading.classList.remove('d-none');
        resultContainer.classList.add('d-none');
        errorMessage.classList.add('d-none');

        // Send request to server
        fetch('/predict', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            loading.classList.add('d-none');
            
            if (data.error) {
                showError(data.error);
                return;
            }

            // Store the current results
            currentResults = data;

            // Update UI with results
            updateResultsUI(data);

            // Show results
            resultContainer.classList.remove('d-none');
            if (data.processed_image_path) {
                previewImage.src = data.processed_image_path;
            } else {
                previewImage.src = data.image_path;
            }
        })
        .catch(error => {
            loading.classList.add('d-none');
            showError(translations[currentLanguage]['error']);
            console.error('Error:', error);
        });
    }

    // Update UI with prediction results
    function updateResultsUI(data) {
        // Define disease icons mapping
        const diseaseIcons = {
            'Early Blight': 'fas fa-seedling',
            'Late Blight': 'fas fa-cloud-rain',
            'Bacterial Spot': 'fas fa-bacteria',
            'Leaf Mold': 'fas fa-leaf',
            'Mosaic Virus': 'fas fa-virus',
            'Septoria Leaf Spot': 'fas fa-bullseye',
            'Spider Mites': 'fas fa-spider',
            'Target Spot': 'fas fa-bullseye',
            'Yellow Leaf Curl Virus': 'fas fa-wind',
            'Healthy': 'fas fa-heart'
        };

        // Get the top prediction
        const topResult = data.results[0];
        
        // Get or format disease name
        let diseaseName = topResult.name || formatDiseaseName(topResult.class);
        
        // Set disease name
        const diseaseNameEl = document.getElementById('disease-name');
        diseaseNameEl.textContent = diseaseName;
        
        // Set confidence value and progress bar
        const confidence = Math.round(topResult.probability);
        document.getElementById('confidence-value').textContent = `${confidence}%`;
        
        const confidenceBar = document.getElementById('confidence-bar');
        confidenceBar.style.width = `${confidence}%`;
        confidenceBar.setAttribute('aria-valuenow', confidence);
        
        // Set confidence bar color based on confidence level
        confidenceBar.classList.remove('high-confidence', 'medium-confidence', 'low-confidence');
        if (confidence >= 70) {
            confidenceBar.classList.add('high-confidence');
        } else if (confidence >= 50) {
            confidenceBar.classList.add('medium-confidence');
        } else {
            confidenceBar.classList.add('low-confidence');
        }
        
        // Set appropriate icon for disease
        const icon = diseaseIcons[diseaseName] || 'fas fa-bug';
        const iconElement = document.querySelector('.disease-icon i');
        iconElement.className = icon;
        
        // Handle low confidence predictions and alternative predictions carousel
        if (data.low_confidence) {
            document.getElementById('low-confidence-warning').classList.remove('d-none');
            document.getElementById('alt-predictions-carousel').classList.remove('d-none');
            
            // Set up the carousel
            const carouselItemsContainer = document.getElementById('carousel-items-container');
            const carouselControls = document.getElementById('carousel-controls');
            
            // Clear previous content
            carouselItemsContainer.innerHTML = '';
            carouselControls.innerHTML = '';
            
            // Create carousel items for top 3 predictions
            data.results.forEach((result, index) => {
                // Get or format disease name for this prediction
                const predName = result.name || formatDiseaseName(result.class);
                const predConfidence = Math.round(result.probability);
                const predIcon = diseaseIcons[predName] || 'fas fa-bug';
                
                // Create carousel item
                const item = document.createElement('div');
                item.className = `alt-prediction-item ${index === 0 ? 'active' : ''} animate-slide-in`;
                item.style.animationDelay = `${index * 0.1}s`;
                item.setAttribute('data-index', index);
                
                item.innerHTML = `
                    <div class="disease-icon">
                        <i class="${predIcon}"></i>
                    </div>
                    <div class="ms-3">
                        <strong>${predName}</strong>
                        <span class="confidence-badge ${getConfidenceBadgeClass(predConfidence)}">${predConfidence}%</span>
                    </div>
                `;
                
                carouselItemsContainer.appendChild(item);
                
                // Create carousel dot control
                const dot = document.createElement('div');
                dot.className = `alt-carousel-dot ${index === 0 ? 'active' : ''}`;
                dot.setAttribute('data-index', index);
                carouselControls.appendChild(dot);
                
                // Add click event to dot control
                dot.addEventListener('click', () => {
                    // Update active dot
                    document.querySelectorAll('.alt-carousel-dot').forEach(d => d.classList.remove('active'));
                    dot.classList.add('active');
                    
                    // Update active item
                    document.querySelectorAll('.alt-prediction-item').forEach(i => i.classList.remove('active'));
                    document.querySelector(`.alt-prediction-item[data-index="${index}"]`).classList.add('active');
                });
            });
        } else {
            document.getElementById('low-confidence-warning').classList.add('d-none');
            document.getElementById('alt-predictions-carousel').classList.add('d-none');
        }
        
        // Update the severity indicator based on the disease
        updateSeverityIndicator(diseaseName);
        
        // Display prevention steps in accordion format
        createPreventionAccordion(topResult.prevention || []);
    }

    // Helper function to determine confidence badge class
    function getConfidenceBadgeClass(confidence) {
        if (confidence >= 70) {
            return 'badge-high';
        } else if (confidence >= 50) {
            return 'badge-medium';
        } else {
            return 'badge-low';
        }
    }

    // Show error message
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('d-none');
    }

    // Format disease name for display
    function formatDiseaseName(name) {
        // Remove underscores and replace with spaces
        return name.replace(/__/g, ' - ').replace(/_/g, ' ');
    }

    // Function to display prediction results
    function displayResults(data) {
        // Show results container
        document.getElementById('result-container').classList.remove('d-none');
    }

    // Create prevention accordion with steps
    function createPreventionAccordion(preventionSteps) {
        const accordionContainer = document.getElementById('preventionAccordion');
        
        // Clear existing content
        accordionContainer.innerHTML = '';
        
        // If no prevention steps, show message
        if (!preventionSteps || preventionSteps.length === 0) {
            accordionContainer.innerHTML = `
                <div class="alert alert-info">
                    ${translations[currentLanguage]['noPreventionSteps'] || 'No prevention steps available.'}
                </div>
            `;
            return;
        }
        
        // Map common keywords to appropriate icons
        const iconMapping = {
            'water': 'fas fa-tint',
            'irrigation': 'fas fa-tint',
            'moisture': 'fas fa-tint',
            'wet': 'fas fa-tint',
            'rain': 'fas fa-cloud-rain',
            'fungicide': 'fas fa-spray-can',
            'spray': 'fas fa-spray-can',
            'chemical': 'fas fa-flask',
            'seed': 'fas fa-seedling',
            'plant': 'fas fa-seedling',
            'rotate': 'fas fa-sync',
            'rotation': 'fas fa-sync',
            'remove': 'fas fa-trash',
            'destroy': 'fas fa-trash',
            'space': 'fas fa-expand',
            'spacing': 'fas fa-expand',
            'distance': 'fas fa-expand',
            'variety': 'fas fa-leaf',
            'resistant': 'fas fa-shield-alt',
            'harvest': 'fas fa-shopping-basket',
            'weather': 'fas fa-sun',
            'temperature': 'fas fa-temperature-high',
            'mulch': 'fas fa-layer-group',
            'soil': 'fas fa-mountain',
            'hygienic': 'fas fa-hands-wash',
            'clean': 'fas fa-broom',
            'sanitize': 'fas fa-pump-soap',
            'prune': 'fas fa-cut',
            'cut': 'fas fa-cut',
            'tools': 'fas fa-tools',
            'default': 'fas fa-check-circle'
        };
        
        // Helper function to find the appropriate icon for a prevention step
        function findIcon(text) {
            // Convert to lowercase for case-insensitive matching
            const lowerText = text.toLowerCase();
            
            // Find the first keyword match
            for (const [keyword, icon] of Object.entries(iconMapping)) {
                if (lowerText.includes(keyword)) {
                    return icon;
                }
            }
            
            // Default icon if no match found
            return iconMapping.default;
        }
        
        // Create accordion items for each prevention step
        preventionSteps.forEach((step, index) => {
            // Find appropriate icon
            const icon = findIcon(step);
            
            // Create a title from the first few words
            const stepWords = step.split(' ');
            const title = stepWords.slice(0, 3).join(' ') + (stepWords.length > 3 ? '...' : '');
            
            // Create accordion item
            const accordionItem = document.createElement('div');
            accordionItem.className = 'accordion-item fade-in-up';
            accordionItem.style.animationDelay = `${index * 0.1}s`;
            
            accordionItem.innerHTML = `
                <h2 class="accordion-header" id="heading${index}">
                    <button class="accordion-button ${index === 0 ? '' : 'collapsed'}" 
                            type="button" 
                            data-bs-toggle="collapse" 
                            data-bs-target="#collapse${index}" 
                            aria-expanded="${index === 0 ? 'true' : 'false'}" 
                            aria-controls="collapse${index}">
                        <div class="prevention-icon">
                            <i class="${icon}"></i>
                        </div>
                        ${title}
                    </button>
                </h2>
                <div id="collapse${index}" 
                     class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                     aria-labelledby="heading${index}" 
                     data-bs-parent="#preventionAccordion">
                    <div class="accordion-body">
                        <div class="prevention-step">
                            <div class="prevention-step-content">
                                <p class="prevention-step-description">${step}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            accordionContainer.appendChild(accordionItem);
        });
    }
    
    // Update severity indicator based on disease
    function updateSeverityIndicator(diseaseName) {
        const severityBadge = document.getElementById('severity-badge');
        let severity = 'medium'; // Default severity
        let severityText = 'Medium Severity';
        
        // Define high severity diseases
        const highSeverityDiseases = [
            'Late Blight', 
            'Bacterial Spot', 
            'Mosaic Virus',
            'Yellow Leaf Curl Virus'
        ];
        
        // Define low severity diseases
        const lowSeverityDiseases = [
            'Healthy', 
            'Septoria Leaf Spot',
            'Target Spot'
        ];
        
        // Set severity based on disease name
        if (highSeverityDiseases.some(disease => diseaseName.includes(disease))) {
            severity = 'high';
            severityText = 'High Severity';
        } else if (lowSeverityDiseases.some(disease => diseaseName.includes(disease))) {
            severity = 'low';
            severityText = 'Low Severity';
        }
        
        // Update the severity badge
        severityBadge.className = `severity-indicator severity-${severity}`;
        severityBadge.innerHTML = `<span>${translations[currentLanguage]['severity' + severity.charAt(0).toUpperCase() + severity.slice(1)] || severityText}</span>`;
    }

    // Initialize theme settings
    function initializeTheme() {
        // Check for saved theme preference
        const savedTheme = localStorage.getItem('preferredTheme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        }
        
        // Add event listener for theme toggle
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Toggle between light and dark themes
    function toggleTheme() {
        if (document.body.classList.contains('dark-mode')) {
            // Switch to light mode
            document.body.classList.remove('dark-mode');
            localStorage.setItem('preferredTheme', 'light');
        } else {
            // Switch to dark mode
            document.body.classList.add('dark-mode');
            localStorage.setItem('preferredTheme', 'dark');
        }
    }

    // Initialize feedback system
    function initializeFeedbackSystem() {
        // Populate correct disease select with available diseases
        populateDiseaseSelect();
        
        // Event listeners for feedback buttons
        if (correctPredictionBtn) {
            correctPredictionBtn.addEventListener('click', function() {
                submitFeedback(true);
            });
        }
        
        if (incorrectPredictionBtn) {
            incorrectPredictionBtn.addEventListener('click', function() {
                // Show correction form
                correctionForm.classList.remove('d-none');
                feedbackSuccess.classList.add('d-none');
            });
        }
        
        if (submitCorrectionBtn) {
            submitCorrectionBtn.addEventListener('click', function() {
                // Get selected disease
                const selectedDisease = correctDiseaseSelect.value;
                if (!selectedDisease) {
                    return;
                }
                
                // Submit feedback with correction
                submitFeedback(false, selectedDisease);
            });
        }
    }
    
    // Populate disease select dropdown
    function populateDiseaseSelect() {
        if (!correctDiseaseSelect) return;
        
        // Clear existing options
        correctDiseaseSelect.innerHTML = '';
        
        // Add default option
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = translations[currentLanguage]['selectDisease'] || 'Select disease...';
        correctDiseaseSelect.appendChild(defaultOption);
        
        // Add all diseases from the diseaseTranslations object
        for (const [diseaseKey, translations] of Object.entries(diseaseTranslations)) {
            const option = document.createElement('option');
            option.value = diseaseKey;
            option.textContent = translations[currentLanguage] || diseaseKey;
            correctDiseaseSelect.appendChild(option);
        }
    }
    
    // Submit feedback to the server
    function submitFeedback(isCorrect, correctedDisease = null) {
        // If no prediction results or no image, return
        if (!currentResults || !selectedFile) {
            return;
        }
        
        // Prepare data
        const feedbackData = new FormData();
        
        // Add the original prediction details
        feedbackData.append('original_prediction', currentResults.results[0].class);
        feedbackData.append('confidence', currentResults.results[0].probability);
        feedbackData.append('is_correct', isCorrect);
        
        // If it's incorrect, add the corrected disease
        if (!isCorrect && correctedDisease) {
            feedbackData.append('corrected_disease', correctedDisease);
        }
        
        // If user wants to contribute to dataset, add the image
        if (!isCorrect && contributeToDatasetCheckbox && contributeToDatasetCheckbox.checked) {
            feedbackData.append('contribute_to_dataset', 'true');
            feedbackData.append('image', selectedFile);
        }
        
        // Add location data if available
        if (userLocation) {
            feedbackData.append('latitude', userLocation.latitude);
            feedbackData.append('longitude', userLocation.longitude);
            if (userLocation.name) {
                feedbackData.append('location_name', userLocation.name);
            }
        }
        
        // Show loading indicator
        const submitBtn = document.getElementById('submit-correction-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';
        }
        
        // Send feedback to server
        fetch('/feedback', {
            method: 'POST',
            body: feedbackData
        })
        .then(response => response.json())
        .then(data => {
            // Hide correction form if visible
            if (correctionForm) {
                correctionForm.classList.add('d-none');
            }
            
            // Show success message
            if (feedbackSuccess) {
                feedbackSuccess.classList.remove('d-none');
                
                // Add success class to feedback container
                const feedbackContainer = document.querySelector('.feedback-container');
                if (feedbackContainer) {
                    feedbackContainer.classList.add('success');
                }
            }
            
            // If insights were returned with the response, update them
            if (data.insights) {
                updateInsights(data.insights);
                
                // Show insights container
                if (insightsContainer) {
                    insightsContainer.classList.remove('d-none');
                    
                    // Scroll to insights after a delay
                    setTimeout(() => {
                        insightsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 800);
                }
                
                // Add a button to toggle insights visibility if not already present
                let toggleBtn = document.getElementById('toggle-insights-btn');
                if (!toggleBtn) {
                    toggleBtn = document.createElement('button');
                    toggleBtn.id = 'toggle-insights-btn';
                    toggleBtn.className = 'btn btn-outline-primary mt-3 pulse-animation';
                    toggleBtn.innerHTML = `<i class="fas fa-chart-line me-2"></i> <span data-i18n="viewInsights">${translations[currentLanguage]['viewInsights'] || 'View Community Insights'}</span>`;
                    
                    toggleBtn.addEventListener('click', function() {
                        insightsContainer.classList.toggle('d-none');
                        if (!insightsContainer.classList.contains('d-none')) {
                            insightsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                        
                        // Remove pulse animation after first click
                        this.classList.remove('pulse-animation');
                    });
                    
                    // Add to the page in the feedback container
                    if (feedbackSuccess && feedbackSuccess.parentNode) {
                        feedbackSuccess.parentNode.appendChild(toggleBtn);
                    }
                } else {
                    // Update existing button
                    toggleBtn.classList.add('pulse-animation');
                }
            }
            
            // Reset button state
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i class="fas fa-paper-plane"></i> <span data-i18n="submitCorrection">${translations[currentLanguage]['submitCorrection'] || 'Submit Correction'}</span>`;
            }
        })
        .catch(error => {
            console.error('Error submitting feedback:', error);
            showError(translations[currentLanguage]['feedbackError'] || 'Error submitting feedback');
            
            // Reset button state
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<i class="fas fa-paper-plane"></i> <span data-i18n="submitCorrection">${translations[currentLanguage]['submitCorrection'] || 'Submit Correction'}</span>`;
            }
        });
    }

    // Initialize user location
    function initializeUserLocation() {
        if (navigator.geolocation && !isLoadingLocation && !userLocation) {
            isLoadingLocation = true;
            
            navigator.geolocation.getCurrentPosition(
                // Success callback
                function(position) {
                    userLocation = {
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude
                    };
                    
                    // Get location name from coordinates
                    fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${userLocation.latitude}&lon=${userLocation.longitude}&zoom=10`)
                        .then(response => response.json())
                        .then(data => {
                            if (data && data.address) {
                                // Get city or state level location
                                userLocation.name = data.address.city || 
                                                   data.address.town || 
                                                   data.address.state || 
                                                   data.address.country || 
                                                   'Unknown Location';
                            }
                            isLoadingLocation = false;
                        })
                        .catch(error => {
                            console.error('Error getting location name:', error);
                            isLoadingLocation = false;
                        });
                },
                // Error callback
                function(error) {
                    console.log('Error getting location:', error.message);
                    isLoadingLocation = false;
                },
                // Options
                {
                    enableHighAccuracy: false,
                    timeout: 5000,
                    maximumAge: 0
                }
            );
        }
    }

    // Update insights section with data from the server
    function updateInsights(insightsData) {
        if (!insightsContainer) return;
        
        // Update region diseases chart
        if (regionDiseasesChart && insightsData.regionDiseases && insightsData.regionDiseases.length > 0) {
            updateRegionDiseasesChart(insightsData.regionDiseases);
        } else if (regionDiseasesChart) {
            regionDiseasesChart.innerHTML = `<p class="text-muted">${translations[currentLanguage]['noInsightsAvailable'] || 'No insights available yet. Be the first to contribute!'}</p>`;
        }
        
        // Update seasonal trends chart
        if (seasonalTrendsChart && insightsData.seasonalTrends && insightsData.seasonalTrends.length > 0) {
            updateSeasonalTrendsChart(insightsData.seasonalTrends);
        } else if (seasonalTrendsChart) {
            seasonalTrendsChart.innerHTML = `<p class="text-muted">${translations[currentLanguage]['noInsightsAvailable'] || 'No insights available yet. Be the first to contribute!'}</p>`;
        }
        
        // Update recent submissions
        if (recentSubmissions && insightsData.recentSubmissions && insightsData.recentSubmissions.length > 0) {
            updateRecentSubmissions(insightsData.recentSubmissions);
        } else if (recentSubmissions) {
            recentSubmissions.innerHTML = `<p class="text-muted">${translations[currentLanguage]['noInsightsAvailable'] || 'No insights available yet. Be the first to contribute!'}</p>`;
        }
    }
    
    // Update region diseases chart
    function updateRegionDiseasesChart(regionDiseases) {
        if (!regionDiseasesChart) return;
        
        // Clear existing content
        regionDiseasesChart.innerHTML = '';
        
        // Sort diseases by count in descending order
        regionDiseases.sort((a, b) => b.count - a.count);
        
        // Calculate total for percentage
        const total = regionDiseases.reduce((sum, disease) => sum + disease.count, 0);
        
        // If no data, show message
        if (total === 0) {
            regionDiseasesChart.innerHTML = `<p class="text-muted">${translations[currentLanguage]['noInsightsAvailable'] || 'No insights available yet. Be the first to contribute!'}</p>`;
            return;
        }
        
        // Take top 5 diseases
        const topDiseases = regionDiseases.slice(0, 5);
        
        // Create chart
        topDiseases.forEach(disease => {
            // Get translated disease name
            const diseaseName = disease.name;
            let translatedName = getTranslatedDiseaseName(diseaseName);
            
            // Truncate very long names (for display purposes)
            const displayName = translatedName.length > 25 ? translatedName.substring(0, 22) + '...' : translatedName;
            
            // Calculate percentage
            const percentage = Math.round((disease.count / total) * 100);
            
            // Calculate width based on percentage (min 10% for visibility)
            const width = Math.max(percentage, 10);
            
            // Create chart bar
            const chartBar = document.createElement('div');
            chartBar.className = 'chart-bar';
            chartBar.style.width = `${width}%`;
            chartBar.title = `${translatedName}: ${percentage}%`; // Add tooltip
            
            // Add label and value
            const label = document.createElement('span');
            label.className = 'chart-bar-label';
            label.textContent = displayName;
            
            const value = document.createElement('span');
            value.className = 'chart-bar-value';
            value.textContent = `${percentage}%`;
            
            // Append to chart bar
            chartBar.appendChild(label);
            chartBar.appendChild(value);
            
            // Append to chart container with animation delay
            chartBar.style.animation = `fadeIn 0.5s ease forwards ${topDiseases.indexOf(disease) * 0.1}s`;
            regionDiseasesChart.appendChild(chartBar);
        });
    }
    
    // Update seasonal trends chart
    function updateSeasonalTrendsChart(seasonalTrends) {
        if (!seasonalTrendsChart) return;
        
        // Clear existing content
        seasonalTrendsChart.innerHTML = '';
        
        // Sort by count
        seasonalTrends.sort((a, b) => b.count - a.count);
        
        // Calculate total
        const total = seasonalTrends.reduce((sum, item) => sum + item.count, 0);
        
        // If no data, show message
        if (total === 0) {
            seasonalTrendsChart.innerHTML = `<p class="text-muted">${translations[currentLanguage]['noInsightsAvailable'] || 'No insights available yet. Be the first to contribute!'}</p>`;
            return;
        }
        
        // Take top 5
        const topItems = seasonalTrends.slice(0, 5);
        
        // Create chart
        topItems.forEach(item => {
            // Get translated disease name with season
            const diseaseName = item.disease;
            let translatedName = getTranslatedDiseaseName(diseaseName);
            
            // Format as "Season: Disease"
            const seasonalLabel = `${item.season}: ${translatedName}`;
            
            // Truncate very long names (for display purposes)
            const displayName = seasonalLabel.length > 25 ? seasonalLabel.substring(0, 22) + '...' : seasonalLabel;
            
            // Calculate percentage
            const percentage = Math.round((item.count / total) * 100);
            
            // Calculate width (min 10%)
            const width = Math.max(percentage, 10);
            
            // Create chart bar with different color
            const chartBar = document.createElement('div');
            chartBar.className = 'chart-bar';
            chartBar.style.width = `${width}%`;
            chartBar.style.background = 'linear-gradient(90deg, #5c6bc0, #3949ab)';
            chartBar.title = `${seasonalLabel}: ${percentage}%`; // Add tooltip
            
            // Add label and value
            const label = document.createElement('span');
            label.className = 'chart-bar-label';
            label.textContent = displayName;
            
            const value = document.createElement('span');
            value.className = 'chart-bar-value';
            value.textContent = `${percentage}%`;
            
            // Append to chart bar
            chartBar.appendChild(label);
            chartBar.appendChild(value);
            
            // Append to chart container with animation delay
            chartBar.style.animation = `fadeIn 0.5s ease forwards ${topItems.indexOf(item) * 0.1}s`;
            seasonalTrendsChart.appendChild(chartBar);
        });
    }
    
    // Update recent submissions
    function updateRecentSubmissions(recentSubmissions) {
        if (!document.getElementById('recent-submissions')) return;
        
        const container = document.getElementById('recent-submissions');
        // Clear existing content
        container.innerHTML = '';
        
        // If no submissions, show message
        if (!recentSubmissions || recentSubmissions.length === 0) {
            const emptyMessage = document.createElement('p');
            emptyMessage.className = 'empty-insights-message';
            emptyMessage.textContent = translations[currentLanguage]['noInsightsAvailable'] || 'No insights available yet. Be the first to contribute!';
            container.appendChild(emptyMessage);
            return;
        }
        
        // Create submission items
        recentSubmissions.forEach((submission, index) => {
            // Get translated disease name
            const translatedName = getTranslatedDiseaseName(submission.disease);
            
            // Create submission item
            const item = document.createElement('div');
            item.className = 'submission-item';
            
            // Create disease name and location
            const diseaseInfoDiv = document.createElement('div');
            diseaseInfoDiv.className = 'submission-info';
            
            const diseaseName = document.createElement('div');
            diseaseName.className = 'submission-disease';
            diseaseName.textContent = translatedName;
            
            // Create details container
            const detailsDiv = document.createElement('div');
            detailsDiv.className = 'submission-details';
            
            // If there's an image thumbnail, add it
            if (submission.thumbnail) {
                const img = document.createElement('img');
                img.className = 'submission-image';
                img.src = submission.thumbnail;
                img.alt = translatedName;
                detailsDiv.appendChild(img);
            }
            
            // Create metadata container
            const metaDiv = document.createElement('div');
            metaDiv.className = 'submission-meta';
            
            // Create location span if available
            if (submission.location) {
                const locationSpan = document.createElement('span');
                locationSpan.className = 'submission-location';
                locationSpan.textContent = `${translations[currentLanguage]['location'] || 'Location'}: ${submission.location}`;
                metaDiv.appendChild(locationSpan);
            }
            
            // Create date span
            const dateSpan = document.createElement('span');
            dateSpan.className = 'submission-date';
            
            // Format date - convert to local date string
            let dateStr = submission.timestamp;
            try {
                const date = new Date(submission.timestamp);
                if (!isNaN(date.getTime())) {
                    dateStr = date.toLocaleDateString();
                }
            } catch (e) {
                console.error('Error formatting date:', e);
            }
            
            dateSpan.textContent = `${translations[currentLanguage]['submittedOn'] || 'Submitted on'}: ${dateStr}`;
            metaDiv.appendChild(dateSpan);
            
            // Add meta div to details
            detailsDiv.appendChild(metaDiv);
            
            // Append all elements
            diseaseInfoDiv.appendChild(diseaseName);
            item.appendChild(diseaseInfoDiv);
            item.appendChild(detailsDiv);
            
            // Add animation with delay
            item.style.animation = `fadeIn 0.5s ease forwards ${index * 0.1}s`;
            container.appendChild(item);
        });
    }
    
    // Helper function to get translated disease name
    function getTranslatedDiseaseName(diseaseKey) {
        // Check if the disease key exists in diseaseTranslations
        if (diseaseTranslations[diseaseKey]) {
            return diseaseTranslations[diseaseKey][currentLanguage] || diseaseKey;
        }
        // Fallback to formatted disease name
        return formatDiseaseName(diseaseKey);
    }
}); 