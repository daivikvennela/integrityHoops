# 🏀 Miami Heat Professional Theme Guide

## Overview
A clean, sleek, professional dark interface with neon red accents inspired by the Miami Heat. Perfect for basketball analytics and sports data visualization.

## Quick Start

### 1. Add to Your HTML Template
```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/miami-heat-theme.css') }}">
```

### 2. View the Demo
Navigate to: **http://localhost:8000/heat-theme-demo**

## Color Palette

### Primary Colors
- **Heat Red**: `#F9423A` - Main brand color
- **Heat Black**: `#000000` - Primary background
- **Heat Dark Gray**: `#0A0A0A` - Secondary background
- **Heat Mid Gray**: `#1A1A1A` - Card backgrounds
- **Heat Light Gray**: `#2A2A2A` - Borders and dividers

### Accent Colors
- **Heat Gold**: `#FFB81C` - Special highlights
- **Heat White**: `#FFFFFF` - Primary text
- **Heat Off-White**: `#F5F5F5` - Secondary text

## Typography

### Font Families
1. **Inter** - Body text and general content
2. **Rajdhani** - Headers and navigation
3. **Orbitron** - Display text and large numbers

### Usage Examples
```html
<h1>Display Heading (Orbitron)</h1>
<h2>Section Heading (Rajdhani)</h2>
<p>Body text (Inter)</p>
<p class="text-heat-red">Red colored text</p>
<p class="text-neon-red">Red text with glow effect</p>
```

## Components

### Buttons
```html
<!-- Primary Button -->
<button class="btn-heat btn-heat-primary">Click Me</button>

<!-- Outline Button -->
<button class="btn-heat btn-heat-outline">Outline</button>

<!-- Ghost Button -->
<button class="btn-heat btn-heat-ghost">Ghost</button>

<!-- Pulsing Button -->
<button class="btn-heat btn-heat-primary pulse-red">Pulse</button>
```

### Cards
```html
<!-- Standard Card -->
<div class="heat-card">
    <div class="heat-card-header">
        <h3>Card Title</h3>
    </div>
    <p>Card content goes here</p>
</div>

<!-- Card with Neon Glow -->
<div class="heat-card neon-red-glow">
    <h3>Glowing Card</h3>
    <p>Content</p>
</div>
```

### Statistics Cards
```html
<div class="heat-stat-card">
    <div class="heat-stat-value">94.2</div>
    <div class="heat-stat-label">Offensive Rating</div>
</div>
```

### Forms & Inputs
```html
<label class="heat-label">Player Name</label>
<input type="text" class="heat-input" placeholder="Enter name...">

<label class="heat-label">Position</label>
<select class="heat-select">
    <option>Point Guard</option>
    <option>Shooting Guard</option>
</select>
```

### Tables
```html
<table class="heat-table">
    <thead>
        <tr>
            <th>Player</th>
            <th>PPG</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Jimmy Butler</td>
            <td>22.9</td>
            <td><span class="heat-badge heat-badge-red">Active</span></td>
        </tr>
    </tbody>
</table>
```

### Navigation
```html
<nav class="heat-navbar">
    <div class="heat-container">
        <a href="/" class="heat-nav-link active">Home</a>
        <a href="/players" class="heat-nav-link">Players</a>
        <a href="/stats" class="heat-nav-link">Stats</a>
    </div>
</nav>
```

### Progress Bars
```html
<div class="heat-progress">
    <div class="heat-progress-bar" style="width: 75%;"></div>
</div>
```

### Badges
```html
<span class="heat-badge heat-badge-red">Elite</span>
<span class="heat-badge heat-badge-outline">Starter</span>
<span class="heat-badge heat-badge-gold">MVP</span>
```

### Alerts
```html
<div class="heat-alert">Standard alert</div>
<div class="heat-alert heat-alert-success">Success message</div>
<div class="heat-alert heat-alert-warning">Warning message</div>
```

## Layout System

### Container
```html
<div class="heat-container">
    <!-- Content with max-width and padding -->
</div>
```

### Grid System
```html
<!-- 2 Column Grid -->
<div class="heat-grid heat-grid-2">
    <div>Column 1</div>
    <div>Column 2</div>
</div>

<!-- 3 Column Grid -->
<div class="heat-grid heat-grid-3">
    <div>Column 1</div>
    <div>Column 2</div>
    <div>Column 3</div>
</div>

<!-- 4 Column Grid -->
<div class="heat-grid heat-grid-4">
    <div>Column 1</div>
    <div>Column 2</div>
    <div>Column 3</div>
    <div>Column 4</div>
</div>
```

## Special Effects

### Neon Red Effects
```html
<!-- Glowing Element -->
<div class="neon-red-glow">Element with glow</div>

<!-- Neon Border -->
<div class="neon-red-border">Element with neon border</div>

<!-- Pulsing Effect -->
<div class="pulse-red">Pulsing element</div>

<!-- Underlined Text -->
<span class="neon-red-underline">Underlined text</span>
```

### Animations
```html
<!-- Fade In Animation -->
<div class="fade-in">Fades in on load</div>

<!-- Loading Spinner -->
<div class="heat-spinner"></div>
```

## Utility Classes

### Spacing
```html
<!-- Margin Top -->
<div class="mt-1">Small margin top</div>
<div class="mt-2">Medium margin top</div>
<div class="mt-3">Large margin top</div>
<div class="mt-4">Extra large margin top</div>

<!-- Margin Bottom -->
<div class="mb-1">Small margin bottom</div>
<div class="mb-2">Medium margin bottom</div>
<div class="mb-3">Large margin bottom</div>
<div class="mb-4">Extra large margin bottom</div>

<!-- Padding -->
<div class="p-1">Small padding</div>
<div class="p-2">Medium padding</div>
<div class="p-3">Large padding</div>
<div class="p-4">Extra large padding</div>
```

### Text Alignment
```html
<div class="text-left">Left aligned</div>
<div class="text-center">Center aligned</div>
<div class="text-right">Right aligned</div>
```

### Shadows
```html
<div class="heat-shadow">Standard shadow</div>
<div class="heat-shadow-red">Red glow shadow</div>
```

## Dashboard Components

### Dashboard Header
```html
<div class="heat-dashboard-header">
    <h1 class="text-neon-red">DASHBOARD TITLE</h1>
    <p>Dashboard description</p>
</div>
```

### Section Title
```html
<h2 class="heat-section-title">SECTION NAME</h2>
```

### Divider
```html
<div class="heat-divider"></div>
```

## CSS Variables

You can customize the theme by overriding CSS variables:

```css
:root {
    --heat-red: #F9423A;
    --heat-black: #000000;
    --heat-gold: #FFB81C;
    /* ... and more */
}
```

## Responsive Design

The theme is fully responsive with breakpoints at:
- **1024px**: Tablets
- **768px**: Mobile devices

Grids automatically collapse on smaller screens.

## Best Practices

1. **Use semantic HTML** with theme classes
2. **Combine utility classes** for custom spacing
3. **Use neon effects sparingly** for emphasis
4. **Keep backgrounds dark** for the Miami Heat aesthetic
5. **Use Heat Red** for primary actions and highlights
6. **Apply font families** appropriately:
   - Orbitron for large numbers/stats
   - Rajdhani for headers
   - Inter for body text

## Integration with Existing Templates

To apply the theme to your existing pages:

1. Add the CSS link to your template
2. Replace generic classes with heat-themed classes
3. Wrap content in `heat-container`
4. Use `heat-card` for content sections
5. Replace buttons with `btn-heat` variants
6. Update tables with `heat-table` class

## Example Full Page Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Page - IntegrityHoops</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/miami-heat-theme.css') }}">
</head>
<body>
    <!-- Navigation -->
    <nav class="heat-navbar">
        <div class="heat-container">
            <h2 class="text-neon-red">🏀 INTEGRITY HOOPS</h2>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="heat-container">
        <div class="heat-dashboard-header fade-in">
            <h1 class="text-neon-red">PAGE TITLE</h1>
        </div>

        <section class="fade-in">
            <h2 class="heat-section-title">SECTION</h2>
            <div class="heat-card">
                <p>Your content here</p>
            </div>
        </section>
    </div>
</body>
</html>
```

## Support

For issues or questions about the Miami Heat theme:
1. Check the demo page at `/heat-theme-demo`
2. Review this guide
3. Inspect the CSS file for available classes

---

**Built with ❤️ for Professional Basketball Analytics**

*Theme inspired by Miami Heat's iconic black and red color scheme*
