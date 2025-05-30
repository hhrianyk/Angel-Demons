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