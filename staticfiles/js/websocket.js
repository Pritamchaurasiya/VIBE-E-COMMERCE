/**
 * WebSocket utilities for real-time features.
 * This module handles WebSocket connections for notifications, cart, and orders.
 */

// WebSocket connection manager
class WebSocketManager {
    constructor(url, options = {}) {
        this.url = url;
        this.options = {
            reconnectInterval: 3000,
            maxReconnectAttempts: 5,
            ...options
        };
        this.ws = null;
        this.reconnectAttempts = 0;
        this.listeners = {};
    }

    connect() {
        try {
            const protocol = globalThis.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${globalThis.location.host}${this.url}`;
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log(`WebSocket connected: ${this.url}`);
                this.reconnectAttempts = 0;
                this.emit('connected');
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.emit('message', data);
                    if (data.type) {
                        this.emit(data.type, data);
                    }
                } catch (error) {
                    console.error('WebSocket message parse error:', error);
                }
            };

            this.ws.onclose = () => {
                console.log(`WebSocket closed: ${this.url}`);
                this.emit('disconnected');
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error(`WebSocket error: ${this.url}`, error);
                this.emit('error', error);
            };

        } catch (error) {
            console.error('WebSocket connection failed:', error);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.options.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
            setTimeout(() => this.connect(), this.options.reconnectInterval);
        }
    }

    send(data) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    on(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    off(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    }

    emit(event, data) {
        this.listeners[event]?.forEach(callback => callback(data));
    }

    close() {
        this.ws?.close();
    }
}

// Notification handler
class NotificationHandler {
    ws = null;
    badge = document.querySelector('.notification-badge');
    dropdown = document.querySelector('#notificationDropdown');

    constructor() {

        // Only connect if user is authenticated
        const isAuthenticated = document.body.dataset.authenticated === 'true';
        if (isAuthenticated) {
            this.ws = new WebSocketManager('/ws/notifications/');
            
            this.ws.on('notification_count', (data) => {
                this.updateBadge(data.count);
            });

            this.ws.on('notification', (data) => {
                this.showNotification(data);
                this.addToDropdown(data);
            });

            this.ws.connect();
        }
    }

    updateBadge(count) {
        if (this.badge) {
            if (count > 0) {
                this.badge.textContent = count > 99 ? '99+' : count;
                this.badge.classList.remove('d-none');
                this.badge.classList.add('pulse');
                setTimeout(() => this.badge.classList.remove('pulse'), 1000);
            } else {
                this.badge.classList.add('d-none');
            }
        }
    }

    showNotification(data) {
        // Use browser notifications if available
        if ('Notification' in globalThis && Notification.permission === 'granted') {
            new Notification(data.title || 'VIBE E-Commerce', {
                body: data.message,
                icon: '/static/images/logo.png'
            });
        }

        // Also show toast
        if (typeof Toastify !== 'undefined') {
            Toastify({
                text: `${data.title}: ${data.message}`,
                duration: 5000,
                close: true,
                gravity: 'top',
                position: 'right',
                backgroundColor: 'linear-gradient(to right, #667eea, #764ba2)',
                onClick: () => {
                    if (data.link) {
                        globalThis.location.href = data.link;
                    }
                }
            }).showToast();
        }
    }

    addToDropdown(data) {
        if (this.dropdown) {
            const item = document.createElement('a');
            item.className = 'dropdown-item notification-item new';
            item.href = data.link || '#';

            const container = document.createElement('div');
            container.className = 'd-flex align-items-center';

            const iconContainer = document.createElement('div');
            iconContainer.className = 'notification-icon me-3';
            const icon = document.createElement('i');
            icon.className = 'bi bi-bell-fill text-primary';
            iconContainer.appendChild(icon);

            const textContainer = document.createElement('div');
            const title = document.createElement('p');
            title.className = 'mb-0 fw-bold';
            title.textContent = data.title;
            const message = document.createElement('small');
            message.className = 'text-muted';
            message.textContent = data.message;
            textContainer.appendChild(title);
            textContainer.appendChild(message);

            container.appendChild(iconContainer);
            container.appendChild(textContainer);
            item.appendChild(container);

            this.dropdown.insertBefore(item, this.dropdown.firstChild);
        }
    }

    markAsRead(ids) {
        this.ws?.send({ type: 'mark_read', ids: ids });
    }

    requestPermission() {
        if ('Notification' in globalThis && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }
}

// Cart real-time updates
class CartHandler {
    ws = null;
    cartCount = document.querySelector('.cart-count');
    cartTotal = document.querySelector('.cart-total');

    constructor() {
        this.ws = new WebSocketManager('/ws/cart/');

        this.ws.on('cart_update', (data) => {
            this.updateUI(data);
        });

        this.ws.connect();
    }

    updateUI(data) {
        if (data.cart_count !== undefined) {
            this.cartCount?.classList.add('bounce');
            if (this.cartCount) {
                this.cartCount.textContent = data.cart_count;
            }
            setTimeout(() => this.cartCount?.classList.remove('bounce'), 500);
        }

        if (data.cart_total !== undefined) {
            if (this.cartTotal) {
                this.cartTotal.textContent = `₹${data.cart_total}`;
            }
        }
    }
}

// Order tracking real-time updates
class OrderTracker {
    constructor(orderId) {
        this.orderId = orderId;
        this.ws = null;
        this.statusElement = document.querySelector('.order-status');
        this.progressBar = document.querySelector('.order-progress');
    }

    init() {
        this.ws = new WebSocketManager(`/ws/orders/${this.orderId}/`);

        this.ws.on('order_status', (data) => {
            this.updateStatus(data.status, data.message);
        });

        this.ws.connect();
    }

    updateStatus(status, message) {
        const statusMap = {
            'pending': { step: 1, label: 'Pending', color: 'warning' },
            'confirmed': { step: 2, label: 'Confirmed', color: 'info' },
            'shipped': { step: 3, label: 'Shipped', color: 'primary' },
            'delivered': { step: 4, label: 'Delivered', color: 'success' },
            'cancelled': { step: 0, label: 'Cancelled', color: 'danger' }
        };

        const statusInfo = statusMap[status] || statusMap['pending'];

        if (this.statusElement) {
            this.statusElement.textContent = statusInfo.label;
            this.statusElement.className = `order-status badge bg-${statusInfo.color}`;
        }

        if (this.progressBar) {
            const progress = (statusInfo.step / 4) * 100;
            this.progressBar.style.width = `${progress}%`;
        }

        // Show notification
        if (message && typeof Toastify !== 'undefined') {
            Toastify({
                text: message,
                duration: 5000,
                gravity: 'top',
                position: 'right',
                backgroundColor: 'linear-gradient(to right, #00b09b, #96c93d)'
            }).showToast();
        }
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Main application setup
const Vibe = {
    init: function() {
        // Initialize notification handler
        this.notificationHandler = new NotificationHandler();

        // Initialize cart handler
        this.cartHandler = new CartHandler();

        // Initialize order tracker if on order detail page
        const orderDetailPage = document.querySelector('[data-order-id]');
        if (orderDetailPage) {
            const orderId = orderDetailPage.dataset.orderId;
            this.orderTracker = new OrderTracker(orderId);
            this.orderTracker.init();
        }

        // Request notification permission
        if ('Notification' in globalThis && Notification.permission === 'default') {
            const notificationBtn = document.querySelector('[data-request-notifications]');
            if (notificationBtn) {
                notificationBtn.addEventListener('click', () => {
                    this.notificationHandler.requestPermission();
                });
            }
        }
    }
};

// Initialize handlers when DOM is ready
document.addEventListener('DOMContentLoaded', () => Vibe.init());

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { WebSocketManager, NotificationHandler, CartHandler, OrderTracker, Vibe };
}
