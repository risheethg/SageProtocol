document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const uploadBox = document.getElementById('upload-box');
    const fileInput = document.getElementById('meal-upload');
    const previewImage = document.getElementById('preview-image');
    const mealDescription = document.getElementById('meal-description');
    const submitButton = document.getElementById('submit-button');
    const uploadForm = document.getElementById('upload-form');

    // Update button state based on form content
    function updateButtonState() {
        const hasImage = fileInput.files.length > 0;
        const hasDescription = mealDescription.value.trim() !== '';
        
        submitButton.disabled = !(hasImage || hasDescription);
    }

    // Handle file input click
    uploadBox.addEventListener('click', function() {
        fileInput.click();
    });

    // Handle file selection
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.classList.remove('hidden');
                updateButtonState();
            }
            reader.readAsDataURL(file);
        }
    });

    // Handle drag and drop
    uploadBox.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--primary-color)';
    });

    uploadBox.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--border-color)';
    });

    uploadBox.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = 'var(--border-color)';
        
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) {
            fileInput.files = e.dataTransfer.files;
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewImage.classList.remove('hidden');
                updateButtonState();
            }
            reader.readAsDataURL(file);
        } else {
            alert('Please upload an image file.');
        }
    });

    // Handle description input
    mealDescription.addEventListener('input', updateButtonState);

    // Handle form submission
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        
        try {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
            
            const response = await fetch('/api/upload-meal', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Meal logged successfully!');
                window.location.href = '/dashboard';
            } else {
                alert(data.message || 'Failed to log meal. Please try again.');
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('An error occurred while uploading. Please try again.');
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = '<i class="fa-solid fa-utensils"></i> Get Details';
        }
    });

    // Mobile menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    menuToggle.addEventListener('click', function() {
        navLinks.style.display = navLinks.style.display === 'flex' ? 'none' : 'flex';
    });
}); 