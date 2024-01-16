const storeCards = document.querySelectorAll('#stores-wrapper .store-card');

storeCards.forEach((card) => {
    const editStoreToggle = card.querySelector('.edit-store-toggle');
    const editStoreForm = card.querySelector('.edit-store-form');
    const editStoreButton = editStoreForm.querySelector('#submit-btn');
    const editStoreFormCard = editStoreForm.parentElement;

    editStoreToggle.onclick = () => {
        editStoreFormCard.classList.add('show-block');
    };

    document.addEventListener('click', (e) => {
        if (!editStoreToggle.contains(e.target) && !editStoreFormCard.contains(e.target)){
            editStoreFormCard.classList.remove('show-block');
        };
    });

    editStoreButton.onPost = function(){
        this.disabled = true;
        this.innerHTML = 'Updating Store...';
    }
    
    editStoreButton.onResponse = function(){
        this.disabled = false;
        this.innerHTML = 'Update Store';
    }
});




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
