const passwordChangeForm = document.querySelector('#change-password-form');
const passwordChangeFormCard = passwordChangeForm.parentElement;
const changePasswordButton = passwordChangeForm.querySelector('.submit-btn');
const passwordField1 = passwordChangeForm.querySelector('#new-password1');
const passwordField2 = passwordChangeForm.querySelector('#new-password2');


addOnPostAndOnResponseFuncAttr(changePasswordButton, 'Updating password...');

passwordChangeForm.addEventListener('keyup', function(e) {
    changePasswordButton.disabled = false;
});

passwordChangeForm.addEventListener('change', function(e) {
    changePasswordButton.disabled = false;
});


passwordChangeForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!validatePassword(passwordField1, passwordField2)) return;

    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    changePasswordButton.onPost();
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(data),
    }

    fetch(this.action, options).then((response) => {
        if (!response.ok) {
            changePasswordButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if (errors){
                    console.log(errors )
                    if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = this.querySelector(`*[name=${fieldName}]`);
                        formFieldHasError(field.parentElement, msg);
                    };

                }else{
                    pushNotification("error", data.detail ?? 'An error occurred!');
                };
            });

        }else{
            changePasswordButton.onResponse();
            changePasswordButton.disabled = true;

            response.json().then((data) => {
                pushNotification("success", data.detail ?? 'Password updated successfully!');
            });
            
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        }
    });
};

