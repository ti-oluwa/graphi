const updateStoreFormCard = document.querySelector('#form-card');
const updateStoreForm = document.querySelector('#update-store-form');
const updateStoreButton = document.querySelector('#update-store-form #submit-btn');
const emailField = document.querySelector('#update-store-form #email');


updateStoreButton.onPost = function(){
    this.disabled = true;
    this.innerHTML = 'Updating Store...';
}

updateStoreButton.onResponse = function(){
    this.disabled = false;
    this.innerHTML = 'Update Store';
}

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
    $.ajax({
        url: this.action,
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(data),
        headers: {'X-CSRFToken': getCookie('csrftoken')},

        success: (response) => {
            const data = JSON.parse(response.detail)
            if(response.status === 'success'){
                window.location.href = data.redirect_url
            };
        },
        error: (response) => {
            updateStoreButton.onResponse();
            const data = JSON.parse(response.detail)
            const errors = data.errors ?? null;
            if (errors){
                if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")

                for (const [fieldName, msg] of Object.entries(errors)){
                    let field = this.querySelector(`input[name=${fieldName}]`);
                    formFieldHasError(field.parentElement, msg);
                };
            };
            alert(data.detail ?? 'An error occurred while updating store!')
        }
    });
};
