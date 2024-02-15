const createStoreToggle = document.querySelector('#create-store-toggle');
const createStoreForm = document.querySelector('#create-store-form');
const createStoreFormCard = createStoreForm.parentElement;
const createStoreButton = createStoreForm.querySelector('.submit-btn');
const emailField = createStoreForm.querySelector('#email');
const cardOptionsContainers = document.querySelectorAll('.card-options');


createStoreToggle.onclick = () => {
    createStoreFormCard.classList.add('show-block');
};


document.addEventListener('click', (e) => {
    if (!createStoreToggle.contains(e.target) && !createStoreFormCard.contains(e.target)){
        createStoreFormCard.classList.remove('show-block');
    };
});

if (cardOptionsContainers) {
    cardOptionsContainers.forEach((container) => {
        let storeCard = container.parentElement;
        storeCard.addEventListener("pointerenter", (e) => {
            // if the container is already showing, don't do anything
            if (container.classList.contains('show-flex')) return;

            container.classList.add('show-flex');
            setTimeout(() => {
                container.classList.remove('show-flex');
            }, 3000);
        });

        container.addEventListener("pointerleave", (e) => {
            container.classList.remove('show-flex');
        });
    });
}


addOnPostAndOnResponseFuncAttr(createStoreButton, 'Creating store...');


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
        if (!response.ok) {
            createStoreButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if(errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")
    
                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = this.querySelector(`*[name=${fieldName}]`);
                        if(!field){
                            pushNotification("error", msg);
                            continue;
                        }
                        formFieldHasError(field.parentElement, msg);
                    };

                }else{
                    pushNotification("error", data.detail ?? 'An error occurred!');
                };
            });

        }else{
            response.json().then((data) => {
                pushNotification("success", data.detail);
                const redirectURL  = data.redirect_url ?? null;

                if(!redirectURL) return;
                window.location.href = redirectURL;
            });
        }
    });
};

