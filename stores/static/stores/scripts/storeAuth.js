const storePasskeyForm = document.querySelector('#store-passkey-form');
const storePasskeyFormCard = storePasskeyForm.parentElement;
const passkeyField = storePasskeyForm.querySelector('input#passkey');
const authorizeButton = storePasskeyForm.querySelector('button.submit-btn');

/**
 * Retrieves the passkey from the store passkey form
 * @returns {object} an object containing the passkey
 */
function getStorePasskeyFormData() {
    let formData = new FormData(storePasskeyForm);
    return {
        passkey: formData.get('passkey'),
    }
}

addOnPostAndOnResponseFuncAttr(authorizeButton, "Authorizing...");

storePasskeyForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    authorizeButton.onPost();
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(getStorePasskeyFormData()),
    }

    fetch(window.location.href, options).then((response) => {
        if (!response.ok) {
            authorizeButton.onResponse();
            response.json().then((response) => {
                const data = JSON.parse(response.detail);
                const errorDetail = data.detail ?? null;

                if(!errorDetail) return;
                formFieldHasError(passkeyField.parentElement, errorDetail);
            });

        }else{
            response.json().then((response) => {
                const data = JSON.parse(response.detail);
                const redirectURL  = data.redirect_url ?? null;

                if(!redirectURL) return;
                window.location.href = redirectURL;
            });
        }
    });
    
}
