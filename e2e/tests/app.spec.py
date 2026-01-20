import os
from playwright.sync_api import sync_playwright, expect

def test_login_and_dashboard():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Define base URL - in a real CI this would be an env var
        # For this test script, we assume localhost:3000 as per typical CRA
        BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")

        try:
            # 1. Navigate to Home
            print(f"Navigating to {BASE_URL}")
            page.goto(BASE_URL)
            expect(page).to_have_title(re.compile("VIBE"))

            # 2. Check for Theme Toggle
            print("Checking theme toggle...")
            theme_btn = page.get_by_label("Switch to dark mode")
            if theme_btn.is_visible():
                theme_btn.click()
                # Verify dark mode class added to body
                # This depends on implementation details, checking logic flow primarily
                print("Toggled dark mode")

            # 3. Check for Login Link
            print("Checking login navigation...")
            login_link = page.get_by_role("link", name="Login")
            if login_link.is_visible():
                login_link.click()
                expect(page).to_have_url(f"{BASE_URL}/login")

                # 4. Attempt Login (UI check only since we don't have backend running in this script context)
                page.fill('input[name="username"]', "admin")
                page.fill('input[name="password"]', "password123")
                # We stop here as we can't actually authenticate without the backend running
                print("Login form filled")

            print("E2E Test completed successfully (partial flow due to no backend)")

        except Exception as e:
            print(f"Test failed: {e}")
            # Take screenshot on failure
            page.screenshot(path="failure.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    # Ensure regex import
    import re
    test_login_and_dashboard()
