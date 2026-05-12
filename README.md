# Arcade.XYZ - Create Maps. Earn Money. 🚀

A neon-powered gaming platform for creating AI-generated maps and earning credits.

## Features

- 🎮 **Dark Mode Optimized** - Navy/black background with neon accents
- ✨ **Neon Aesthetic** - Magenta (#FF006E), Green (#00FF00), and Cyan (#00FFFF) color scheme
- 🤖 **AI Map Generation** - Generate custom game maps with AI
- 💳 **Credit System** - Buy and spend credits for map generation
- 📊 **Pricing Tiers** - Free, Pro, and Studio subscription plans
- 🛍️ **Credit Shop** - Purchase credits with bonus rewards
- 📱 **Mobile Responsive** - Works seamlessly on all devices
- ⚡ **Gaming Vibe** - Energetic, arcade-inspired interface

## Tech Stack

- **Framework**: Next.js 14
- **Styling**: Tailwind CSS + Custom CSS
- **Language**: TypeScript
- **Components**: React Server & Client Components

## Project Structure

```
arcade-xyz/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   └── globals.css         # Global styles & neon effects
├── components/
│   ├── Header.tsx          # Logo + Credit counter
│   ├── MapGenerator.tsx    # Map generation UI
│   ├── PricingTiers.tsx    # Pricing section
│   ├── CreditShop.tsx      # Credit purchase
│   └── Footer.tsx          # Footer links
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) to see the app.

## Design System

### Colors
- **Neon Magenta**: #FF006E
- **Neon Green**: #00FF00
- **Neon Cyan**: #00FFFF
- **Dark BG**: #0a0e27
- **Card BG**: #1a1f3a

### Typography
- **Headings**: Arial Black, Impact (Arcade style)
- **Body**: System fonts (Roboto, Ubuntu, etc.)

### Effects
- Neon glow shadows
- Text shadows for depth
- Hover animations and scale transforms
- Arcade flicker animation

## Features Overview

### Header
- Arcade.XYZ logo with magenta glow
- Real-time credit counter (green display)
- Fixed navigation bar

### Map Generator
- Bold hero section: "Create Maps. Earn Money. 🚀"
- Text input for map descriptions
- Quick suggestion buttons
- AI suggestion cards with apply functionality
- Main CTA button with lightning emoji

### Pricing Tiers
- **FREE**: 100 credits/month
- **PRO**: 1,000 credits/month (featured)
- **STUDIO**: 10,000 credits/month

### Credit Shop
- 50 credits - $0.99
- 500 credits - $7.99 (25% bonus, best value)
- 2,500 credits - $29.99 (50% bonus)

### Footer
- Product links
- Community links (Discord, Twitter, GitHub)
- Legal links (Privacy, Terms, etc.)

## Customization

### Change Colors
Edit `tailwind.config.js`:
```js
colors: {
  neon: {
    magenta: "#FF006E",
    green: "#00FF00",
    cyan: "#00FFFF",
  }
}
```

### Adjust Glow Effects
Edit `app/globals.css`:
```css
.neon-glow-magenta {
  box-shadow: 0 0 10px rgba(255, 0, 110, 0.6), /* adjust values */
}
```

### Modify Content
- Update pricing in `components/PricingTiers.tsx`
- Change credit packages in `components/CreditShop.tsx`
- Edit suggestions in `components/MapGenerator.tsx`

## Performance

- Optimized images and lazy loading
- CSS-in-JS for dynamic styles
- Server components for initial load
- Client components for interactivity

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

Private - Arcade.XYZ © 2024

---

**Built with ⚡ for gamers**
