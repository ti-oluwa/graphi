
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
 * Gets the element that displays messages for the field
 * @param {Element} field The input field
 * @returns The message element of the field
 */
function getMsgEl(field) {
    if (!field.classList.contains('form-input')) {
        throw new Error('Field must have class "form-input"');
    }
    return field.parentElement.querySelector('.field-message');
}


/**
 * Sets and displays the error message for the field
 * @param {Element} field The input field that has an error
 * @param {string} errorMsg The error message to display
 */
function fieldHasError(field, errorMsg) {
    const msgEl = getMsgEl(field);
    if (!msgEl) throw new Error('Field must have a message element with class "field-message"');

    msgEl.innerHTML = errorMsg;
    field.classList.add('invalid-field');
    field.addEventListener('input', () => {
        field.classList.remove('invalid-field');
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
 * @param {Element} passwordField1 The first password field
 * @param {Element} passwordField2 The second password field
 * @returns {boolean} true if the password is valid, false otherwise
 */
function validatePassword(passwordField1, passwordField2) { 
    const specialChars = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?\s]+/;
    if (!specialChars.test(passwordField1.value)) {
        fieldHasError(passwordField1, 'Password must contain at least 1 special character');
        return false;
    }
    if (!/\d/.test(passwordField1.value)) {
        fieldHasError(passwordField1, 'Password must contain a number');
        return false;
    }
    if (/^\d$/.test(passwordField1.value)) {
        fieldHasError(passwordField1, 'Password cannot be all numbers');
        return false;
    }
    if (passwordField1.value.length < 8) {
        fieldHasError(passwordField1, 'Password must be at least 8 characters');
        return false;
    }
    if (passwordField1.value !== passwordField2.value) {
        fieldHasError(passwordField2, 'Passwords do not match');
        return false;
    } 
    return true;
}


