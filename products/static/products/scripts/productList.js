const productCards = document.querySelectorAll('.product-card');
const addProductToggle = document.querySelector('#add-product-toggle');
const addProductForm = document.querySelector('#add-product-form');
const addProductFormCard = addProductForm.parentElement;
const addProductButton = addProductForm.querySelector('.submit-btn');


productCards.forEach((card) => {
    let cardMain = card.querySelector('.product-card-main');
    let cardExtras = card.querySelector('.product-card-extras');

    cardMain.addEventListener('click', () => {
        cardExtras.classList.toggle('show-flex');
        for(let i = 0; i < productCards.length; i++) {
            if(productCards[i] !== card) {
                productCards[i].querySelector('.product-card-extras').classList.remove('show-flex');
            }
        }
    });
});


addProductToggle.onclick = () => {
    addProductFormCard.classList.add('show-block');
};

document.addEventListener('click', (e) => {
    if (!addProductToggle.contains(e.target) && !addProductFormCard.contains(e.target)){
        addProductFormCard.classList.remove('show-block');
    };
});

addOnPostAndOnResponseFuncAttr(addProductButton, 'Adding Product...');


addProductForm.onsubmit = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

    addProductButton.onPost();
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
            addProductButton.onResponse();
            response.json().then((data) => {
                const errors = data.errors ?? null;
                if (errors){
                    if(!typeof errors === Object) throw new TypeError("Invalid data type for 'errors'")
    
                    for (const [fieldName, msg] of Object.entries(errors)){
                        let field = this.querySelector(`*[name=${fieldName}]`);
                        formFieldHasError(field.parentElement, msg);
                    };

                }else{
                    alert(data.detail ?? 'An error occurred!');
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

