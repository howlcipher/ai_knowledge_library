---
name: "frontend_engineering"
description: "Best practices and constraints for modern frontend web development."
triggers:
  - "frontend"
  - "react"
  - "typescript"
  - "component"
  - "state management"
tier: 2
---

# Frontend Engineering Standards

This skill governs the development of client-side web applications, establishing mandatory standards for component design, state management, accessibility, performance optimization, and styling.

## Component Design and Architecture

- **Strict Componentization**: Design applications using modular, reusable, single-responsibility components. Enforce a clean separation between presentational (UI-focused) and container (logic/data-focused) components.
- **Type Safety**: Enforce type safety using TypeScript for all components, properties (`Props`), and state. Define strict interfaces or types and avoid the use of `any`.
- **Hooks and Composition**: Utilize React Hooks (or equivalent framework paradigms) to extract and share stateful logic across components instead of legacy higher-order components or mixins.

## State Management

- **Predictable Data Flow**: Enforce unidirectional data flow. Keep local component state isolated.
- **Global State Isolation**: Utilize lightweight, predictable global state managers (e.g., Zustand, Redux Toolkit, Pinia) only for truly global concern-states (e.g., authentication, user preferences). Avoid over-reliance on context APIs for high-frequency updates to prevent unnecessary re-rendering.

## Performance Optimization

- **Bundle Optimization**: Implement code-splitting and dynamic imports (`React.lazy`, Next.js dynamic imports) to minimize initial bundle size and optimize time-to-interactive (TTI).
- **Asset Management**: Optimize and compress all static assets. Serve responsive images using modern formats (e.g., WebP, AVIF) and correct sizing.
- **Rendering Efficiency**: Minimize component re-renders by utilizing memoization (e.g., `useMemo`, `useCallback`) and profiling component trees using framework-specific developer tools.

## Related Skills
- Defer to `accessibility` for WCAG compliance, semantic HTML, ARIA, and keyboard navigation standards.
- Defer to `ui_ux` for interaction design and `visual_design` for hierarchy and typography decisions.
- Defer to `software_development` for general defensive coding and modularity standards.
