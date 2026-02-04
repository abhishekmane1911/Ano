# Animations Quick Reference Guide

Quick reference for using animations and polish features in the Ano platform.

## Toast Notifications

```tsx
import { useToast } from './hooks/useToast';

function MyComponent() {
  const toast = useToast();

  // Success (green)
  toast.success('Profile saved successfully!');
  
  // Error (red)
  toast.error('Failed to send message');
  
  // Warning (orange)
  toast.warning('Connection unstable');
  
  // Info (blue)
  toast.info('New match available');
  
  // Custom duration (default is 3000ms)
  toast.success('Quick message', 1500);
}
```

## Loading Skeletons

```tsx
import { 
  LoadingSkeleton, 
  MessageSkeleton, 
  ProfileCardSkeleton, 
  ListSkeleton 
} from './components/common';

// Basic skeleton
<LoadingSkeleton variant="text" width="80%" />
<LoadingSkeleton variant="circular" width={40} height={40} />
<LoadingSkeleton variant="rectangular" height="200px" />

// Pre-built skeletons
<MessageSkeleton count={3} />
<ProfileCardSkeleton count={1} />
<ListSkeleton count={5} />

// Usage in component
{loading ? <MessageSkeleton count={5} /> : <MessageList messages={messages} />}
```

## Page Transitions

```tsx
import { PageTransition, FadeTransition, SlideTransition, ScaleTransition } from './components/common';

// Default transition (slide + fade)
<PageTransition>
  <YourComponent />
</PageTransition>

// Fade only
<FadeTransition>
  <YourComponent />
</FadeTransition>

// Slide from right
<SlideTransition>
  <YourComponent />
</SlideTransition>

// Scale effect
<ScaleTransition>
  <YourComponent />
</ScaleTransition>
```

## Animation Classes

### Fade Animations
```html
<div class="animate-fade-in">Fades in</div>
<div class="animate-fade-in-up">Fades in from bottom</div>
<div class="animate-fade-in-down">Fades in from top</div>
```

### Slide Animations
```html
<div class="animate-slide-in-left">Slides from left</div>
<div class="animate-slide-in-right">Slides from right</div>
```

### Scale Animations
```html
<div class="animate-scale-in">Scales up</div>
<div class="animate-scale-out">Scales down</div>
```

### Special Animations
```html
<div class="animate-bounce">Bounces</div>
<div class="animate-pulse">Pulses</div>
<div class="animate-shake">Shakes</div>
<div class="animate-spin">Spins</div>
```

### Hover Effects
```html
<div class="hover-lift">Lifts on hover</div>
<div class="hover-scale">Scales on hover</div>
<div class="hover-glow">Glows on hover</div>
<div class="hover-brighten">Brightens on hover</div>
```

### Transitions
```html
<div class="transition-all">Smooth transition</div>
<div class="transition-fast">Fast transition</div>
<div class="transition-slow">Slow transition</div>
```

### Delays
```html
<div class="animate-fade-in delay-100">Delayed 0.1s</div>
<div class="animate-fade-in delay-200">Delayed 0.2s</div>
<div class="animate-fade-in delay-300">Delayed 0.3s</div>
```

### Stagger Children
```html
<div class="stagger-children">
  <div>Item 1 (0.1s delay)</div>
  <div>Item 2 (0.2s delay)</div>
  <div>Item 3 (0.3s delay)</div>
</div>
```

## Loading Spinner

```html
<!-- Default spinner -->
<div class="spinner"></div>

<!-- Small spinner -->
<div class="spinner spinner-small"></div>

<!-- Large spinner -->
<div class="spinner spinner-large"></div>
```

## Framer Motion (Advanced)

```tsx
import { motion } from 'framer-motion';

// Basic animation
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -20 }}
  transition={{ duration: 0.3 }}
>
  Content
</motion.div>

// Hover and tap
<motion.button
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
>
  Click me
</motion.button>

// Drag
<motion.div
  drag="x"
  dragConstraints={{ left: -100, right: 100 }}
>
  Drag me
</motion.div>
```

## Common Patterns

### Loading State
```tsx
{loading ? (
  <MessageSkeleton count={5} />
) : (
  <MessageList messages={messages} />
)}
```

### Success Action
```tsx
const handleSave = async () => {
  try {
    await saveProfile();
    toast.success('Profile saved!');
  } catch (error) {
    toast.error('Failed to save profile');
  }
};
```

### Animated List
```tsx
<div className="stagger-children">
  {items.map(item => (
    <div key={item.id} className="hover-lift">
      {item.name}
    </div>
  ))}
</div>
```

### Modal with Animation
```tsx
<motion.div
  className="modal-overlay"
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
>
  <motion.div
    className="modal"
    initial={{ scale: 0.8, opacity: 0 }}
    animate={{ scale: 1, opacity: 1 }}
    exit={{ scale: 0.8, opacity: 0 }}
  >
    Modal content
  </motion.div>
</motion.div>
```

### Card with Hover
```tsx
<div className="hover-lift transition-all">
  <img src={avatar} alt="Profile" />
  <h3>Anonymous User</h3>
  <div className="tags">
    <span className="tag hover-scale">Interest</span>
  </div>
</div>
```

## Accessibility

All animations automatically respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  /* Animations are automatically disabled or minimized */
}
```

No additional code needed - it's built in!

## Performance Tips

1. **Use CSS animations for simple effects** (better performance)
2. **Use Framer Motion for complex animations** (automatic optimization)
3. **Avoid animating width/height** (use transform instead)
4. **Keep durations short** (200-400ms)
5. **Use will-change sparingly** (only when needed)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Need Help?

- Full documentation: `ANIMATIONS_IMPLEMENTATION.md`
- Verification checklist: `ANIMATIONS_VERIFICATION_CHECKLIST.md`
- Summary: `ANIMATIONS_SUMMARY.md`
