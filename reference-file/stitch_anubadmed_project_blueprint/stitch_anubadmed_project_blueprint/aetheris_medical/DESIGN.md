# Design System Specification

## 1. Overview & Creative North Star: "The Ethereal Clinic"

This design system rejects the sterile, boxed-in aesthetics of traditional medical software. Our Creative North Star is **"The Ethereal Clinic"**—a digital environment that feels like a calm, high-end sanctuary rather than a database. 

By leveraging **Spatial 3D Design (Spline)** and **Glassmorphism**, we create an interface that feels immersive and tactile. We break the "template" look through intentional asymmetry, overlapping glass surfaces, and a radical departure from traditional grid lines. The goal is to reassure the patient through a sense of technological mastery and atmospheric depth, moving away from "flat" design into a world of light, blur, and soft luminescence.

---

## 2. Color & Atmospheric Depth

The palette is anchored in a deep, nocturnal navy to reduce eye strain and promote a sense of calm. 

### The "No-Line" Rule
**Strict Mandate:** Designers are prohibited from using 1px solid borders for sectioning. Structural boundaries must be defined solely through background tonal shifts (e.g., a `surface-container-low` panel resting on a `background` floor) or through soft gradients. 

### Surface Hierarchy & Nesting
Instead of a flat grid, treat the UI as a series of physical layers of frosted glass.
- **Base Layer:** `surface` (#071325).
- **Secondary Sections:** `surface-container-low` (#101c2e).
- **Interactive Floating Panels:** `surface-container-high` (#1f2a3d) with a `backdrop-blur` of 20px–40px and 10% opacity.

### The "Glass & Gradient" Rule
To achieve a "signature" feel, main CTAs and hero backgrounds should utilize a transition from `primary` (#4fdbc8) to `primary-container` (#14b8a6) with a 15-degree tilt. This provides a "glowing" soul to the interface that flat colors cannot replicate.

---

## 3. Typography: The Editorial Voice

We utilize a high-contrast typography scale to create an authoritative, editorial feel. 

*   **Display & Headlines:** **Manrope.** Its geometric yet warm curves provide a futuristic, professional tone. Use `display-lg` (3.5rem) for hero statements to create a "digital poster" effect.
*   **UI & Body:** **Inter.** Chosen for its extreme legibility in complex medical data.
*   **Accessibility:** **Noto Sans Bengali.** This must be integrated seamlessly, maintaining the same optical weight as Inter to ensure the bilingual experience feels unified, not like an afterthought.

**Hierarchy as Identity:** Use `headline-lg` (2rem) for section headers with wide letter-spacing (tracking) to convey a premium, spacious feel. Never "crowd" the type; let the breathing room communicate luxury and competence.

---

## 4. Elevation & Depth: Tonal Layering

We convey hierarchy through light and density rather than shadows.

*   **The Layering Principle:** Depth is achieved by "stacking." Place a `surface-container-lowest` card on a `surface-container-low` section to create a soft, natural recess.
*   **Ambient Shadows:** For floating elements (Modals/Popovers), use "Soft-Light" shadows. 
    *   *Values:* Y: 20px, Blur: 40px, Spread: -5px. 
    *   *Color:* A tinted version of `on-surface` at 6% opacity. Never use pure black shadows.
*   **The "Ghost Border" Fallback:** If a border is required for accessibility, use the `outline-variant` token at **15% opacity**. High-contrast, 100% opaque borders are strictly forbidden as they "shatter" the glass illusion.
*   **Glassmorphism:** All primary panels should use a semi-transparent `surface-variant` with a heavy backdrop-blur. This allows the deep navy background colors to bleed through, softening the edges of the UI.

---

## 5. Component Logic

### Buttons: The Kinetic Glow
*   **Primary:** Uses a linear gradient (`primary` to `primary-container`). Roundedness: `full`. Include a subtle outer glow (bloom) using the `primary` color at 20% opacity on hover.
*   **Secondary/Tertiary:** "Glass" buttons. Transparent backgrounds with a `Ghost Border`.

### Input Fields: Recessed Glass
Forbid the "boxed" input. Use a `surface-container-highest` background with a subtle inner shadow to make the field feel "carved" into the glass. 

### Cards & Lists: Fluid Separation
**No Divider Lines.** Separate list items using the `Spacing Scale` (specifically `3` or `4`) or by alternating between `surface-container-low` and `surface-container-lowest`. 

### Specialized Medical Components
*   **Spline Integration:** Use 3D isometric organs or medical icons that subtly rotate on scroll. These are not decorations; they are the focal points of the "Spatial" experience.
*   **Vitals Micro-Charts:** Use `primary` glows for line graphs. Avoid axes and grids where possible; use "Floating Data Points" to maintain the ethereal aesthetic.

---

## 6. Do’s and Don’ts

### Do
*   **Do** use intentional asymmetry. Overlap a glass panel over a 3D Spline element to create true spatial depth.
*   **Do** use `xl` (3rem) or `lg` (2rem) corner rounding for all main containers to maintain a "friendly/calm" medical vibe.
*   **Do** prioritize vertical white space. If in doubt, add more padding from the `16` (5.5rem) or `20` (7rem) scales.

### Don’t
*   **Don’t** use 1px solid dividers or borders. They "flatten" the experience and kill the premium feel.
*   **Don’t** use standard "Drop Shadows." Use the Ambient Shadow method described in Section 4.
*   **Don’t** use high-saturation reds for errors. Use the `error` (#ffb4ab) and `error_container` tokens to ensure the "Calm" aesthetic is not broken during alerts.