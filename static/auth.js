document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabButtons = document.querySelectorAll('.tab-btn');
    const authForms = document.querySelectorAll('.auth-form');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active class from all tabs and forms
            tabButtons.forEach(btn => btn.classList.remove('active'));
            authForms.forEach(form => form.classList.remove('active'));

            // Add active class to clicked tab and corresponding form
            button.classList.add('active');
            const formId = `${button.dataset.tab}-form`;
            document.getElementById(formId).classList.add('active');

            // Reset carousel if switching to signup
            if (button.dataset.tab === 'signup') {
                resetCarousel();
            }
        });
    });

    // Carousel functionality
    const slides = document.querySelectorAll('.carousel-slide');
    const progressBar = document.querySelector('.progress-bar');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    let currentSlide = 0;

    function updateCarousel() {
        // Update slides
        slides.forEach((slide, index) => {
            if (index === currentSlide) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });

        // Update progress bar
        const progress = ((currentSlide + 1) / slides.length) * 100;
        progressBar.style.width = `${progress}%`;

        // Update buttons
        prevBtn.disabled = currentSlide === 0;
        nextBtn.style.display = currentSlide === slides.length - 1 ? 'none' : 'block';
        submitBtn.style.display = currentSlide === slides.length - 1 ? 'block' : 'none';
    }

    function resetCarousel() {
        currentSlide = 0;
        updateCarousel();
    }

    function validateCurrentSlide() {
        const currentSlideElement = slides[currentSlide];
        const inputs = currentSlideElement.querySelectorAll('input[required], select[required]');
        let isValid = true;

        inputs.forEach(input => {
            if (!input.value) {
                isValid = false;
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        });

        return isValid;
    }

    // Event listeners for carousel navigation
    prevBtn.addEventListener('click', () => {
        if (currentSlide > 0) {
            currentSlide--;
            updateCarousel();
        }
    });

    nextBtn.addEventListener('click', () => {
        if (validateCurrentSlide()) {
            currentSlide++;
            updateCarousel();
        }
    });

    // Form submission
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signup-form').querySelector('form');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();
            
            if (data.success) {
                window.location.href = '/'; // Redirect to home page on success
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert('An error occurred during login');
            console.error('Login error:', error);
        }
    });

    // Handle "Other" medical condition
    const otherConditionCheckbox = document.getElementById('other_condition');
    const otherConditionInput = document.getElementById('other_condition_input');
    const otherConditionText = document.getElementById('other_condition_text');

    otherConditionCheckbox.addEventListener('change', () => {
        otherConditionInput.style.display = otherConditionCheckbox.checked ? 'block' : 'none';
        if (!otherConditionCheckbox.checked) {
            otherConditionText.value = '';
        }
    });

    // Check URL parameters for tab navigation
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    if (tab === 'signup') {
        const signupTab = document.querySelector('[data-tab="signup"]');
        if (signupTab) {
            signupTab.click();
        }
    }

    // Form validation function
    function validateForm(formData) {
        const errors = [];
        
        // Basic info validation
        if (!formData.name?.trim()) errors.push('Name is required');
        if (!formData.email?.trim()) errors.push('Email is required');
        if (!formData.password?.trim()) errors.push('Password is required');
        if (formData.password?.length < 8) errors.push('Password must be at least 8 characters');
        
        // Physical info validation
        if (!formData.height || formData.height <= 0) errors.push('Valid height is required');
        if (!formData.weight || formData.weight <= 0) errors.push('Valid weight is required');
        if (!formData.pre_pregnancy_weight || formData.pre_pregnancy_weight <= 0) errors.push('Valid pre-pregnancy weight is required');
        if (!formData.age || formData.age <= 0) errors.push('Valid age is required');
        
        // Pregnancy info validation
        if (!formData.trimester) errors.push('Trimester is required');
        if (!formData.multiple_pregnancies) errors.push('Multiple pregnancies status is required');
        
        // Dietary preferences validation
        if (!formData.diet_type) errors.push('Diet type is required');
        
        return errors;
    }

    // Update form submission to include validation
    signupForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!validateCurrentSlide()) {
            return;
        }

        // Collect medical conditions
        const medicalConditions = [];
        document.querySelectorAll('input[name="medical_conditions"]:checked').forEach(checkbox => {
            if (checkbox.value === 'other' && otherConditionText.value.trim()) {
                medicalConditions.push(otherConditionText.value.trim());
            } else if (checkbox.value !== 'other') {
                medicalConditions.push(checkbox.value);
            }
        });

        // Collect all form data
        const formData = {
            username: document.getElementById('email').value.split('@')[0],
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            password: document.getElementById('signup-password').value,
            height: document.getElementById('height').value,
            weight: document.getElementById('weight').value,
            pre_pregnancy_weight: document.getElementById('pre-pregnancy-weight').value,
            age: document.getElementById('age').value,
            trimester: document.getElementById('trimester').value,
            multiple_pregnancies: document.getElementById('multiple-pregnancies').value,
            medical_conditions: medicalConditions,
            diet_type: document.getElementById('diet-type').value,
            allergies: document.getElementById('allergies').value
        };

        // Validate form data
        const errors = validateForm(formData);
        if (errors.length > 0) {
            alert('Please correct the following errors:\n' + errors.join('\n'));
            return;
        }

        try {
            const response = await fetch('/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();
            
            if (data.success) {
                window.location.href = '/'; // Redirect to home page on success
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert('An error occurred during signup');
            console.error('Signup error:', error);
        }
    });

    // Add visual feedback for required fields
    const requiredFields = document.querySelectorAll('input[required], select[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', () => {
            if (!field.value.trim()) {
                field.classList.add('error');
                field.parentElement.classList.add('error');
            } else {
                field.classList.remove('error');
                field.parentElement.classList.remove('error');
            }
        });
    });

    // Initialize carousel
    updateCarousel();
}); 