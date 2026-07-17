---
name: "accessibility"
description: "Standards and best practices for creating accessible software and web interfaces."
---

# Accessibility Standards and Best Practices

This skill outlines the principles, requirements, and compliance standards for building accessible user interfaces and software systems.

## Core Directives

### 1. WCAG Compliance
Strictly adhere to the latest Web Content Accessibility Guidelines (WCAG 2.1/2.2 AA standards). All user interface implementations must target Level AA compliance as a minimum baseline.

### 2. Semantic HTML
Prioritize native, semantic HTML elements over generic containers. Ensure correct document structure and element roles:
- Use landmarks (header, nav, main, footer) to define page structure.
- Maintain correct heading hierarchies (H1 to H6) without skipping levels.
- Utilize semantic interactive elements (button, a, input, select) to inherit native keyboard and screen reader support.

### 3. Contrast and Visual Design
Ensure sufficient color contrast ratios for text and UI components:
- Minimum contrast ratio of 4.5:1 for normal text.
- Minimum contrast ratio of 3:1 for large text and essential visual components.
- Do not rely solely on color to convey information, state, or actions.

### 4. ARIA and Screen-Reader Compatibility
When native semantic elements are insufficient, apply Accessible Rich Internet Applications (ARIA) attributes correctly:
- Use `aria-label`, `aria-labelledby`, and `aria-describedby` to provide clear, descriptive labels.
- Implement state indicators like `aria-expanded`, `aria-selected`, and `aria-hidden` to dynamically update screen readers.
- Ensure all non-text content (images, icons) has descriptive alternative text (`alt` attributes) or is explicitly marked as decorative (`alt=""` or `role="presentation"`).

### 5. Keyboard Navigability
Ensure all interactive elements are fully accessible and functional via keyboard interface:
- Maintain a logical and intuitive tab order.
- Implement visible, high-contrast focus indicators for all interactive controls.
- Prevent keyboard traps by ensuring users can navigate into and out of all components.
- Support standard keyboard patterns (e.g., Space/Enter to activate, Arrow keys for menus/tabs, Escape to dismiss dialogs).
