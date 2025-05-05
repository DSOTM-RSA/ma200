// Main application JavaScript

// DOM ready function
document.addEventListener('DOMContentLoaded', function() {
    // Flash messages that auto-dismiss
    const flashMessages = document.querySelectorAll('.alert');
    if (flashMessages.length > 0) {
        setTimeout(function() {
            flashMessages.forEach(message => {
                message.style.opacity = '0';
                setTimeout(() => message.style.display = 'none', 300);
            });
        }, 5000);
    }

    // PIN validation
    const pinInputs = document.querySelectorAll('input[pattern]');
    pinInputs.forEach(input => {
        input.addEventListener('input', function() {
            validatePin(this);
        });
    });

    // Form submission with validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const pinInput = form.querySelector('input[pattern]');
            if (pinInput && !validatePin(pinInput)) {
                e.preventDefault();
            }
        });
    });
});

// Validate PIN format (4 letters + 2 digits)
function validatePin(input) {
    if (input.value.length !== 6) return false;
    
    const pattern = /^[A-Za-z]{4}\d{2}$/;
    const isValid = pattern.test(input.value);
    
    if (!isValid && input.value.length === 6) {
        input.classList.add('border-danger');
        const errorEl = document.getElementById(input.id + '-error');
        if (errorEl) {
            errorEl.textContent = 'PIN must be 4 letters followed by 2 digits';
            errorEl.style.display = 'block';
        }
    } else {
        input.classList.remove('border-danger');
        const errorEl = document.getElementById(input.id + '-error');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    }
    
    return isValid;
}

// Refresh stocks data periodically on portfolio page (optional)
if (window.location.pathname === '/portfolio') {
    setInterval(function() {
        const refreshButton = document.querySelector('button[hx-get="/portfolio"]');
        if (refreshButton) {
            refreshButton.click();
        }
    }, 300000); // 5 minutes
}