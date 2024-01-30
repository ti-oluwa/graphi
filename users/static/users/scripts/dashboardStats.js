const advancedOptionsToggles = document.querySelectorAll('.stat-card .more-options')
const advancedOptionsCards = document.querySelectorAll('.stat-card .options-card')
const advancedOptionsProcessURL = window.location.href + 'stats/advanced-options/'


/**
 * Parses advanced options form and returns the form data
 * @param {*} advancedOptionsForm 
 * @returns {object} The form data
 */
function getAdvancedOptionsFormData(advancedOptionsForm){
    const data = {};
    const storeOptionsFieldset = advancedOptionsForm.querySelector('fieldset.store-options');
    const categoryOptionsFieldset = advancedOptionsForm.querySelector('fieldset.category-options');
    const dateOptionFieldset = advancedOptionsForm.querySelector('fieldset.date-option');
    const timeRangeOptionFieldset = advancedOptionsForm.querySelector('fieldset.time-range-option');
    const dateRangeOptionFieldset = advancedOptionsForm.querySelector('fieldset.date-range-option');

    // For store options
    let storeOptions = [];
    const storeOptionsFieldsetInputs = storeOptionsFieldset.querySelectorAll('input');
    storeOptionsFieldsetInputs.forEach(input => {
        if(input.checked){
            storeOptions.push(input.name);
        }
    });
    data['store_pks'] = storeOptions;

    // For category options
    let categoryOptions = [];
    const categoryOptionsFieldsetInputs = categoryOptionsFieldset.querySelectorAll('input');
    categoryOptionsFieldsetInputs.forEach(input => {
        if(input.checked){
            categoryOptions.push(input.value);
        }
    });
    data['categories'] = categoryOptions;

    // For date option
    let dateInput = dateOptionFieldset.querySelector('input');
    if (dateInput.value){
        data['date'] = dateInput.value;
    };

    // For time range option
    let fromTimeInput = timeRangeOptionFieldset.querySelector('input#from-time');
    let toTimeInput = timeRangeOptionFieldset.querySelector('input#to-time');
    if (fromTimeInput.value){
        data['from_time'] = fromTimeInput.value;
    };
    if (toTimeInput.value){
        data['to_time'] = toTimeInput.value;
    };

    // For date range option
    let fromDateInput = dateRangeOptionFieldset.querySelector('input#from-date');
    let toDateInput = dateRangeOptionFieldset.querySelector('input#to-date');
    if (fromDateInput.value){
        data['from_date'] = fromDateInput.value;
    };
    if (toDateInput.value){
        data['to_date'] = toDateInput.value;
    };

    return data;
}


/**
 * Sends form data to the server and returns the result
 * @param {string} processURL The url to send the form data to for processing
 * @param {*} formData The form data to send to the server
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
 * Processes advanced options form and returns the result
 * @param {string} processURL The url to send the form data to for processing
 * @param {HTMLFormElement} advancedOptionsForm The advanced options form to process
 * @param {function} callback The callback function to run after processing the form
 * @returns {object} result 
 */
function processadvancedOptionsForm(processURL, advancedOptionsForm, callback){
    advancedOptionsForm.checkValidity();
    
    const formData = getAdvancedOptionsFormData(advancedOptionsForm);
    if (advancedOptionsForm.id === 'sales-stat-form'){
        formData['stat_type'] = "sales";
    }else{
        formData['stat_type'] = "revenue";
    }

    return processFormData(processURL, formData, callback);
}


advancedOptionsToggles.forEach(toggle => {
    let advancedOptionsCard = toggle.parentElement.nextElementSibling
    toggle.addEventListener('click', () => {
        advancedOptionsCard.classList.add('show-flex');
        advancedOptionsCard.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
        });
    });

    let cardClosetoggle = advancedOptionsCard.querySelector('.close-card');
    cardClosetoggle.addEventListener('click', () => {
        advancedOptionsCard.classList.remove('show-flex');
    });
});


advancedOptionsCards.forEach(card => {
    let resultElement = card.previousElementSibling.querySelector('h1')
    let applyBtn = card.querySelector('.apply-btn');
    let advancedOptionsForm = applyBtn.parentElement.nextElementSibling;
    let dateInput = advancedOptionsForm.querySelector('fieldset.date-option input');
    let dateRangeInputs = advancedOptionsForm.querySelectorAll('fieldset.date-range-option input');

    let callback = (result) => {
        resultElement.textContent = result;
    }

    applyBtn.addEventListener('click', () => {
        processadvancedOptionsForm(advancedOptionsProcessURL, advancedOptionsForm, callback);
    });

    dateRangeInputs.forEach(input => {
        input.addEventListener('input', () => {
            if(input.value){
                dateInput.value = null;
                dateInput.disabled = true;
            }else{
                dateInput.disabled = false;
            }
        });
    });

})


document.addEventListener('click', (e) => {

    advancedOptionsCards.forEach(card => {
        if (!card.contains(e.target) && !card.parentElement.contains(e.target)) {
            card.classList.remove('show-flex');
        }
    });
    
});
