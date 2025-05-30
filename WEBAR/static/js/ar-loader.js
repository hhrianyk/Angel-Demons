document.addEventListener('DOMContentLoaded', () => {
    const scene = document.querySelector('a-scene');

    scene.addEventListener('loaded', () => {
        console.log('AR scene loaded');

        // Додаткові налаштування
        const arSystem = scene.systems["mindar-image-system"];

        arSystem.start(); // Автоматичний старт

        // Обробники подій
        scene.addEventListener('targetFound', event => {
            console.log('Target found:', event.detail.target);
        });

        scene.addEventListener('targetLost', event => {
            console.log('Target lost:', event.detail.target);
        });
    });

    // Обробка помилок
    scene.addEventListener('error', (error) => {
        console.error('AR error:', error);
        alert('AR initialization failed. Please check camera permissions.');
    });
});