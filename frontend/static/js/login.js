async function checkExistingToken() {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
        // Verify token validity using refresh-token endpoint
        const response = await fetch('http://localhost:5014/api/v1/refresh-token', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            // Update token and redirect to home
            localStorage.setItem('token', data.data.access_token);
            window.location.href = '/';
        } else {
            // Token is invalid, remove it
            localStorage.removeItem('token');
        }
    } catch (error) {
        console.error('Token verification error:', error);
        localStorage.removeItem('token');
    }
}

document.addEventListener('DOMContentLoaded', checkExistingToken);

async function handleLogin(event) {
    event.preventDefault();
    resetErrors();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!validateForm(email, password)) {
        return;
    }

    try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch('http://localhost:5014/api/v1/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.status === 'success') {
            localStorage.setItem('token', data.data.access_token);
            window.location.href = '/';
        } else {
            if (data.status === 'fail') {
                if (data.data) {
                    Object.keys(data.data).forEach(field => {
                        showFieldError(field, data.data[field]);
                    });
                } else {
                    showGeneralError(data.message || 'Login failed');
                }
            } else {
                showGeneralError(data.message || 'Login failed');
            }
        }
    } catch (error) {
        console.error('Login error:', error);
        showGeneralError('Network error occurred. Please try again later.');
    }
}

function validateForm(email, password) {
    let isValid = true;

    if (!email) {
        showFieldError('email', 'Email is required');
        isValid = false;
    } else if (!isValidEmail(email)) {
        showFieldError('email', 'Please enter a valid email address');
        isValid = false;
    }

    if (!password) {
        showFieldError('password', 'Password is required');
        isValid = false;
    }

    return isValid;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showFieldError(field, message) {
    const input = document.getElementById(field);
    const errorDiv = document.getElementById(`${field}Error`);
    if (input && errorDiv) {
        input.classList.add('input-error');
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
}

function showGeneralError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

function resetErrors() {
    const errorDivs = document.getElementsByClassName('error-message');
    Array.from(errorDivs).forEach(div => {
        div.style.display = 'none';
        div.textContent = '';
    });

    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => input.classList.remove('input-error'));
}