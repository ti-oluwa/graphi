const storePasskeyForm = document.getElementById('store-passkey-form');

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
