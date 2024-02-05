const storeFieldset = filtersCardForm.querySelector('fieldset.store-filters');
const storeFieldsetCheckboxes = storeFieldset.querySelectorAll('input[type=checkbox]');

const filtersCardToggles = document.querySelectorAll('.stat-card .more-options');
const filtersProcessURL = window.location.href + 'stats/advanced-options/';


filtersCardToggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
        updateFiltersCardTitle(toggle.dataset.title);
        filtersCard.show();
    });
});


/**
 * Disable all input in the filters card except those in excludedFieldset
 * @param {boolean} disable Disables inputs if true;
 * @param {*} excludeFieldset fieldset whose input will be excluded
 */
function disableFiltersCardInputs(disable, excludedFieldset){
    filtersCardFormFieldsets.forEach(fieldset => {
        if (fieldset != excludedFieldset){
            const fieldsetInputs = fieldset.querySelectorAll('input');
            fieldsetInputs.forEach(input => {
                input.disabled = disable;
            });
        };
    });
};


filtersCardForm.addEventListener("change", () => {
    let hasStoreChecked = false;
    for (let i = 0; i < storeFieldsetCheckboxes.length; i++){
        hasStoreChecked = storeFieldsetCheckboxes[i].checked;
        if (hasStoreChecked) break;
    };

    if(!hasStoreChecked){
        disableFiltersCardInputs(true, storeFieldset);
    }else{
        disableFiltersCardInputs(false, storeFieldset);
    }
});


/**
 * Returns a a form data that is ready to be sent to the filters processing URL
 * @param {object} formData The filters form data
 * @returns {object} form data ready for processing
 */
function cleanFiltersFormData(formData){
    const cleanedData = {};
    for (let key in formData){
        let value = formData[key];
        if(!value) continue;
        
        if (!Array.isArray(value)){
            let newValue = underScoreObjectKeys(value);
            Object.assign(cleanedData, newValue)
        }else{
            cleanedData[key] = value;
        }
    }
    return cleanedData;
}


/**
 * Sends form data to the server and returns the result
 * @param {string} processURL The url to send the form data to for processing
 * @param {object} formData The form data to send to the server
 * @param {function} callback The callback function to run after processing the form
 * @returns {object} result
 */
function processFormData(processURL, formData, callback){
    const options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        mode: 'same-origin',
        body: JSON.stringify(formData),
    }

    fetch(processURL, options).then((response) => {
        if (!response.ok) {
            response.json().then((data) => {
                const errorDetail = data.detail ?? null;
                pushNotification("error", errorDetail ?? 'An error occurred!');
            });

        }else{
            response.json().then((data) => {
                const result  = data.data.result ?? null;
                if(result === null) return;
                callback(result);
            });
        }
    });
};


/**
 * Processes filters selected in the filters form and returns the result
 * @param {string} processURL The url to send the form data to for processing
 * @param {HTMLFormElement} filtersForm The filters form to process
 * @param {function} callback The callback function to pass the result of the form processing to
 * @returns {object} result 
 */
function processFilters(processURL, filtersForm, callback){
    
    const formData = cleanFiltersFormData(filtersForm.getData());
    if (filtersForm.dataset.stattype === 'sales'){
        formData['statType'] = "sales";
    }else{
        formData['statType'] = "revenue";
    }

    return processFormData(processURL, formData, callback);
}


/**
 * Makes a result callback function that updates the result element with the result
 * @param {HTMLElement} resultElement The element whose text content will be updated with the result
 * @returns callback function
 */
function makeResultCallback(resultElement){
    return (result) => {
        resultElement.textContent = result;
    };
}

filtersCardApplyBtn.addEventListener('click', () => {
    filtersCardForm.checkValidity();
    filtersCardForm.reportValidity();
    if (!filtersCardForm.checkValidity()) return;

    let resultElement;
    if(filtersCard.getTitle().includes("sales")){
        filtersCardForm.dataset.stattype = "sales";
        resultElement = document.querySelector('.stat-card#sales-card .stat-value');
    }else{
        filtersCardForm.dataset.stattype = "revenue";
        resultElement = document.querySelector('.stat-card#revenue-card .stat-value');
    }

    const callback = makeResultCallback(resultElement);
    processFilters(filtersProcessURL, filtersCardForm, callback);
    filtersCard.close();
});

