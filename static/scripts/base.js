const menuToggle = document.querySelector('#nav-menu #menu-toggle');
const sideBar = document.querySelector("#sidebar");


document.addEventListener('click', (e) => {
    if (menuToggle.contains(e.target)){
        sideBar.classList.toggle("show-sidebar");

    }else if(!menuToggle.contains(e.target) && !sideBar.contains(e.target)){
        sideBar.classList.remove("show-sidebar");
    }
});
