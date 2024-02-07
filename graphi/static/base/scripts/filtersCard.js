const filtersCard = document.querySelector('.filters-card');
const filtersCardCloseBtn = filtersCard.querySelector('.close-card');
const filtersCardApplyBtn = filtersCard.querySelector('.apply-btn');
const filtersCardForm = filtersCard.querySelector('#filter-form');
const filtersCardDateInput = filtersCardForm.querySelector('fieldset.date-filter input');
const filtersCardDateRangeInputs = filtersCardForm.querySelectorAll('fieldset.date-range-filter input');
const filtersCardFormFieldsets = filtersCardForm.querySelectorAll("fieldset");


/**
 * Updates the filters card title
 * @param {string} title The title to update the filters card with
 */
function updateFiltersCardTitle(title){
    filtersCard.querySelector('.card-title').textContent = title;
};


filtersCard.show = function() {
    this.classList.add('show-flex');
};


filtersCard.close = function() {
    this.classList.remove('show-flex');
};


/**
 * Returns the title of the filters card
 * @returns {string} The title of the filters card
 */
filtersCard.getTitle = function() {
    return this.querySelector('.card-title').textContent;
};


/**
 * Parses out the data from a filters card form fieldset
 * @param {HTMLFieldSetElement} fieldset 
 * @returns {*} The fieldset's data
 */
function getFieldsetData(fieldset){
    const fieldsetInputs = fieldset.querySelectorAll('input');
    const fieldsetType = fieldsetInputs[0].type;

    let data;
    if (fieldsetType == "checkbox"){
        data = [];
        fieldsetInputs.forEach(checkbox => {
            if (checkbox.checked){
                data.push(checkbox.name);
            };
        });

    }else{
        data = {}
        fieldsetInputs.forEach(input => {
            if (!input.disabled){
                data[input.name] = input.value;
            };
        });
    }
    return data;
};


/**
 * Returns a form data that is ready to be sent for processing
 * @param {object} formData The filters form data
 * @returns {object} form data ready for processing
 */
function cleanFiltersFormData(formData){
    const cleanedData = {};
    for (let key in formData){
        let value = formData[key];
        if(!value) continue;
        
        if (!Array.isArray(value) || !typeof value === "string"){
            let newValue = underScoreObjectKeys(value);
            Object.assign(cleanedData, newValue)
        }else{
            cleanedData[key] = value;
        }
    }
    return cleanedData;
}


/**
 * Returns the filters form data
 */
filtersCardForm.getData = () => {
    const data = {};
    filtersCardFormFieldsets.forEach(fieldset => {
        data[fieldset.dataset.name] = getFieldsetData(fieldset);
    });
    return cleanFiltersFormData(data);
};


filtersCardCloseBtn.addEventListener('click', () => {
    filtersCard.close();
});


if (filtersCardDateInput){
    filtersCardDateRangeInputs.forEach(input => {
        input.addEventListener('input', () => {
            if(input.value){
                filtersCardDateInput.value = null;
                filtersCardDateInput.disabled = true;
            }else{
                filtersCardDateInput.disabled = false;
            }
        });
    });
};


