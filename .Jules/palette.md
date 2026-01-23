# Palette's Journal

## 2024-05-22 - Dynamic ARIA Labels in Product Lists
**Learning:** Generic "Add to Cart" or "Select" buttons in lists are confusing for screen reader users as context is lost.
**Action:** Always include the item name in the `aria-label`, e.g., `aria-label={"Add " + product.name + " to cart"}`.
