from playwright.sync_api import sync_playwright, expect

def verify_search_ux():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock the API response to return a product with a price and vendor
        page.route("**/api/v1/products/?search=Test&limit=5", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body='{"results": [{"id": 1, "name": "Test Product", "slug": "test-product", "price": 100, "vendor_name": "Test Vendor", "image": "https://via.placeholder.com/150"}], "count": 1}'
        ))

        # Fallback for other queries
        page.route("**/api/v1/products/*", lambda route: route.fallback())

        # Navigate to the test page
        try:
            page.goto("http://localhost:3000/verification/search", timeout=30000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            return

        # Find the search input
        try:
            search_input = page.get_by_placeholder("Search products...")
            expect(search_input).to_be_visible(timeout=10000)
        except Exception as e:
            print(f"Search input not found: {e}")
            page.screenshot(path="/home/jules/verification/debug_not_found.png")
            return

        # Type query
        search_input.fill("Test")

        # Wait for results
        try:
            # Check for the price with Rupee symbol
            # The component renders price as {'\u20B9'}{product.price} inside a Typography
            # Text should be "₹100"
            price_locator = page.get_by_text("₹100")
            expect(price_locator).to_be_visible(timeout=5000)

            # Check for bullet point
            # bullet_locator = page.get_by_text("•") # Depending on rendering, might be hard to match exact text if it's separate
            # expect(bullet_locator).to_be_visible()

            # Check for Clear button
            # It only appears when query is present.
            clear_button = page.get_by_label("Clear search query")
            expect(clear_button).to_be_visible()

            print("All elements found!")

        except Exception as e:
            print(f"Verification failed: {e}")

        # Take screenshot
        page.screenshot(path="/home/jules/verification/verification.png")

        browser.close()

if __name__ == "__main__":
    verify_search_ux()
