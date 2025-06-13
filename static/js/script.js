document.addEventListener('DOMContentLoaded', function() {
    // Бургер-меню
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    const menuIcon = document.getElementById('menuIcon');

    // Перевірка наявності елементів (для всіх сторінок)
    if (mobileMenuBtn && navLinks && menuIcon) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            document.body.classList.toggle('no-scroll');

            // Зміна іконки
            if (navLinks.classList.contains('active')) {
                menuIcon.classList.remove('fa-bars');
                menuIcon.classList.add('fa-times');
            } else {
                menuIcon.classList.remove('fa-times');
                menuIcon.classList.add('fa-bars');
            }
        });

        // Закриття меню при кліку на посилання
        document.querySelectorAll('.nav-links a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                document.body.classList.remove('no-scroll');
                menuIcon.classList.remove('fa-times');
                menuIcon.classList.add('fa-bars');
            });
        });
    }

    // Керування кількістю товарів (тільки для сторінки замовлення)
    if (document.querySelector('.quantity-btn')) {
        document.querySelectorAll('.quantity-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.parentElement.querySelector('.quantity-input');
                let value = parseInt(input.value) || 0;

                if (this.classList.contains('plus')) {
                    value++;
                } else {
                    value = value > 0 ? value - 1 : 0;
                }

                input.value = value;
            });
        });
    }
});

// Add this to your script section
function toggleFavorite(itemId, button) {
    // Check if user is logged in
    {% if not current_user.is_authenticated %}
        showNotification('Будь ласка, увійдіть, щоб додавати товари до улюблених', 'warning');
        return;
    {% endif %}

    const icon = button.querySelector('i');

    fetch('/toggle_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `item_id=${itemId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.action === 'added') {
                button.classList.add('active');
                icon.classList.replace('far', 'fas');
                showNotification('Додано до улюблених');
            } else {
                button.classList.remove('active');
                icon.classList.replace('fas', 'far');
                showNotification('Видалено з улюблених');
            }
        } else {
            showNotification('Помилка при обробці запиту', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Помилка при з'єднанні з сервером', 'error');
    });
}

// Function to check favorites on page load (if user is logged in)
function checkFavorites() {
    {% if current_user.is_authenticated %}
        fetch('/get_favorites')
        .then(response => response.json())
        .then(favorites => {
            favorites.forEach(itemId => {
                const button = document.querySelector(`.favorite-btn[onclick*="${itemId}"]`);
                if (button) {
                    button.classList.add('active');
                    const icon = button.querySelector('i');
                    icon.classList.replace('far', 'fas');
                }
            });
        })
        .catch(error => console.error('Error loading favorites:', error));
    {% endif %}
}

// Call this when page loads
document.addEventListener('DOMContentLoaded', checkFavorites);