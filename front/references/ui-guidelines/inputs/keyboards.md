# Inputs — Keyboards

## When to consult this file

- Any text input
- Keyboard shortcuts and accelerators
- Focus management for power users

## Core principles

- **Every mouse action has a keyboard equivalent.** No exceptions.
- **`Escape` closes** dialogs, popovers, menus, panels.
- **`Tab` moves** forward, `Shift+Tab` back. Order matches visual order.
- **`Enter` activates** the default action; `Space` activates buttons; arrow keys navigate lists / menus / radio groups.
- **Shortcuts use modifier keys** consistently (`⌘` on Mac, `Ctrl` elsewhere). Show the right one to the right user.

## Concrete rules

1. Set `inputmode` correctly so mobile keyboards specialize (see `components/text-fields.md`).
2. Use `accesskey` sparingly; conflicts with screen-reader hotkeys.
3. **Don't trap focus** anywhere except inside intentionally modal contexts.
4. Detect platform with `navigator.platform.includes('Mac')`; show `⌘K` on Mac, `Ctrl+K` elsewhere.

## Common shortcuts (web)

| Action | Shortcut |
|---|---|
| Command palette | `⌘K` / `Ctrl+K` |
| Search focus | `/` |
| Save | `⌘S` / `Ctrl+S` |
| Undo / Redo | `⌘Z` / `⌘⇧Z` |
| Close dialog | `Escape` |
| Submit form | `⌘Enter` / `Ctrl+Enter` |

## Pattern — shortcut display

```js
const isMac = /Mac/.test(navigator.platform);
const cmd = isMac ? '⌘' : 'Ctrl';
button.querySelector('[data-shortcut]').textContent = `${cmd}K`;
```

## Checklist

- [ ] Every mouse interaction has a keyboard equivalent.
- [ ] `Escape` closes modal surfaces.
- [ ] Tab order matches visual order.
- [ ] Shortcuts localized to platform.
- [ ] No focus trap outside modals.
