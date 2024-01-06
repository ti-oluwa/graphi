const signUpForm = document.querySelector('#signup-form');
const signUpButton = document.querySelector('#signup-form #submit-btn');
const timezoneField = document.querySelector('#signup-form #timezone');
const passwordField1 = document.querySelector('#signup-form #password1');
const passwordField2 = document.querySelector('#signup-form #password2');


/**
 * Gets the timezone of the client
 * @returns {string} the timezone of the client
 */
function getClientTimezone() {
    return Intl.DateTimeFormat().resolvedOptions().timeZone;
}


/**
 * Checks if the password is valid and sets custom validity message if not
 * @returns {boolean} true if the password is valid, false otherwise
 */
function validatePassword() {
    if (passwordField1.value !== passwordField2.value) {
        passwordField2.setCustomValidity('Passwords do not match');
        passwordField2.reportValidity();
        return false;
    } else {
        passwordField2.setCustomValidity('');
        return true;
    }
}

signUpForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();
    console.log(getTimezone());
    if (!validatePassword()){
        return;
    };

    signUpButton.disabled = true;
    signUpButton.innerHTML = 'Please wait...';
    const formData = new FormData(signUpForm);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    data['timezone'] = getClientTimezone();

    fetch('/signup/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        credentials: 'include',
    }).then((response) => {
        if (response.ok) {
            response.json().then((data) => {
                window.location.href = data['redirect_url'];
            });
        } else {
            response.json().then((data) => {
                signUpButton.disabled = false;
                signUpButton.innerHTML = 'Sign Up';
                alert(data['detail']);
            });
        }
    });
};
