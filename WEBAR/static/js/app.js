document.addEventListener('DOMContentLoaded', function() {
    // Ініціалізація AR сканера
    initARScanner();

    // Обробка події для кнопки старту
    document.getElementById('start-scan').addEventListener('click', function() {
        startCamera();
    });
});

function initARScanner() {
    console.log('AR Scanner initialized');
    // Тут може бути додаткова ініціалізація
}

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            console.log('Camera access granted');
            // Тут можна додати логіку для відображення потоку
        })
        .catch(function(error) {
            console.error('Camera access denied:', error);
            alert('Не вдалося отримати доступ до камери. Будь ласка, перевірте дозволи.');
        });
}