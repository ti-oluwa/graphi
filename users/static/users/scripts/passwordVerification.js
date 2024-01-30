const passwordVerificationForm = document.querySelector('#password-verification-form');
const passwordVerificationFormCard = passwordVerificationForm.parentElement;
const passwordField = passwordVerificationForm.querySelector('input#password');
const verifyButton = passwordVerificationForm.querySelector('button.submit-btn');


function getPasswordVerificationFormData() {
    let formData = new FormData(passwordVerificationForm);
    return {
        password: formData.get('password'),
    }
}

addOnPostAndOnResponseFuncAttr(verifyButton, "Verifying...");

passwordVerificationForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    verifyButton.onPost();
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(getPasswordVerificationFormData()),
    }

    fetch(window.location.href, options).then((response) => {
        if (!response.ok) {
            verifyButton.onResponse();
            response.json().then((data) => {
                const errorDetail = data.detail ?? null;
                pushNotification("error", errorDetail ?? 'An error occurred!');
            });

        }else{
            response.json().then((data) => {
                pushNotification("success", data.detail ?? 'Password verification successful!');
                const redirectURL  = data.redirect_url ?? null;

                if(!redirectURL) return;
                window.location.href = redirectURL;
            });
        }
    });
    
}
