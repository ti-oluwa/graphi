const createStoreToggle = document.querySelector('#create-store-toggle');
const createStoreForm = document.querySelector('#create-store-form');
const createStoreFormCard = createStoreForm.parentElement;
const createStoreButton = createStoreForm.querySelector('.submit-btn');
const emailField = createStoreForm.querySelector('#email');


createStoreToggle.onclick = () => {
    createStoreFormCard.classList.add('show-block');
};

document.addEventListener('click', (e) => {
    if (!createStoreToggle.contains(e.target) && !createStoreFormCard.contains(e.target)){
        createStoreFormCard.classList.remove('show-block');
    };
});

addOnPostAndOnResponseFuncAttr(createStoreButton, 'Creating Store...');


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
        createStoreButton.onResponse();
        if (!response.ok) {
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if (errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")
    
                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = this.querySelector(`input[name=${fieldName}]`);
                        formFieldHasError(field.parentElement, msg);
                    };
                };
    
                alert(data.detail ?? 'An error occurred while creating store!')
            });

        }else{
            window.location.reload();
        }
    });
};

