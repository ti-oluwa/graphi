const mostSoldProductForm = document.querySelector('#most-sold-product-form');
const statValueElementMSP = mostSoldProductForm.previousElementSibling;
const miscStatValueElementMSP = mostSoldProductForm.parentElement.previousElementSibling.querySelector('.stat-value-misc');


mostSoldProductForm.onchange = function(e) {
    e.stopImmediatePropagation();
    e.preventDefault();

    const formData = new FormData(this);
    const data = {};
    for (const [key, value] of formData.entries()) {
        data[key] = value;
    }

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
            response.json().then((data) => {
                pushNotification("error", data.detail ?? 'An error occurred!');
            });

        }else{
            response.json().then((data) => {
                const responseData = data.data;
                const mostSoldProduct = responseData.mostSoldProduct ?? null;
                if (mostSoldProduct){
                    statValueElementMSP.innerHTML = mostSoldProduct.name;
                    miscStatValueElementMSP.innerHTML = `${mostSoldProduct.store} - ${mostSoldProduct.totalQuantitySold} units sold`

                }else{
                    statValueElementMSP.innerHTML = 'No data';
                    miscStatValueElementMSP.innerHTML = 'No data';
                }
            });
        }
    });
};

