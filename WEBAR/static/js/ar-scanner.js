document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    const statusEl = document.getElementById('status');
    const scene = document.querySelector('a-scene');
    let arSystem;

    // Ініціалізація AR
    scene.addEventListener('loaded', () => {
        arSystem = scene.systems["mindar-image-system"];
        statusEl.textContent = "System loaded";
    });

    // Обробник кнопки старту
    startBtn.addEventListener('click', async () => {
        try {
            // Запит доступу до камери
            const stream = await navigator.mediaDevices.getUserMedia({ video: true });

            if (arSystem) {
                arSystem.start();
                startBtn.textContent = "Scanning...";
                startBtn.disabled = true;
                statusEl.textContent = "Looking for target...";
            }
        } catch (err) {
            console.error("Camera error:", err);
            statusEl.textContent = "Camera access denied";
        }
    });

    // Події знаходження/втрати маркера
    scene.addEventListener('targetFound', () => {
        statusEl.textContent = "Target found!";
    });

    scene.addEventListener('targetLost', () => {
        statusEl.textContent = "Target lost";
    });

    // Обробка помилок
    scene.addEventListener('error', (err) => {
        console.error("AR error:", err);
        statusEl.textContent = "Error: " + err.detail;
    });
});