
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
        if (response.status !== 201) {
            signUpButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if(errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = signUpForm.querySelector(`input[name=${fieldName}]`);
                        if(!field){
                            pushNotification("error", msg);
                            continue;
                        }
                        formFieldHasError(field.parentElement, msg);
                    };

                }else{
                    pushNotification("error", data.detail ?? 'An error occurred!');
                }
            });
            
        }else{
            response.json().then((data) => {
                pushNotification("success", data.detail ?? 'Sign up successful!');
                const redirectURL  = data.redirect_url ?? null
                if(!redirectURL) return;
                
                setTimeout(() => {
                    window.location.href = redirectURL;
                }, 3000);
            });
        }
    });
};
