// Mobile Menu Toggle Script
document.addEventListener('DOMContentLoaded', function() {
    const headerContent = document.querySelector('.header-content');
    const mainNav = document.querySelector('.main-nav');

    if (headerContent && mainNav && window.innerWidth <= 768) {
        let toggleBtn = document.querySelector('.mobile-menu-toggle');

        if (!toggleBtn) {
            toggleBtn = document.createElement('button');
            toggleBtn.className = 'mobile-menu-toggle';
            toggleBtn.setAttribute('aria-label', 'Toggle menu');
            toggleBtn.innerHTML = `
                <div class="hamburger">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            `;

            const brand = headerContent.querySelector('.header-brand') || headerContent.firstElementChild;
            if (brand) {
                brand.appendChild(toggleBtn);
            } else {
                headerContent.insertBefore(toggleBtn, mainNav);
            }
        }


        toggleBtn.addEventListener('click', function() {
            mainNav.classList.toggle('active');
            this.querySelector('.hamburger').classList.toggle('active');


            const isExpanded = mainNav.classList.contains('active');
            this.setAttribute('aria-expanded', isExpanded);
        });
        e
        document.addEventListener('click', function(event) {
            const isClickInside = headerContent.contains(event.target);

            if (!isClickInside && mainNav.classList.contains('active')) {
                mainNav.classList.remove('active');
                toggleBtn.querySelector('.hamburger').classList.remove('active');
                toggleBtn.setAttribute('aria-expanded', 'false');
            }
        });

        window.addEventListener('resize', function() {
            if (window.innerWidth > 768 && mainNav.classList.contains('active')) {
                mainNav.classList.remove('active');
                toggleBtn.querySelector('.hamburger').classList.remove('active');
                toggleBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }
});

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#') {
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                const mainNav = document.querySelector('.main-nav');
                const toggleBtn = document.querySelector('.mobile-menu-toggle');
                if (mainNav && mainNav.classList.contains('active')) {
                    mainNav.classList.remove('active');
                    if (toggleBtn) {
                        toggleBtn.querySelector('.hamburger').classList.remove('active');
                    }
                }
            }
        }
    });
});