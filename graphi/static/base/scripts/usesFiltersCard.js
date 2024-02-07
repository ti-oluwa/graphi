const filtersCardToggle = document.querySelector('#filters-toggle');


filtersCardToggle.onclick = function(e) {
    filtersCard.show();
}

filtersCardApplyBtn.addEventListener("click", () => {
    filtersCardForm.checkValidity();
    filtersCardForm.reportValidity();
    if (!filtersCardForm.checkValidity()) return;

    const formData = JSON.parse(JSON.stringify(filtersCardForm.getData()));
    // Remove empty fields and arrays
    for (const [key, value] of Object.entries(formData)){
        if (!value || value.length === 0){
            delete formData[key];
        }
    };
    // Encode the data to be used in the URL. List items should be separated by commas
    for (const [key, value] of Object.entries(formData)){
        if (Array.isArray(value)){
            formData[key] = value.join(',');
        };
    };
    const queryParam = new URLSearchParams(formData).toString();
    const newURL = `${window.location.pathname}?${queryParam}`;
    window.location.href = newURL;
});
