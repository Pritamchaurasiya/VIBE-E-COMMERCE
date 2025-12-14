"""
VIBE E-Commerce API test flow module.

This module contains end-to-end tests for the e-commerce API including
registration, login, products, cart, wishlist, and order creation.
"""
import os
import random
import string

import requests

BASE_URL = 'http://localhost:8000/api/v1'
REQUEST_TIMEOUT = 30  # seconds

# Test credentials from environment or defaults (for testing only)
TEST_PASSWORD = os.environ.get('TEST_USER_PASSWORD', 'testpassword123')  # noqa: S105


def random_string(length=10):
    """Generate a random alphanumeric string."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def run_tests():
    """Run all API tests sequentially."""
    print("Starting VIBE E-Commerce API Tests...")

    # 1. Register
    username = f"user_{random_string()}"
    email = f"{username}@example.com"

    print(f"\n1. Registering user: {username}")
    reg_data = {
        "username": username,
        "email": email,
        "password": TEST_PASSWORD,
        "first_name": "Test",
        "last_name": "User"
    }
    resp = requests.post(
        f"{BASE_URL}/auth/register/",
        json=reg_data,
        timeout=REQUEST_TIMEOUT
    )
    if resp.status_code != 201:
        print(f"FAILED: Registration failed. {resp.status_code} - {resp.text}")
        return

    token = resp.json()['token']
    headers = {'Authorization': f'Token {token}'}
    print("SUCCESS: Registered and got token.")

    # 2. Login (Verify)
    print("\n2. Verifying Login")
    resp = requests.post(
        f"{BASE_URL}/auth/login/",
        json={'username': username, 'password': TEST_PASSWORD},
        timeout=REQUEST_TIMEOUT
    )
    if resp.status_code != 200:
        print(f"FAILED: Login failed. {resp.status_code}")
        return
    print("SUCCESS: Login verified.")

    # 3. List Products
    print("\n3. Listing Products")
    resp = requests.get(
        f"{BASE_URL}/products/",
        headers=headers,
        timeout=REQUEST_TIMEOUT
    )
    if resp.status_code != 200:
        print(f"FAILED: List products failed. {resp.status_code}")
        return

    products = resp.json().get('results', [])
    if not products:
        print("WARNING: No products found.")
        return

    product = products[0]
    print(
        f"found {len(products)} products. "
        f"Selected: {product['name']} (ID: {product['id']})"
    )
    print("SUCCESS: Products listed.")

    # 4. Add to Cart
    print("\n4. Adding to Cart")
    cart_data = {
        "product_id": product['id'],
        "quantity": 2,
        "action": "add"
    }
    resp = requests.post(
        f"{BASE_URL}/cart/",
        json=cart_data,
        headers=headers,
        timeout=REQUEST_TIMEOUT
    )
    if resp.status_code != 200:
        print(f"FAILED: Add to cart failed. {resp.status_code} - {resp.text}")
        return
    print(f"Cart response: {resp.json()}")
    print("SUCCESS: Added to cart.")

    # 5. Get Cart
    print("\n5. Fetching Cart")
    resp = requests.get(
        f"{BASE_URL}/cart/",
        headers=headers,
        timeout=REQUEST_TIMEOUT
    )
    if resp.status_code != 200:
        print(f"FAILED: Get cart failed. {resp.status_code}")
        return
    cart_items = resp.json().get('items', [])
    if len(cart_items) != 1 or cart_items[0]['quantity'] != 2:
        print(f"FAILED: Cart content mismatch. {cart_items}")
        return
    print("SUCCESS: Cart fetched and verified.")

    # 6. Wishlist
    print("\n6. Adding to Wishlist")
    resp = requests.post(
        f"{BASE_URL}/wishlist/",
        json={"product_id": product['id']},
        headers=headers,
        timeout=REQUEST_TIMEOUT
    )
    if resp.status_code not in [200, 201]:
        print(f"FAILED: Wishlist add failed. {resp.status_code}")
    else:
        print("SUCCESS: Added to wishlist.")

    # 7. Create Order (Mock)
    print("\n7. Creating Order")
    order_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "address": "123 Test St",
        "zipcode": "123456",
        "place": "Test City",
        "phone": "9876543210",
        "payment_method": "cod"  # cash on delivery
    }
    resp = requests.post(
        "http://localhost:8000/api/start_order/",
        json=order_data,
        headers=headers,
        timeout=REQUEST_TIMEOUT
    )
    if resp.status_code in [200, 201]:
        print("SUCCESS: Order created.")
        print(resp.json())
    else:
        print(f"FAILED: Order creation failed. {resp.status_code} - {resp.text}")

    print("\nAll Tests Completed.")


if __name__ == "__main__":
    run_tests()
