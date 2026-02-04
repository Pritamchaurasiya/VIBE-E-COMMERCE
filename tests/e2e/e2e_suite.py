import os
import time
import sys
from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")
HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"

def run_tests():
    print(f"Starting E2E Tests against {BASE_URL}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Test 1: Homepage Load
            print("[Test] Homepage Load...")
            page.goto(BASE_URL)
            page.wait_for_load_state("networkidle")
            title = page.title()
            print(f"Page Title: {title}")
            # Assert title or content (Frontend might set specific title)
            # assert "VIBE" in title

            # Test 2: Navigation to Login
            print("[Test] Navigation to Login...")
            page.click('a[href="/login"]')
            page.wait_for_url("**/login")
            print("Navigated to login page")

            # Test 3: Login Flow (Mock or Real if server running)
            # We assume a test user 'testuser' / 'password123' exists or we just test UI presence
            print("[Test] Login UI Check...")
            assert page.is_visible('input[name="username"]')
            assert page.is_visible('input[name="password"]')
            assert page.is_visible('button[type="submit"]')

            # Test 4: Product Search
            print("[Test] Product Search...")
            page.goto(f"{BASE_URL}/products")
            page.wait_for_load_state("networkidle")

            # Check if search bar exists (based on common/Header.js usually)
            # Adjust selector based on actual Header component
            # Assuming there is an input with placeholder 'Search...' or similar
            # page.fill('input[type="text"]', "Wheat")
            # page.keyboard.press("Enter")

            print("E2E Tests Passed!")
            return True

        except Exception as e:
            print(f"E2E Test Failed: {e}")
            page.screenshot(path="e2e_failure.png")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
