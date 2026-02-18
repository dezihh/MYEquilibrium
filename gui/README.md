# MYEquilibrium GUI

This folder contains the Vite + React UI used by the Tauri app. The goal is a compact, reusable UI layer with shared components, minimal page logic, and consistent styling via tokens.

## Structure

- src/App.tsx: App shell, routing-by-state, and data orchestration.
- src/components/: Reusable UI building blocks.
- src/pages/: Page-level UI (Scenes, Devices, Settings, Icons, Connect).
- src/hooks/: Small reusable state helpers.
- src/utils/: Small shared utilities (e.g., class name helpers).
- src/types.ts: Shared UI types.
- src/styles.css: Global styles, tokens, and layout primitives.

## Conventions

- Components stay dumb: accept data + callbacks, no data fetching unless explicitly scoped.
- Pages compose components and keep layout; avoid duplicated markup.
- Hooks own shared state logic (menus, async loading, etc.).
- Styles use tokens in :root; avoid hard-coded values when a token exists.
- Keep files small; split when a file grows beyond a single screen.

## Common Tasks

### Add a new page

1. Create a file in src/pages/.
2. Add any new shared types to src/types.ts.
3. Wire the page in App.tsx (state + render).
4. Reuse components in src/components/; add new ones only if needed.

### Add a new component

1. Add a file in src/components/.
2. Keep props minimal and explicit.
3. Prefer composition over configuration options.

### Add a new icon

1. Add the SVG to src/components/icons.tsx.
2. Reference it via the settingIcons map.

## State & API Notes

- Image management lives in App.tsx and is passed to IconsPage.
- Menu open/close state uses useMenuState from src/hooks/.
- Local storage key: equilibrium_hub_url.

## Styling Notes

- tokens: spacing, radius, shadows, transition are defined at :root.
- prefer .button variants over new button classes.
- list rows use ListRow component + list-row* classes.

## Planned Extensions

- Extract bottom navigation into a dedicated component.
- Add a useImages hook to centralize image API and errors.
- Add a menu/modal system for confirm dialogs.
