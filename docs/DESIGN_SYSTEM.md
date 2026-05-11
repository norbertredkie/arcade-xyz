# Gen Z UI Design System

Arcade.XYZ v3 UI aesthetic: **TikTok meets Fortnite**

**Vibe:** Young, energetic, playful, neon. NOT corporate. NOT boring.

---

## Color Palette

### Primary Colors

**Hot Pink #FF006E**
- Call-to-action buttons
- Highlights
- Primary actions
- Use for: CTAs, submit buttons, active states

**Electric Cyan #00D9FF**
- Accents
- Hover states
- Energy/focus
- Use for: Secondary actions, hovers, focus rings

**Lime #39FF14**
- Success states
- Credits earned
- Achievements
- Use for: "Success!", notifications, badges

### Background & Surface

**Deep Purple/Black #0a0e27**
- Main background (dark mode always)
- Keeps theme dark, neon pops

**Surface (Glassmorphism)**
- `rgba(255,255,255,0.05)` - Base surface
- `rgba(255,255,255,0.08)` - Hover state
- Frosted glass effect with backdrop blur

### Text

**Primary:** `#FFFFFF` (white, full opacity)
**Secondary:** `rgba(255,255,255,0.7)` (70% opacity)
**Muted:** `rgba(255,255,255,0.5)` (50% opacity)

### Utility Colors

- **Error:** `#FF4444` (red)
- **Warning:** `#FFAA00` (orange)
- **Success:** `#39FF14` (lime)
- **Info:** `#00D9FF` (cyan)

---

## Typography

### Font Families

**Display (Headings)**
```css
font-family: 'Poppins', sans-serif;
font-weight: 700-800;
```
- Bold, playful, friendly
- Use for: Headings, titles, CTAs
- Makes content feel young

**Body (Text)**
```css
font-family: 'Outfit', sans-serif;
font-weight: 400-600;
```
- Modern, clean, readable
- Use for: Body copy, descriptions, labels
- Professional but friendly

**Code**
```css
font-family: 'Courier New', monospace;
```
- Use for: Code snippets, JSON, technical text

### Size Scale

```
xs:  12px
sm:  14px
base: 16px  ← default
lg:  18px
xl:  20px
2xl: 24px
3xl: 30px
4xl: 36px
5xl: 48px   ← page titles
```

### Weight Scale

```
light:     300
normal:    400  ← body text
medium:    500
semibold:  600
bold:      700   ← headings
extrabold: 800   ← display
```

---

## Components

### Button (Primary)

```css
/* Hot Pink with glow */
background: linear-gradient(135deg, #FF006E, #FF1493);
padding: 12px 24px;
border-radius: 16px;
font-weight: 700;
font-size: 16px;
color: #FFFFFF;
border: none;
cursor: pointer;
box-shadow: 0 0 20px rgba(255, 0, 110, 0.4);
transition: all 0.2s ease;

/* Hover */
transform: scale(1.05);
box-shadow: 0 0 30px rgba(255, 0, 110, 0.6);

/* Active */
transform: scale(0.95);
```

**Usage:**
```html
<button className="btn-primary">✨ Generate Map</button>
```

### Button (Secondary)

```css
/* Electric Cyan */
background: linear-gradient(135deg, #00D9FF, #00FFFF);
padding: 12px 24px;
border-radius: 16px;
font-weight: 600;
color: #0a0e27;
border: none;
box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
transition: all 0.2s ease;

/* Hover */
transform: scale(1.05);
box-shadow: 0 0 30px rgba(0, 217, 255, 0.5);
```

### Button (Outline)

```css
background: transparent;
color: #00D9FF;
border: 2px solid #00D9FF;
padding: 12px 24px;
border-radius: 16px;
transition: all 0.2s ease;

/* Hover */
background: rgba(0, 217, 255, 0.1);
box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);
```

### Card (Glassmorphism)

```css
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 16px;
padding: 20px;
transition: all 0.2s ease;

/* Hover */
background: rgba(255, 255, 255, 0.08);
border-color: rgba(0, 217, 255, 0.3);
box-shadow: 0 0 20px rgba(0, 217, 255, 0.2);
```

### Input

```css
background: rgba(255, 255, 255, 0.05);
border: 1px solid rgba(255, 255, 255, 0.1);
border-radius: 12px;
padding: 12px 16px;
color: #FFFFFF;
font-size: 16px;
font-family: 'Outfit', sans-serif;
transition: all 0.2s ease;

::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

/* Focus */
:focus {
  background: rgba(255, 255, 255, 0.08);
  border-color: #00D9FF;
  box-shadow: 0 0 10px rgba(0, 217, 255, 0.3);
  outline: none;
}
```

### Badge

```css
display: inline-block;
padding: 6px 12px;
border-radius: 20px;
font-size: 12px;
font-weight: 600;
background: rgba(0, 217, 255, 0.1);
color: #00D9FF;
border: 1px solid #00D9FF;
```

**Examples:**
```html
<span className="badge">✨ New</span>
<span className="badge">🔥 Hot</span>
<span className="badge">💪 Pro</span>
```

### Dialog/Modal

```css
background: #0a0e27;
border-radius: 20px;
padding: 24px;
box-shadow: 0 20px 60px rgba(255, 0, 110, 0.2);
border: 1px solid rgba(255, 0, 110, 0.2);
```

---

## Animations

### Fade In
```css
@keyframes fadeIn {
  0% { opacity: 0; }
  100% { opacity: 1; }
}

animation: fadeIn 0.3s ease-in;
```

### Slide Up
```css
@keyframes slideUp {
  0% {
    opacity: 0;
    transform: translateY(10px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

animation: slideUp 0.3s ease-out;
```

### Bounce
```css
@keyframes bounce {
  0% { transform: scale(0.95); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

animation: bounce 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Pulse
```css
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

animation: pulse 2s ease-in-out infinite;
```

### Glow (Neon)
```css
@keyframes glow {
  0% {
    box-shadow: 0 0 0px rgba(255, 0, 110, 0);
  }
  100% {
    box-shadow: 0 0 20px rgba(255, 0, 110, 0.6);
  }
}

animation: glow 0.3s ease-out;
```

---

## Spacing Scale

```
xs:  4px
sm:  8px
md:  12px
lg:  16px
xl:  20px
2xl: 24px
3xl: 32px
4xl: 40px
5xl: 48px
6xl: 60px
```

**Use consistently:**
- Padding inside cards: `lg` (16px)
- Gap between elements: `md` (12px)
- Section margins: `3xl` (32px)
- Page padding: `2xl` (24px)

---

## Shadows

```css
sm: 0 2px 4px rgba(0, 0, 0, 0.1);
md: 0 4px 12px rgba(0, 0, 0, 0.15);
lg: 0 8px 24px rgba(0, 0, 0, 0.2);
xl: 0 12px 32px rgba(0, 0, 0, 0.25);

/* Neon glows */
neon-pink: 0 0 20px rgba(255, 0, 110, 0.4);
neon-cyan: 0 0 20px rgba(0, 217, 255, 0.3);
neon-lime: 0 0 20px rgba(57, 255, 20, 0.3);
```

---

## Language & Tone

Everything is emoji-heavy and playful:

### Buttons
- ✨ Generate Map
- 🔥 Trending
- 💪 Pro Features
- 🎮 Play Map
- 💰 Buy Credits
- 🚀 Publish
- 💡 Optimize

### Notifications
- ✅ Success!
- ⚠️ Warning
- ❌ Error
- ℹ️ Info
- 🎁 Bonus!

### States
- ⏳ Loading...
- 🔄 Updating...
- ✨ Done!
- 🚀 Ready to go!

---

## Responsive Design

### Breakpoints

```
xs: 0px
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

### Mobile-First Approach

```css
/* Mobile */
padding: 16px;
font-size: 14px;

/* Tablet */
@media (min-width: 768px) {
  padding: 20px;
  font-size: 16px;
}

/* Desktop */
@media (min-width: 1024px) {
  padding: 24px;
  font-size: 16px;
}
```

---

## Dark Mode (Always)

Arcade.XYZ is **always dark mode**. No light mode option.

```css
background: #0a0e27;
color: #FFFFFF;
```

This is intentional:
- Neon colors pop on dark
- Gen Z prefers dark mode
- Reduces eye strain
- Looks "modern"

---

## Accessibility

**Contrast Ratios:**
- All text vs background: Minimum 4.5:1
- Pink text on black: 8.5:1 ✅
- Cyan text on black: 8.2:1 ✅
- Lime text on black: 7.8:1 ✅

**Focus States:**
- Always visible blue outline or glow
- Keyboard navigation fully supported
- Screen reader compatible

**Reduced Motion:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Implementation (React/Tailwind)

```typescript
// colors.ts
export const colors = {
  primary: '#FF006E',
  secondary: '#00D9FF',
  accent: '#39FF14',
  bg: '#0a0e27',
};

// Button.tsx
export function Button({ children, variant = 'primary' }) {
  const styles = {
    primary: 'bg-gradient-to-br from-[#FF006E] to-[#FF1493] text-white',
    secondary: 'bg-gradient-to-br from-[#00D9FF] to-[#00FFFF] text-[#0a0e27]',
    outline: 'border-2 border-[#00D9FF] text-[#00D9FF]',
  };

  return (
    <button className={`
      px-6 py-3 rounded-2xl font-bold
      transition-all duration-200
      hover:scale-105
      ${styles[variant]}
    `}>
      {children}
    </button>
  );
}

// Card.tsx
export function Card({ children }) {
  return (
    <div className={`
      bg-white/5 backdrop-blur-md
      border border-white/10 rounded-2xl
      p-5 transition-all duration-200
      hover:bg-white/8 hover:border-[#00D9FF]/30
      hover:shadow-[0_0_20px_rgba(0,217,255,0.2)]
    `}>
      {children}
    </div>
  );
}
```

---

## UI Kit Export

Access design tokens in code:

```python
from src.design_system import DESIGN_TOKENS

print(DESIGN_TOKENS['colors']['primary'])  # #FF006E
print(DESIGN_TOKENS['typography']['fonts']['display'])  # Poppins
print(DESIGN_TOKENS['components']['button_primary'])
```

---

## Design Checklist

Before shipping any UI:

- [ ] Uses hot pink (#FF006E) or cyan (#00D9FF) for CTAs
- [ ] Has glassmorphism cards (blur + transparency)
- [ ] Uses Poppins or Outfit fonts
- [ ] Animations are smooth (0.2s - 0.5s)
- [ ] Has emoji in labels/buttons
- [ ] Dark background (#0a0e27)
- [ ] Neon glows on hover
- [ ] Responsive on mobile
- [ ] Accessible (contrast, focus states)
- [ ] Feels "young" and "energetic"

---

**Last Updated:** May 2025
**Version:** 3.0.0
