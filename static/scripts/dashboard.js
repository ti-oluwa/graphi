const moreOptionsToggles = document.querySelectorAll('.stat-card .more-options')
const optionsCards = document.querySelectorAll('.stat-card .options-card')


moreOptionsToggles.forEach(toggle => {
    let optionsCard = toggle.parentElement.nextElementSibling
    toggle.addEventListener('click', () => {
        optionsCard.classList.add('show-flex');
    });

    let cardClosetoggle = optionsCard.querySelector('.close-card');
    cardClosetoggle.addEventListener('click', () => {
        optionsCard.classList.remove('show-flex');
    });
});


document.addEventListener('click', (e) => {
    
    optionsCards.forEach(card => {
        if (!card.contains(e.target) && !card.parentElement.contains(e.target)) {
            card.classList.remove('show-flex');
        }
    });
    
});
