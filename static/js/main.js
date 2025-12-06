// Helper function for star rating glow effect
function handleStarChange(e) {
    const input = e.currentTarget;
    const stars = input.closest('.rating-input').querySelectorAll('label');
    const index = Array.from(stars).indexOf(input.nextElementSibling);
    
    stars.forEach((star, i) => {
        if (i <= index) {
            star.style.color = '#ffc107';
            star.classList.add('star-glow');
            setTimeout(() => star.classList.remove('star-glow'), 300);
        } else {
            star.style.color = '#ddd';
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Add to Cart functionality with enhanced animations
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');

    addToCartForms.forEach(form => {
        form.addEventListener('submit', handleAddToCartSubmit);
    });

    function handleAddToCartSubmit(e) {
        e.preventDefault();
        const form = e.currentTarget;
        const action = form.action;
        const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
        const button = form.querySelector('button[type="submit"]');
        const originalText = button.innerHTML;

        // Add loading animation
        button.innerHTML = '<span class="loading-spinner me-2"></span>Adding...';
        button.disabled = true;
        button.classList.add('loading');

        // Add ripple effect
        const ripple = document.createElement('div');
        ripple.className = 'ripple-effect';
        button.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);

        fetch(action, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Enhanced toast with animation
                Toastify({
                    text: "Product added to cart! 🛒",
                    duration: 3000,
                    close: true,
                    gravity: "bottom",
                    position: "right",
                    backgroundColor: "linear-gradient(to right, #00b09b, #96c93d)",
                    className: "cart-toast",
                    onClick: () => globalThis.location.href = '/cart/',
                    stopOnFocus: true
                }).showToast();

                // Update Cart badge with animation
                if(data.cart_count !== undefined) {
                    const cartCount = document.querySelector('.floating-cart .fw-bold');
                    if(cartCount) {
                        cartCount.innerHTML = data.cart_count + " Items";
                        cartCount.classList.add('pulse-animation');
                        setTimeout(() => cartCount.classList.remove('pulse-animation'), 1000);
                    }

                    const cartTotal = document.querySelector('.floating-cart .text-success');
                    if(cartTotal) {
                        cartTotal.innerHTML = "₹" + data.cart_total_cost;
                        cartTotal.classList.add('glow-animation');
                        setTimeout(() => cartTotal.classList.remove('glow-animation'), 1000);
                    }
                }

                // Add success animation to button
                button.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i>Added!';
                button.classList.add('btn-success-animation');
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.disabled = false;
                    button.classList.remove('loading', 'btn-success-animation');
                }, 2000);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            button.innerHTML = '<i class="bi bi-exclamation-triangle me-2"></i>Failed';
            button.classList.add('btn-error-animation');
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
                button.classList.remove('loading', 'btn-error-animation');
            }, 2000);
        });
    }

    // Enhanced Wishlist functionality with pulse animation
    document.body.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn-wishlist');
        if (btn) {
            e.preventDefault();

            const productId = btn.dataset.productId;
            const icon = btn.querySelector('i');
            const isActive = btn.classList.contains('active');
            const url = isActive ? `/wishlist/remove/${productId}/` : `/wishlist/add/${productId}/`;

            // Add click animation
            btn.classList.add('heart-click');
            setTimeout(() => btn.classList.remove('heart-click'), 300);

            // Get CSRF token
            let csrfToken = '';
            const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfInput) {
                csrfToken = csrfInput.value;
            } else {
                const value = `; ${document.cookie}`;
                const parts = value.split(`; csrftoken=`);
                if (parts.length === 2) csrfToken = parts.pop().split(';').shift();
            }

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI with enhanced animations
                    if(isActive) {
                        btn.classList.remove('active');
                        if(icon) icon.className = 'bi bi-heart';
                        // Add break animation
                        btn.classList.add('heart-break');
                        setTimeout(() => btn.classList.remove('heart-break'), 500);
                    } else {
                        btn.classList.add('active');
                        if(icon) icon.className = 'bi bi-heart-fill';
                        // Add pulse animation
                        btn.classList.add('heart-pulse');
                        setTimeout(() => btn.classList.remove('heart-pulse'), 1000);
                    }

                    // Enhanced notification
                    const message = data.message || (isActive ? "Removed from wishlist 💔" : "Added to wishlist ❤️");
                    const color = isActive ? "linear-gradient(to right, #ff6b6b, #ee5a52)" : "linear-gradient(to right, #ff6b6b, #ffb347)";

                    Toastify({
                        text: message,
                        duration: 3000,
                        close: true,
                        gravity: "bottom",
                        position: "right",
                        style: { background: color },
                        className: "wishlist-toast"
                    }).showToast();
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        }
    });

    // Product image zoom on hover
    const detailImages = document.querySelectorAll('.product-image');
    detailImages.forEach(img => {
        img.addEventListener('mouseenter', function() {
            const image = this.querySelector('img');
            image.classList.add('image-zoom');
        });

        img.addEventListener('mouseleave', function() {
            const image = this.querySelector('img');
            image.classList.remove('image-zoom');
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Enhanced form interactions
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('form-group-focus');
        });

        control.addEventListener('blur', function() {
            this.parentElement.classList.remove('form-group-focus');
        });
    });

    // Star rating interaction enhancement
    const starLabels = document.querySelectorAll('.star-label');
    starLabels.forEach((star, index) => {
        star.addEventListener('mouseenter', function() {
            // Add glow effect to hovered stars
            for (let i = 0; i <= index; i++) {
                starLabels[i].classList.add('star-glow');
            }
        });

        star.addEventListener('mouseleave', function() {
            starLabels.forEach(s => s.classList.remove('star-glow'));
        });
    });

    // Progress bar animations
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });

    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);

    // Observe elements for animation
    document.querySelectorAll('.card, .feature-card, .stat-card').forEach(el => {
        observer.observe(el);
    });

    // Enhanced dropdown animations
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');

        if (toggle && menu) {
            toggle.addEventListener('click', function() {
                menu.classList.add('dropdown-animate');
            });

            dropdown.addEventListener('hidden.bs.dropdown', function() {
                menu.classList.remove('dropdown-animate');
            });
        }
    });

    // Cart item removal animation
    document.querySelectorAll('.remove-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const cartItem = this.closest('.cart-item');
            if (cartItem) {
                cartItem.classList.add('removing');
                setTimeout(() => {
                    cartItem.style.display = 'none';
                }, 300);
            }
        });
    });

    // Loading states for async operations
    const asyncButtons = document.querySelectorAll('[data-async]');
    asyncButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.classList.add('loading');
            this.innerHTML = '<span class="loading-spinner me-2"></span>Loading...';
        });
    });

    // Enhanced search with debouncing
    let searchTimeout;
    const searchInputs = document.querySelectorAll('input[name="q"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchIcon = this.previousElementSibling;
            if (searchIcon) {
                searchIcon.classList.add('searching');
            }

            searchTimeout = setTimeout(() => {
                if (searchIcon) {
                    searchIcon.classList.remove('searching');
                }
                // Trigger search here if needed
            }, 500);
        });
    });

    // Keyboard navigation enhancements
    document.addEventListener('keydown', function(e) {
        // ESC to close modals/dropdowns
        if (e.key === 'Escape') {
            const openDropdowns = document.querySelectorAll('.dropdown-menu.show');
            openDropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }

        // Ctrl+K for search focus
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
    });

    // Performance optimization: Lazy load images
    const lazyImages = document.querySelectorAll('img[data-src]');
    if ('IntersectionObserver' in globalThis) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // Enhanced tooltips
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(el => {
        el.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.dataset.tooltip;
            document.body.appendChild(tooltip);

            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';

            setTimeout(() => tooltip.classList.add('visible'), 10);
        });

        el.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.custom-tooltip');
            if (tooltip) {
                tooltip.classList.remove('visible');
                setTimeout(() => tooltip.remove(), 300);
            }
        });
    });

    // Parallax effect for hero sections
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const heroBg = document.querySelector('.hero-section');
        if (heroBg) {
            heroBg.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
    });

    // Auto-hide floating cart on scroll
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        const floatingCart = document.querySelector('.floating-cart');
        if (floatingCart) {
            floatingCart.classList.add('hidden');
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                floatingCart.classList.remove('hidden');
            }, 1000);
        }
    });

    // Dark Mode Toggle Logic
    const darkModeToggle = document.getElementById('darkModeToggle');
    const body = document.body;
    
    // Check local storage
    if (globalThis.localStorage.getItem('darkMode') === 'enabled') {
        body.classList.add('dark-mode');
        if(darkModeToggle) darkModeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            
            // Update icon
            darkModeToggle.innerHTML = isDark ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>';
            
            // Save preference
            globalThis.localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
        });
    }

    // --- Interactive Enhancements ---

    // 1. Universal Ripple Effect for Buttons
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // 2. Product Card Tilt & Glow Effect
    const productCards = document.querySelectorAll('.product-card');
    productCards.forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Subtle tilt
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;
            
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
            
            // Dynamic glow/shine
            this.style.setProperty('--mouse-x', `${x}px`);
            this.style.setProperty('--mouse-y', `${y}px`);
        });

        card.addEventListener('mouseleave', function() {
            this.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
        });
    });

    // 3. Image Zoom on Quick View Hover
    const quickViewImages = document.querySelectorAll('.card-img-top');
    quickViewImages.forEach(img => {
        img.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1)';
            this.style.transition = 'transform 0.5s ease';
        });
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // 4. Star Rating Interactive Glow
    const ratingInputs = document.querySelectorAll('.rating-input input');
    ratingInputs.forEach(input => {
        input.addEventListener('change', handleStarChange);
    });

    // 5. Navbar Scroll Glass Effect Optimization
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.classList.add('glass-navbar', 'shadow-lg');
                navbar.style.background = 'rgba(31, 41, 55, 0.95)';
            } else {
                navbar.classList.remove('glass-navbar', 'shadow-lg');
                navbar.style.background = 'linear-gradient(135deg, #1f2937 0%, #374151 100%)';
            }
        });
    }
});
