// Ініціалізація AR сцени
function initARScene() {
    // Створення сцени AR.js
    const scene = document.querySelector('a-scene');

    // Додавання маркера
    const marker = document.createElement('a-marker');
    marker.setAttribute('type', 'pattern');
    marker.setAttribute('url', '/static/uploads/target-image.png');
    marker.setAttribute('id', 'marker');

    // Додавання 3D моделі до маркера
    const box = document.createElement('a-box');
    box.setAttribute('position', '0 0.5 0');
    box.setAttribute('rotation', '0 45 0');
    box.setAttribute('color', '#4CC3D9');

    marker.appendChild(box);
    scene.appendChild(marker);

    // Обробник події для виявлення маркера
    marker.addEventListener('markerFound', function() {
        console.log('Marker found!');
    });

    // Обробник події для втрати маркера
    marker.addEventListener('markerLost', function() {
        console.log('Marker lost!');
    });
}

// Запуск AR при завантаженні сторінки
window.addEventListener('load', function() {
    if (typeof AFRAME === 'undefined') {
        console.error('AFrame не завантажено');
        return;
    }

    if (typeof THREEx === 'undefined') {
        console.error('AR.js не завантажено');
        return;
    }

    initARScene();
});