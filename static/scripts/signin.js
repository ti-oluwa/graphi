
const signInForm = document.querySelector('#signin-form');
const signInButton = document.querySelector('#signin-form #submit-btn');
const emailField = document.querySelector('#signin-form #email');
const passwordField = document.querySelector('#signin-form #password');

const signInURL = "/signin/";

signInForm.onPost = function(){
    signInButton.disabled = true;
    signInButton.innerHTML = 'Signing in...';
}


signInForm.onResponse = function(){
    signInButton.disabled = false;
    signInButton.innerHTML = 'Sign In';
}


signInForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!isValidEmail(emailField.value)) {
        fieldHasError(emailField, 'Invalid email address!');
        return;
    }
    
    const formData = new FormData(signInForm);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    signInForm.onPost();

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }

    fetch(signInURL, options).then((response) => {
        signInForm.onResponse();
        if (!response.ok) {
            response.json().then((data) => {
                const errorDetail = data.detail ?? null
                if(!errorDetail) return;
                fieldHasError(passwordField, errorDetail);
            });
        }else{
            response.json().then((data) => {
                const redirectURL  = data.redirect_url ?? null
                if(!redirectURL) return;
                window.location.href = redirectURL;
            });
        }
    });
};
