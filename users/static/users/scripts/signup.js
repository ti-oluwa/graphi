
const signUpForm = document.querySelector('#signup-form');
const signUpButton = document.querySelector('#signup-form #submit-btn');
const emailField = document.querySelector('#signup-form #email');
const passwordField1 = document.querySelector('#signup-form #password1');
const passwordField2 = document.querySelector('#signup-form #password2');


signUpButton.onPost = function(){
    this.disabled = true;
    this.innerHTML = 'Please wait...';
}


signUpButton.onResponse = function(){
    this.disabled = false;
    this.innerHTML = 'Sign Up';
}


signUpForm.onsubmit = (e) => {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!isValidEmail(emailField.value)) {
        formFieldHasError(emailField.parentElement, 'Invalid email address!');
        return;
    }
    if (!validatePassword(passwordField1, passwordField2)) return;
    
    const formData = new FormData(signUpForm);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }
    data['timezone'] = getClientTimezone();

    signUpButton.onPost();

    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }

    fetch(signUpForm.action, options).then((response) => {
        signUpButton.onResponse();
        if (!response.status === 201) {
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if (!errors) return;
                if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                for (const [fieldName, msg] of Object.entries(errors)){
                    let field = signUpForm.querySelector(`input[name=${fieldName}]`);
                    formFieldHasError(field.parentElement, msg);
                }
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
