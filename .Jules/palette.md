## 2026-01-24 - Currency Mojibake & Stateful Buttons
**Learning:** Found multiple instances of `?` or `Ã¢â€šÂ¹` instead of `₹`. Currency symbols must be verified in the UI. Also, "packing options" buttons were missing accessibility state.
**Action:** Always check currency rendering. For option buttons, ensure `aria-pressed` or `aria-selected` is used to communicate state to screen readers.
