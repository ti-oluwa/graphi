const accountUpdateForm = document.querySelector('#account-update-form');
const accountUpdateFormCard = accountUpdateForm.parentElement;
const accountUpdateButton = accountUpdateForm.querySelector('.submit-btn');
const emailField = accountUpdateForm.querySelector('#email');
const autoSelectTimezoneButton = accountUpdateForm.querySelector('#auto-timezone');
const storeSelectFormCard = document.querySelector('#store-select-form-card');
const storeSelectToggle = document.querySelector('#store-select-toggle');


addOnPostAndOnResponseFuncAttr(accountUpdateButton, 'Saving changes...');

accountUpdateForm.addEventListener('keyup', function(e) {
    accountUpdateButton.disabled = false;
});

accountUpdateForm.addEventListener('change', function(e) {
    accountUpdateButton.disabled = false;
});


autoSelectTimezoneButton.onclick = function() {
    const timezoneField = accountUpdateForm.querySelector('select#timezone');
    const timezone = getClientTimezone();
    var ss = $(timezoneField).selectize();
    var selectize = ss[0].selectize;
    selectize.setValue(selectize.search(timezone).items[0].id);
};

storeSelectToggle.onclick = function() {
    storeSelectFormCard.classList.add("show-block");
}

document.addEventListener('click', (e) => {
    if (!storeSelectToggle.contains(e.target) && !storeSelectFormCard.contains(e.target)){
        storeSelectFormCard.classList.remove('show-block');
    };
});


accountUpdateForm.onsubmit = function(e) {
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

    accountUpdateButton.onPost();
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
            accountUpdateButton.onResponse();
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
            accountUpdateButton.onResponse();
            accountUpdateButton.disabled = true;

            response.json().then((data) => {
                pushNotification("success", data.detail ?? 'Account updated successfully!');
            });
        }
    });
};

