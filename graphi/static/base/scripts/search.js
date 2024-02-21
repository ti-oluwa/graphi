const headerSearch = document.querySelector('input#header-search');
const headerSearchForm = headerSearch.parentElement;


/**
 * Disables the header search input
 */
function disableHeaderSearch(){
    headerSearch.disabled = true;
    headerSearchForm.classList.add("remove");
}

/**
 * Parses the query parameters from a url and returns them in an object
 * @param {string} url The url to parse
 * @returns {object} An object containing the query parameters if any
 */
function parseURLParams(url){
    const query = url.split('?')[1];
    if (query) {
        return query.split('&').reduce((acc, param) => {
            const [key, value] = param.split('=');
            acc[key] = value;
            return acc;
        }, {});
    }
    return {};
}


headerSearchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const searchQuery = headerSearch.value;
    if (searchQuery) {
        const pageURL = window.location.href.split('?')[0];
        const queryParams = parseURLParams(window.location.href);
        queryParams["query"] = searchQuery;
        const URLparams = new URLSearchParams(queryParams).toString();
        window.location.href = `${pageURL}?${URLparams}`;
    }
});


function setHeaderSearchTitle(title){
    headerSearchForm.title = title;
}
