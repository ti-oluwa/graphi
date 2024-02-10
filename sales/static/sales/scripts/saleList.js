const addSaleForm = document.querySelector('#add-sale-form');
const addSaleFormCard = addSaleForm.parentElement;
const addSaleButton = addSaleForm.querySelector('.submit-btn');


addOnPostAndOnResponseFuncAttr(addSaleButton, 'Recording sale...');


addSaleForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    addSaleButton.onPost();
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
            addSaleButton.onResponse();
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
                pushNotification("success", data.detail ?? 'Sale recorded successfully!');
                const redirectURL  = data.redirect_url ?? null;

                if(!redirectURL) return;
                window.location.href = redirectURL;
            });
        }
    });
};

