## 2024-10-26 - [Keyboard Accessibility for Pseudo-Links]
**Learning:** The "pseudo-link" pattern (Typography + onClick) is a pervasive accessibility trap. It lacks keyboard focus, activation, and semantic role.
**Action:** Always replace with `<Link component="button">` or `<Button variant="text">` to inherit native interactive behaviors and focus styles.

## 2024-10-26 - [Unused Components as UX Opportunities]
**Learning:** Orphaned "upgrade" components (like `SearchAutocomplete`) are often left unconnected in the codebase.
**Action:** Before writing new features from scratch, search for unused components that might already solve the problem.
