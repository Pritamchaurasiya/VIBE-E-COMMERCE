## 2026-01-05 - SearchAutocomplete Integration

**Learning:** When replacing a standard search input with a complex Autocomplete component in a constrained space (like a Header), ensure the new component exposes props for custom styling (via `sx`) to match the existing visual design (e.g., transparent background vs. solid). Also, verify navigation parameters (`q` vs `search`) match what the listing page expects to avoid broken functionality.

**Action:** Always check the consuming component's query parameter expectations before integrating a new search component. Expose style overrides on reusable UI components.
