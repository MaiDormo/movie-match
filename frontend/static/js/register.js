function validateForm(formData) {
    let isValid = true;
    
    // Name validation
    if (!formData.name.trim()) {
        showError('name', 'First name is required');
        isValid = false;
    } else if (formData.name.length < 2) {
        showError('name', 'First name must be at least 2 characters long');
        isValid = false;
    }

    // Surname validation
    if (!formData.surname.trim()) {
        showError('surname', 'Last name is required');
        isValid = false;
    } else if (formData.surname.length < 2) {
        showError('surname', 'Last name must be at least 2 characters long');
        isValid = false;
    }

    // Email validation
    if (!formData.email.trim()) {
        showError('email', 'Email address is required');
        isValid = false;
    } else if (!isValidEmail(formData.email)) {
        showError('email', 'Please enter a valid email address');
        isValid = false;
    }

    // Password validation
    if (!formData.password) {
        showError('password', 'Password is required');
        isValid = false;
    } else if (formData.password.length < 8) {
        showError('password', 'Password must be at least 8 characters long');
        isValid = false;
    }

    // Password confirmation validation
    if (!formData.password_confirmation) {
        showError('passwordConfirmation', 'Please confirm your password');
        isValid = false;
    } else if (formData.password !== formData.password_confirmation) {
        showError('passwordConfirmation', 'Passwords do not match');
        isValid = false;
    }

    return isValid;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email.trim());
}

async function handleRegister(event) {
    event.preventDefault();
    resetErrors();

    const formData = {
        name: document.getElementById('name').value.trim(),
        surname: document.getElementById('surname').value.trim(),
        email: document.getElementById('email').value.trim(),
        password: document.getElementById('password').value,
        password_confirmation: document.getElementById('passwordConfirmation').value
    };

    if (!validateForm(formData)) {
        showGeneralError('Please correct the errors above');
        return;
    }

    try {
        const response = await fetch('http://localhost:5013/api/v1/registrate-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            window.location.href = '/login';
        } else {
            if (data.status === 'fail' && data.data) {
                Object.keys(data.data).forEach(field => {
                    showError(field, data.data[field]);
                });
                showGeneralError('Please correct the errors above');
            } else {
                showGeneralError(data.message || 'Registration failed. Please try again.');
            }
        }
    } catch (error) {
        console.error('Registration error:', error);
        showGeneralError('Network error occurred. Please check your connection and try again.');
    }
}

function showError(field, message) {
    const input = document.getElementById(field);
    const errorDiv = document.getElementById(`${field}Error`);
    if (input && errorDiv) {
        input.classList.add('input-error');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        input.setAttribute('aria-invalid', 'true');
        input.setAttribute('aria-describedby', `${field}Error`);
    }
}

function showGeneralError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function resetErrors() {
    // Reset all error messages
    const errorDivs = document.querySelectorAll('.error-text, .error-message');
    errorDivs.forEach(div => {
        div.style.display = 'none';
        div.textContent = '';
    });

    // Reset input error styling
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.classList.remove('input-error');
        input.removeAttribute('aria-invalid');
        input.removeAttribute('aria-describedby');
    });
}