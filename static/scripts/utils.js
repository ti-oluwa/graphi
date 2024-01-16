
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + "=")) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
        }
        }
    }
    return cookieValue;
};


/**
 * Gets the timezone of the client.
 * @returns {string} the timezone of the client
 */
function getClientTimezone() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}


/**
 * Gets the element that displays messages for the form field
 * @param {Element} formField The form field
 * @returns The message element of the form field
 */
function getMsgEl(formField) {
    if (!formField.classList.contains('form-field')) {
        throw new Error('Field must have class "form-field"');
    }
    return formField.querySelector('.field-message');
}


/**
 * Sets and displays the error message for the form field
 * @param {Element} formField The form field that has an error
 * @param {string} errorMsg The error message to display
 */
function formFieldHasError(formField, errorMsg) {
    const msgEl = getMsgEl(formField);
    if (!msgEl) throw new Error('Field must have a message element with class "field-message"');

    const fieldInput = formField.querySelector('form-input');
    if (!fieldInput) throw new Error('Field must have a form-input element');
    
    msgEl.innerHTML = errorMsg;

    fieldInput.classList.add('invalid-field');
    fieldInput.addEventListener('input', () => {
        fieldInput.classList.remove('invalid-field');
        msgEl.innerHTML = '';
    });
}


/**
 * Checks if the email is valid 
 * @param {string} email The email to validate
 * @returns {boolean} true if the email is valid, false otherwise
 */
function isValidEmail(email) {
    const emailRegex = /^[a-za-z0-9_.]+@[a-za-z0-9_]+\.[a-z]{2,}$/;
    return emailRegex.test(email);
}


/**
 * Checks if the password is valid and sets custom validity message if not
 * @param {Element} passwordInput1 The first password input field
 * @param {Element} passwordInput2 The second password input field
 * @returns {boolean} true if the password is valid, false otherwise
 */
function validatePassword(passwordInput1, passwordInput2) { 
    const specialChars = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?\s]+/;
    if (!specialChars.test(passwordInput1.value)) {
        formFieldHasError(passwordInput1.parentElement, 'Password must contain at least 1 special character');
        return false;
    }
    if (!/\d/.test(passwordInput1.value)) {
        formFieldHasError(passwordInput1.parentElement, 'Password must contain a number');
        return false;
    }
    if (/^\d$/.test(passwordInput1.value)) {
        formFieldHasError(passwordInput1.parentElement, 'Password cannot be all numbers');
        return false;
    }
    if (passwordInput1.value.length < 8) {
        formFieldHasError(passwordInput1.parentElement, 'Password must be at least 8 characters');
        return false;
    }
    if (passwordInput1.value !== passwordInput2.value) {
        formFieldHasError(passwordInput2.parentElement, 'Passwords do not match');
        return false;
    } 
    return true;
}


