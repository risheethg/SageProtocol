document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('mealForm');
    const imageInput = document.getElementById('mealImage');
    const imagePreview = document.getElementById('imagePreview');
    const submitButton = document.getElementById('submitButton');
    const clearButton = document.getElementById('clearButton');
    const uploadProgress = document.getElementById('uploadProgress');
    const errorMessage = document.getElementById('errorMessage');
    const mealText = document.getElementById('mealText');
    
    // Maximum file size in bytes (16MB)
    const MAX_FILE_SIZE = 16 * 1024 * 1024;
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
        setTimeout(() => {
            errorMessage.classList.add('hidden');
        }, 5000);
    }
    
    function validateFile(file) {
        // Check file size
        if (file.size > MAX_FILE_SIZE) {
            showError('File is too large. Maximum size is 16MB.');
            return false;
        }
        
        // Check file type
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        if (!validTypes.includes(file.type)) {
            showError('Invalid file type. Only JPG, JPEG, and PNG files are allowed.');
            return false;
        }
        
        return true;
    }
    
    function updateImagePreview(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.innerHTML = `
                <img src="${e.target.result}" alt="Meal preview" class="preview-image">
                <span class="change-image">Click to change image</span>
            `;
            submitButton.disabled = false;
            // Disable text input when image is uploaded
            mealText.disabled = true;
            mealText.placeholder = "Text input disabled when image is uploaded";
        };
        reader.readAsDataURL(file);
    }
    
    function clearForm() {
        form.reset();
        imagePreview.innerHTML = `
            <i class="fa-solid fa-camera"></i>
            <p>Click to upload or drag an image here</p>
            <span class="file-requirements">Accepted formats: PNG, JPG, JPEG (max 16MB)</span>
        `;
        submitButton.disabled = true;
        errorMessage.classList.add('hidden');
        // Re-enable both inputs when form is cleared
        mealText.disabled = false;
        mealText.placeholder = "Describe your meal...";
        imagePreview.style.pointerEvents = 'auto';
        imagePreview.style.opacity = '1';
    }
    
    // Handle text input
    mealText.addEventListener('input', function() {
        if (this.value.trim()) {
            // Disable image upload when text is entered
            imagePreview.style.pointerEvents = 'none';
            imagePreview.style.opacity = '0.5';
            submitButton.disabled = false;
        } else {
            // Re-enable image upload when text is cleared
            imagePreview.style.pointerEvents = 'auto';
            imagePreview.style.opacity = '1';
            submitButton.disabled = true;
        }
    });
    
    // Handle drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        imagePreview.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
        });
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        imagePreview.addEventListener(eventName, () => {
            if (!mealText.value.trim()) {
                imagePreview.classList.add('drag-active');
            }
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        imagePreview.addEventListener(eventName, () => {
            imagePreview.classList.remove('drag-active');
        });
    });
    
    imagePreview.addEventListener('drop', (e) => {
        if (mealText.value.trim()) return; // Prevent drop if text is entered
        
        const file = e.dataTransfer.files[0];
        if (file && validateFile(file)) {
            imageInput.files = e.dataTransfer.files;
            updateImagePreview(file);
        }
    });
    
    // Handle click to upload
    imagePreview.addEventListener('click', () => {
        if (!mealText.value.trim()) {
            imageInput.click();
        }
    });
    
    imageInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file && validateFile(file)) {
            updateImagePreview(file);
        } else {
            imageInput.value = '';
        }
    });
    
    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData();
        const mealImage = document.getElementById('mealImage').files[0];
        const mealText = document.getElementById('mealText').value.trim();
        
        if (!mealImage && !mealText) {
            showError('Please either upload an image or enter meal description');
            return;
        }
        
        if (mealImage) {
            formData.append('mealImage', mealImage);
        }
        if (mealText) {
            formData.append('mealText', mealText);
        }
        
        // Show upload progress
        uploadProgress.classList.remove('hidden');
        submitButton.disabled = true;
        
        try {
            console.log('Submitting form data...');
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            console.log('Response received:', response);
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success) {
                // Redirect to meal analysis page
                window.location.href = '/meal-analysis';
            } else {
                showError(data.message || 'Failed to analyze meal');
                submitButton.disabled = false;
            }
        } catch (error) {
            console.error('Upload error:', error);
            showError('An error occurred while uploading the meal');
            submitButton.disabled = false;
        } finally {
            uploadProgress.classList.add('hidden');
        }
    });
    
    // Handle clear button
    clearButton.addEventListener('click', clearForm);

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    menuToggle.addEventListener('click', function() {
        navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
    });
}); 