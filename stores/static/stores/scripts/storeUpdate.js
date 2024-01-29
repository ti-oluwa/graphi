const updateStoreForm = document.querySelector('#update-store-form');
const updateStoreFormCard = updateStoreForm.parentElement;
const updateStoreButton = updateStoreForm.querySelector('.submit-btn');
const emailField = updateStoreForm.querySelector('#email');


addOnPostAndOnResponseFuncAttr(updateStoreButton, 'Updating Store...');

updateStoreForm.onchange = function(e) {
    updateStoreButton.disabled = false;
};

updateStoreForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    if (!isValidEmail(emailField.value)) {
        formFieldHasError(emailField.parentElement, 'Invalid email address!');
        return;
    }
    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    updateStoreButton.onPost();
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
            updateStoreButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if (errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = this.querySelector(`*[name=${fieldName}]`);
                        formFieldHasError(field.parentElement, msg);
                    };

                }else{
                    alert(data.detail ?? 'An error occurred!');
                };
            });

        }else{
            response.json().then((data) => {
                const redirectURL  = data.redirect_url ?? null;

                if(!redirectURL) return;
                window.location.href = redirectURL;
            });
        }
    });
};
