const updateProductForm = document.querySelector('#update-product-form');
const updateProductFormCard = updateProductForm.parentElement;
const updateProductButton = updateProductForm.querySelector('.submit-btn');


addOnPostAndOnResponseFuncAttr(updateProductButton, 'Updating Product...');

updateProductForm.onchange = function(e) {
    updateProductButton.disabled = false;
};

updateProductForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    updateProductButton.onPost();
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
            updateProductButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if (errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")

                    for (const [fieldName, msg] of Object.entries(errors)){
                        console.log(fieldName)
                        let field = this.querySelector(`*[name=${fieldName}]`);
                        formFieldHasError(field.parentElement, msg);
                    };
                    
                }else{
                    alert(data.detail ?? 'An error occured!');
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