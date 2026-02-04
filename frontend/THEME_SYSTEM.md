# Theme System Implementation

## Overview

The Ano platform now includes a comprehensive theme system that supports both light and dark modes. The theme system is built with React Context API and CSS custom properties (CSS variables) for seamless theme switching.

## Features

✅ **Light and Dark Themes**: Complete color schemes for both themes
✅ **Theme Persistence**: User's theme preference is saved to localStorage
✅ **System Preference Detection**: Automatically detects user's system theme preference on first visit
✅ **Smooth Transitions**: All theme changes animate smoothly
✅ **Accessibility**: Respects `prefers-reduced-motion` for users who prefer reduced animations
✅ **Global Theme Toggle**: ThemeToggle component available in navigation

## Architecture

### 1. Theme Context (`src/contexts/ThemeContext.tsx`)

The theme context provides:
- `theme`: Current theme ('light' or 'dark')
- `toggleTheme()`: Function to switch between themes
- `setTheme(theme)`: Function to set a specific theme

```typescript
import { useTheme } from './contexts/ThemeContext';

function MyComponent() {
  const { theme, toggleTheme, setTheme } = useTheme();
  
  return (
    <button onClick={toggleTheme}>
      Current theme: {theme}
    </button>
  );
}
```

### 2. Theme Provider

The app is wrapped with `ThemeProvider` in `main.tsx`:

```typescript
<ThemeProvider>
  <App />
</ThemeProvider>
```

### 3. CSS Variables (`src/index.css`)

All colors are defined as CSS custom properties:

**Light Theme Variables:**
- `--primary-color`: #646cff
- `--bg-primary`: #ffffff
- `--text-primary`: #213547
- And many more...

**Dark Theme Variables:**
- `--primary-color`: #818cf8
- `--bg-primary`: #1a1a1a
- `--text-primary`: rgba(255, 255, 255, 0.87)
- And many more...

### 4. Theme Toggle Component

The `ThemeToggle` component provides a button with sun/moon icons:

```typescript
import ThemeToggle from './components/common/ThemeToggle';

<ThemeToggle />
```

## Usage in Components

### Using Theme Variables in CSS

```css
.my-component {
  background-color: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}

.my-button {
  background-color: var(--primary-color);
  color: var(--text-inverse);
}

.my-button:hover {
  background-color: var(--primary-hover);
}
```

### Accessing Theme in JavaScript

```typescript
import { useTheme } from '../contexts/ThemeContext';

function MyComponent() {
  const { theme } = useTheme();
  
  // Conditional logic based on theme
  const iconColor = theme === 'light' ? '#000' : '#fff';
  
  return <Icon color={iconColor} />;
}
```

## Available CSS Variables

### Colors

**Primary Colors:**
- `--primary-color`: Main brand color
- `--primary-hover`: Hover state
- `--primary-active`: Active/pressed state

**Background Colors:**
- `--bg-primary`: Main background
- `--bg-secondary`: Secondary background (cards, inputs)
- `--bg-tertiary`: Tertiary background
- `--bg-hover`: Hover state background
- `--bg-modal`: Modal overlay background

**Text Colors:**
- `--text-primary`: Primary text
- `--text-secondary`: Secondary text
- `--text-tertiary`: Tertiary/muted text
- `--text-inverse`: Inverse text (for colored backgrounds)

**Border Colors:**
- `--border-primary`: Primary borders
- `--border-secondary`: Secondary borders
- `--border-focus`: Focus state borders

**Status Colors:**
- `--success`: Success messages
- `--error`: Error messages
- `--warning`: Warning messages
- `--info`: Info messages

**Shadows:**
- `--shadow-sm`: Small shadow
- `--shadow-md`: Medium shadow
- `--shadow-lg`: Large shadow

## Theme Persistence

The theme preference is automatically saved to localStorage with the key `ano-theme-preference`. When a user returns to the app, their previous theme choice is restored.

## System Preference Detection

On first visit (when no theme is saved), the system detects the user's OS theme preference using:

```javascript
window.matchMedia('(prefers-color-scheme: dark)').matches
```

## Accessibility

### Reduced Motion

The theme system respects the `prefers-reduced-motion` media query. Users who have enabled reduced motion in their OS settings will see instant theme changes without animations.

### Keyboard Navigation

The ThemeToggle button is fully keyboard accessible:
- Tab to focus
- Enter/Space to toggle
- Clear focus indicators

### Screen Readers

The ThemeToggle button includes:
- `aria-label` for screen readers
- `title` attribute for tooltips
- Semantic button element

## Testing the Theme System

### Manual Testing

1. **Theme Toggle**: Click the theme toggle button in the navigation
2. **Persistence**: Refresh the page - theme should persist
3. **System Preference**: Clear localStorage and reload - should match system preference
4. **All Components**: Navigate through all pages to ensure consistent theming

### Verification Checklist

- [ ] Theme toggle button appears in navigation
- [ ] Clicking toggle switches between light and dark themes
- [ ] Theme persists after page refresh
- [ ] All text is readable in both themes
- [ ] All buttons and interactive elements are visible in both themes
- [ ] Form inputs are styled correctly in both themes
- [ ] Modals and overlays work in both themes
- [ ] Transitions are smooth (unless reduced motion is enabled)
- [ ] Focus indicators are visible in both themes

## Browser Support

The theme system uses modern CSS features:
- CSS Custom Properties (CSS Variables)
- `prefers-color-scheme` media query
- `prefers-reduced-motion` media query
- localStorage API

Supported browsers:
- Chrome/Edge 88+
- Firefox 89+
- Safari 14+

## Future Enhancements

Potential improvements:
- [ ] Additional theme options (e.g., high contrast, custom colors)
- [ ] Per-component theme overrides
- [ ] Theme preview before applying
- [ ] Scheduled theme switching (auto dark mode at night)
- [ ] Integration with Tailwind CSS for utility classes

## Requirements Validation

This implementation satisfies the following requirements:

✅ **Requirement 11.1**: Theme toggle switches between light and dark color schemes
✅ **Requirement 11.2**: Theme preference persisted in local storage
✅ **Requirement 11.3**: Previously selected theme loads on return
✅ **Requirement 11.4**: All UI components are readable and accessible in both themes
