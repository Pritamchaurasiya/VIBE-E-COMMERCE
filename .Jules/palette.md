## 2024-05-23 - Wishlist Tooltip Implementation
**Learning:** Icon-only buttons (like the wishlist heart) can be ambiguous for users. While `aria-label` supports screen readers, visual users benefit significantly from a hover tooltip explaining the action (Add vs Remove), especially when the state toggle isn't immediately obvious from the icon alone.
**Action:** Default to wrapping all icon-only action buttons in a `Tooltip` component to provide dual-channel (visual + accessible) context.
