const mostActiveStoreForm = document.querySelector('#most-active-store-form');
const statValueElementMAS = mostActiveStoreForm.previousElementSibling;
const miscStatValueElementMAS = mostActiveStoreForm.parentElement.previousElementSibling.querySelector('.stat-value-misc');


mostActiveStoreForm.onchange = function(e) {
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
                const mostActiveStore = responseData.mostActiveStore ?? null;
                if (mostActiveStore){
                    statValueElementMAS.innerHTML = mostActiveStore.name;
                    miscStatValueElementMAS.innerHTML = `${mostActiveStore.salesCount} sales made`

                }else{
                    statValueElementMAS.innerHTML = 'No data';
                    miscStatValueElementMAS.innerHTML = 'No data';
                }
            });
        }
    });
};

