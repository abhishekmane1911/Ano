# Theme Migration Guide

## Overview

This guide explains how to migrate existing component styles to use the new theme system's CSS variables.

## Quick Reference: Color Replacements

### Background Colors
- `#ffffff` or `white` → `var(--bg-primary)`
- `#f5f5f5`, `#f9f9f9` → `var(--bg-secondary)`
- `#e8e8e8`, `#e5e7eb` → `var(--bg-tertiary)`
- `#e0e0e0` (hover states) → `var(--bg-hover)`

### Text Colors
- `#333`, `#1a202c`, `#213547` → `var(--text-primary)`
- `#666`, `#4a5568`, `#718096` → `var(--text-secondary)`
- `#999`, `#9ca3af` → `var(--text-tertiary)`

### Border Colors
- `#ddd`, `#e2e8f0` → `var(--border-primary)`
- `#ccc`, `#cbd5e0` → `var(--border-secondary)`

### Primary/Brand Colors
- `#667eea`, `#3b82f6` → `var(--primary-color)`
- `#5568d3`, `#2563eb` → `var(--primary-hover)`

### Status Colors
- Success greens → `var(--success)`
- Error reds → `var(--error)`
- Warning oranges → `var(--warning)`
- Info blues → `var(--info)`

## Migration Steps

### 1. Replace Hardcoded Colors

**Before:**
```css
.my-component {
  background: #ffffff;
  color: #333;
  border: 1px solid #ddd;
}
```

**After:**
```css
.my-component {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}
```

### 2. Add Transitions for Smooth Theme Changes

```css
.my-component {
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background-color 0.3s ease, color 0.3s ease;
}
```

### 3. Update Hover States

**Before:**
```css
.button:hover {
  background: #e8e8e8;
}
```

**After:**
```css
.button:hover {
  background: var(--bg-hover);
}
```

### 4. Update Shadow Values

**Before:**
```css
.card {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
```

**After:**
```css
.card {
  box-shadow: var(--shadow-sm);
}
```

## Component-Specific Examples

### Chat Components

```css
/* Chatroom List */
.chatroom-list {
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-primary);
  transition: background-color 0.3s ease, border-color 0.3s ease;
}

.chatroom-item {
  border-bottom: 1px solid var(--border-primary);
  transition: background-color 0.2s ease;
}

.chatroom-item:hover {
  background: var(--bg-hover);
}

.chatroom-name {
  color: var(--text-primary);
}

.chatroom-description {
  color: var(--text-secondary);
}

/* Message Bubbles */
.message-content {
  background: var(--bg-primary);
  color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}

.own-message .message-content {
  background: var(--primary-color);
  color: var(--text-inverse);
}

/* Input Fields */
.message-textarea {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.message-textarea:focus {
  border-color: var(--primary-color);
}
```

### Profile Components

```css
.profile-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-primary);
  box-shadow: var(--shadow-md);
}

.profile-label {
  color: var(--text-secondary);
}

.profile-value {
  color: var(--text-primary);
}
```

### Matchmaking Components

```css
.swipe-card {
  background: var(--bg-primary);
  box-shadow: var(--shadow-lg);
}

.swipe-card-info {
  color: var(--text-primary);
}

.interest-tag {
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-primary);
}
```

## Testing Checklist

After migrating a component:

- [ ] Component looks good in light theme
- [ ] Component looks good in dark theme
- [ ] Transitions are smooth when toggling theme
- [ ] Text is readable in both themes
- [ ] Borders are visible in both themes
- [ ] Hover states work in both themes
- [ ] Focus states are visible in both themes
- [ ] No hardcoded colors remain (except gradients/special cases)

## Special Cases

### Gradients

Gradients can remain hardcoded if they're part of the brand identity:

```css
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

### Transparent Overlays

Use rgba with theme-aware opacity:

```css
.modal-overlay {
  background: var(--bg-modal); /* Already includes opacity */
}
```

### Images and Media

Images don't need migration, but consider adding filters for dark mode if needed:

```css
.dark .logo-image {
  filter: brightness(0.9);
}
```

## Automated Migration Script

For bulk updates, you can use this regex pattern:

Find: `background:\s*#(ffffff|fff|f5f5f5|f9f9f9)`
Replace: `background: var(--bg-primary)` or `var(--bg-secondary)`

Find: `color:\s*#(333|666|999)`
Replace: `color: var(--text-primary)` or `var(--text-secondary)` or `var(--text-tertiary)`

## Priority Components to Migrate

1. ✅ App.css (completed)
2. ✅ index.css (completed)
3. Chat components (Chat.css, MessageBubble, etc.)
4. Profile components (ProfileComponents.css)
5. Matchmaking components (Matchmaking.css)
6. Safety components (Safety.css)
7. Admin components (Admin.css)

## Notes

- The theme system is fully functional even if not all components are migrated
- Components using hardcoded colors will still work, they just won't change with the theme
- Migrate components incrementally as you work on them
- Always test in both themes after migration
