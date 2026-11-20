const products = [
    {
        id: 1,
        name: 'Product 1',
        price: 19.99,
        image: 'data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect x='0' y='0' width='100' height='100' fill='%23FF69B4'%3E%3C/svg%3E'
    },
    {
        id: 2,
        name: 'Product 2',
        price: 29.99,
        image: 'data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Crect x='0' y='0' width='100' height='100' fill='%23FFC107'%3E%3C/svg%3E'
    }
];

const featuredProducts = document.querySelector('.featured-products');
const collections = document.querySelector('.collections');

products.forEach((product) => {
    const productElement = document.createElement('li');
    productElement.innerHTML = `
        <img src="${product.image}" alt="${product.name}">
        <h3>${product.name}</h3>
        <p>
            
        </p>
    `;
    featuredProducts.appendChild(productElement);
});

collections.addEventListener('click', (e) => {
    if (e.target.tagName === 'A') {
        const collectionName = e.target.textContent;
        console.log(collectionName);
    }
});