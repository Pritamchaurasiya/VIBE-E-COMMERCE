/**
 * Vibe E-Commerce Main JavaScript
 * Handles global UI interactions, animations, and common functionality.
 */

const VibeApp = {
    init() {
        this.initTheme();
        this.initSearch();
        this.initCart();
        this.initWishlist();
        this.initAnimations();
        this.initProductInteractions();
        this.initScrollFeatures();
    },

    // --- Theme Management ---
    initTheme() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        const body = document.body;
        
        // Check local storage
        if (localStorage.getItem('darkMode') === 'enabled') {
            body.classList.add('dark-mode');
            if(darkModeToggle) darkModeToggle.innerHTML = '<i class="bi bi-sun-fill"></i>';
        }

        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', () => {
                body.classList.toggle('dark-mode');
                const isDark = body.classList.contains('dark-mode');
                
                // Update icon
                darkModeToggle.innerHTML = isDark ? '<i class="bi bi-sun-fill"></i>' : '<i class="bi bi-moon-fill"></i>';
                localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
            });
        }
    },

    // --- Search Functionality ---
    initSearch() {
        const searchInput = document.getElementById('liveSearchInput');
        const searchResults = document.getElementById('searchResults');
        
        if (!searchInput || !searchResults) return;

        let searchTimeout;
        const RECENT_KEY = 'agri_recent_searches';

        const getRecent = () => {
            try { return JSON.parse(localStorage.getItem(RECENT_KEY)) || []; }
            catch { return []; }
        };

        const saveRecent = (term) => {
            if (!term || term.length < 2) return;
            let recent = getRecent().filter(s => s.toLowerCase() !== term.toLowerCase());
            recent.unshift(term);
            localStorage.setItem(RECENT_KEY, JSON.stringify(recent.slice(0, 5)));
        };

        const renderResults = (data) => {
            searchResults.innerHTML = '';
            if (data.results.length === 0) {
                searchResults.innerHTML = '<div class="p-3 text-muted text-center">No products found</div>';
            } else {
                data.results.forEach(p => {
                    const html = `
                        <a href="/product/${p.slug}/" class="d-flex align-items-center p-3 text-decoration-none text-dark border-bottom search-result-item">
                            ${p.image ? `<img src="${p.image}" class="rounded me-3" style="width:50px;height:50px;object-fit:cover;">` : '<div class="bg-light rounded me-3" style="width:50px;height:50px;"></div>'}
                            <div class="flex-grow-1">
                                <div class="fw-bold">${this.escapeHtml(p.name)}</div>
                                <small class="text-muted">${this.escapeHtml(p.category || '')}</small>
                            </div>
                            <div class="text-success fw-bold">₹${p.price}</div>
                        </a>`;
                    searchResults.insertAdjacentHTML('beforeend', html);
                });
            }
            searchResults.classList.remove('d-none');
        };
        
        const renderRecent = () => {
             const recent = getRecent();
             if(!recent.length) { searchResults.classList.add('d-none'); return; }
             searchResults.innerHTML = '<div class="p-2 bg-light border-bottom"><small class="fw-bold">Recent Searches</small></div>';
             recent.forEach(term => {
                 const div = document.createElement('div');
                 div.className = 'p-2 px-3 search-result-item pointer';
                 // Use safe DOM methods instead of innerHTML to prevent XSS
                 const icon = document.createElement('i');
                 icon.className = 'bi bi-clock-history me-2';
                 div.appendChild(icon);
                 div.appendChild(document.createTextNode(term));
                 div.onclick = () => { searchInput.value = term; searchInput.dispatchEvent(new Event('input')); };
                 searchResults.appendChild(div);
             });
             searchResults.classList.remove('d-none');
        };

        searchInput.addEventListener('focus', () => {
            if (searchInput.value.trim().length < 2) renderRecent();
        });

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();
            clearTimeout(searchTimeout);
            
            if (query.length < 2) {
                renderRecent(); 
                return;
            }

            searchTimeout = setTimeout(() => {
                fetch(`/api/search/?q=${encodeURIComponent(query)}`)
                    .then(r => r.json())
                    .then(data => {
                        renderResults(data);
                        if(data.results.length) saveRecent(query);
                    });
            }, 300);
        });

        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.classList.add('d-none');
            }
        });
    },

    // --- Cart Interactions ---
    initCart() {
        document.querySelectorAll('.add-to-cart-form').forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const btn = form.querySelector('button[type="submit"]');
                const originalContent = btn.innerHTML;
                
                this.setLoading(btn, true);

                try {
                    const csrf = form.querySelector('[name=csrfmiddlewaretoken]').value;
                    const res = await fetch(form.action, {
                        method: 'POST',
                        headers: { 
                            'X-CSRFToken': csrf, 
                            'X-Requested-With': 'XMLHttpRequest' 
                        }
                    });
                    const data = await res.json();

                    if (data.success) {
                        this.showToast('Product added to cart! 🛒', 'success');
                        this.updateCartBadge(data.cart_count, data.cart_total_cost);
                        this.setSuccess(btn, 'Added!');
                        setTimeout(() => this.resetButton(btn, originalContent), 2000);
                    }
                } catch (err) {
                    console.error(err);
                    this.showToast('Failed to add to cart', 'error');
                    this.resetButton(btn, originalContent);
                }
            });
        });

        // Cart Item Removal
        document.querySelectorAll('.remove-btn').forEach(btn => {
           btn.addEventListener('click', function() {
               this.closest('.cart-item')?.classList.add('removing');
           });
        });
    },

    // --- Wishlist Interactions ---
    initWishlist() {
        document.body.addEventListener('click', async (e) => {
            const btn = e.target.closest('.btn-wishlist');
            if(!btn) return;
            
            e.preventDefault();
            const productId = btn.dataset.productId;
            const isActive = btn.classList.contains('active');
            const url = isActive ? `/wishlist/remove/${productId}/` : `/wishlist/add/${productId}/`;
            
            // Optimistic update
            btn.classList.toggle('active');
            const icon = btn.querySelector('i');
            if(icon) icon.className = isActive ? 'bi bi-heart' : 'bi bi-heart-fill';

            try {
                const csrf = this.getCsrfToken();
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 
                        'X-CSRFToken': csrf, 
                        'X-Requested-With': 'XMLHttpRequest' 
                    }
                });
                const data = await res.json();
                if(data.success) {
                    this.showToast(data.message || (isActive ? 'Removed from wishlist' : 'Added to wishlist'), isActive ? 'info' : 'success');
                } else {
                    // Revert on failure
                    btn.classList.toggle('active');
                }
            } catch (err) {
                console.error('Wishlist toggle failed:', err);
                btn.classList.toggle('active');
            }
        });
    },

    // --- Animations & UI ---
    initAnimations() {
        // Universal Ripple
        document.addEventListener('click', (e) => {
            if(e.target.matches('.btn, .btn *')) {
                const btn = e.target.closest('.btn');
                const ripple = document.createElement('span');
                ripple.className = 'ripple-effect';
                const rect = btn.getBoundingClientRect();
                ripple.style.left = `${e.clientX - rect.left}px`;
                ripple.style.top = `${e.clientY - rect.top}px`;
                btn.appendChild(ripple);
                setTimeout(() => ripple.remove(), 600);
            }
        });

        // Scroll Animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) entry.target.classList.add('animate-in');
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.card, .feature-card, .stat-card').forEach(el => observer.observe(el));
    },

    initProductInteractions() {
        // Image Zoom
        document.querySelectorAll('.product-image').forEach(div => {
            div.addEventListener('mouseenter', () => div.querySelector('img')?.classList.add('image-zoom'));
            div.addEventListener('mouseleave', () => div.querySelector('img')?.classList.remove('image-zoom'));
        });

        // Star Rating
        document.querySelectorAll('.rating-input input').forEach(input => {
            input.addEventListener('change', (e) => this.handleStarRating(e.target));
        });
    },

    initScrollFeatures() {
        // Navbar Glass Effect
        const navbar = document.querySelector('.navbar');
        if(navbar) {
            window.addEventListener('scroll', () => {
                if(window.scrollY > 50) navbar.classList.add('glass-navbar', 'shadow-lg');
                else navbar.classList.remove('glass-navbar', 'shadow-lg');
            });
        }

        // Scroll to Top
        const scrollBtn = document.createElement('button');
        scrollBtn.className = 'scroll-to-top';
        scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
        document.body.appendChild(scrollBtn);
        
        scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
        window.addEventListener('scroll', () => {
            scrollBtn.classList.toggle('visible', window.scrollY > 300);
        });
    },

    // --- Helpers ---
    getCsrfToken() {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        if(input) return input.value;
        const csrfRegex = /csrftoken=([^;]+)/;
        const match = csrfRegex.exec(document.cookie);
        return match ? match[1] : '';
    },

    escapeHtml(str) {
        if(!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    setLoading(btn, isLoading) {
        if(isLoading) {
            btn.dataset.original = btn.innerHTML;
            btn.innerHTML = '<span class="loading-spinner me-2"></span>Loading...';
            btn.disabled = true;
        } else {
            btn.innerHTML = btn.dataset.original;
            btn.disabled = false;
        }
    },

    setSuccess(btn, msg) {
        btn.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i>${msg}`;
        btn.classList.add('btn-success-animation');
    },

    resetButton(btn, content) {
        btn.innerHTML = content;
        btn.disabled = false;
        btn.classList.remove('btn-success-animation');
    },

    updateCartBadge(count, total) {
        const badge = document.querySelector('.floating-cart .fw-bold');
        if(badge) badge.textContent = `${count} Items`;
        const cost = document.querySelector('.floating-cart .text-success');
        if(cost) cost.textContent = `₹${total}`;
    },

    showToast(msg, type = 'success') {
        let bg;
        if (type === 'success') {
            bg = 'linear-gradient(to right, #00b09b, #96c93d)';
        } else if (type === 'error') {
            bg = 'linear-gradient(to right, #ff5f6d, #ffc371)';
        } else {
            bg = 'linear-gradient(to right, #2193b0, #6dd5ed)';
        }
        
        if (typeof Toastify === 'undefined') {
            // Fallback
            alert(msg);
            return;
        }
        
        Toastify({
            text: msg,
            duration: 3000,
            gravity: 'bottom',
            position: 'right',
            style: { background: bg },
            stopOnFocus: true
        }).showToast();
    },

    handleStarRating(input) {
         const labels = input.closest('.rating-input').querySelectorAll('label');
         const index = Array.from(labels).indexOf(input.nextElementSibling);
         labels.forEach((l, i) => {
             l.style.color = i <= index ? '#ffc107' : '#ddd';
         });
    }
};

document.addEventListener('DOMContentLoaded', () => VibeApp.init());

// Keep helper functions global if needed by inline scripts (though strict CSP would prevent inline scripts)
globalThis.changeMainImage = function(el) {
    const main = document.getElementById('mainProductImage');
    const img = el.querySelector('img');
    if(main && img) main.src = img.src;
    document.querySelectorAll('.thumbnail-item').forEach(i => i.classList.remove('active'));
    el.classList.add('active');
};
