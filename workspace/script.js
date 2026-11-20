const hero = document.getElementById('hero');
const shopTea = document.getElementById('shop-tea');
const discoverNewTeas = document.getElementById('discover-new-teas');
const bestSellers = document.getElementById('best-sellers');

const shopTeaList = document.getElementById('shop-tea').querySelectorAll('li');
const discoverNewTeasList = document.getElementById('discover-new-teas').querySelectorAll('li');
const bestSellersList = document.getElementById('best-sellers').querySelectorAll('li');

shopTeaList.forEach((item) => {
    item.addEventListener('click', () => {
        alert('Shop tea now!');
    });
});

discoverNewTeasList.forEach((item) => {
    item.addEventListener('click', () => {
        alert('Discover new teas!');
    });
});

bestSellersList.forEach((item) => {
    item.addEventListener('click', () => {
        alert('Best Sellers!');
    });
});

const searchForm = document.createElement('form');
searchForm.className = 'site-search';
searchForm.setAttribute('role', 'search');

const searchLabel = document.createElement('label');
searchLabel.className = 'visually-hidden';
searchLabel.htmlFor = 'tea-search';
searchLabel.textContent = 'Search teas';

const searchInput = document.createElement('input');
searchInput.id = 'tea-search';
searchInput.type = 'search';
searchInput.placeholder = 'Search teas';

const searchButton = document.createElement('button');
searchButton.type = 'submit';
searchButton.textContent = 'Search';

searchForm.append(searchLabel, searchInput, searchButton);
const header = document.querySelector('header');
header.appendChild(searchForm);

searchForm.addEventListener('submit', (event) => {
    event.preventDefault();
});

searchInput.addEventListener('input', () => {
    const searchValue = searchInput.value.toLowerCase();
    const teas = document.querySelectorAll('#shop-tea li, #discover-new-teas li, #best-sellers li');
    teas.forEach((tea) => {
        const teaName = tea.querySelector('h3').textContent.toLowerCase();
        if (teaName.includes(searchValue)) {
            tea.classList.remove('is-filtered');
        } else {
            tea.classList.add('is-filtered');
        }
    });
});