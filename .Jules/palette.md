## 2025-02-27 - Respecting Reduced Motion Preferences in Animations

**Learning:** Animations can trigger vestibular disorders (nausea, dizziness) in some users. `prefers-reduced-motion` is a critical media query to respect.
**Action:** When implementing animations (CSS or JS-based like Framer Motion), always check `useMediaQuery('(prefers-reduced-motion: reduce)')` and provide a static or simplified alternative.
