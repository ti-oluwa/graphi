const createStoreToggle = document.querySelector('#create-store-toggle');
const createStoreFormCard = document.querySelector('#form-card');
const createStoreForm = document.querySelector('#create-store-form');
const createStoreButton = document.querySelector('#create-store-form #submit-btn');
const emailField = document.querySelector('#create-store-form #email');


createStoreToggle.onclick = () => {
    createStoreFormCard.classList.add('show-block');
};

document.addEventListener('click', (e) => {
    if (!createStoreToggle.contains(e.target) && !createStoreFormCard.contains(e.target)){
        createStoreFormCard.classList.remove('show-block');
    };
});

createStoreButton.onPost = function(){
    this.disabled = true;
    this.innerHTML = 'Creating Store...';
}

createStoreButton.onResponse = function(){
    this.disabled = false;
    this.innerHTML = 'Create Store';
}

createStoreForm.onsubmit = function(e) {
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

    createStoreButton.onPost();
    $.ajax({
        url: this.action,
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        success: (response) => {
            if(response.status === 'success'){
                window.location.reload();
            };
        },
        error: (response) => {
            createStoreButton.onResponse();
            const errors = response.errors ?? null;
            if (!errors) return;
            if(!typeof errors === Object) throw new TypeError("Invalid response type for 'errors'")

            for (const [fieldName, msg] of Object.entries(errors)){
                let field = this.querySelector(`input[name=${fieldName}]`);
                formFieldHasError(field.parentElement, msg);
            };
        }
    });
};
