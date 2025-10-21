# 🎨 Theme Switching System - IntegrityHoops

## Overview
IntegrityHoops now features a professional theme switching system that allows you to toggle between the default theme and the Miami Heat professional theme.

## 🚀 Quick Access

### Settings Page
Navigate to the full settings page:
```
http://localhost:8000/settings
```

### Floating Theme Switcher
Look for the **floating palette button** in the bottom-right corner of any page to quickly switch themes!

## 🎯 Available Themes

### 1. Default Theme
- **Color Scheme**: Purple gradient with light backgrounds
- **Design**: Clean Bootstrap 5 interface
- **Best For**: Standard data viewing and analysis
- **Fonts**: System fonts (Bootstrap default)

### 2. Miami Heat Professional
- **Color Scheme**: Dark black with neon red accents
- **Design**: Sleek, professional sports analytics interface
- **Best For**: High-impact presentations and professional dashboards
- **Fonts**: Premium fonts (Orbitron, Rajdhani, Inter)
- **Special Effects**: Neon glows, animations, pulsing effects

## 💡 How to Switch Themes

### Method 1: Floating Widget (Recommended)
1. Look for the **floating palette icon** in the bottom-right corner
2. Click the icon to open the theme selector
3. Choose your preferred theme
4. Click to apply instantly!

### Method 2: Settings Page
1. Navigate to **Settings** from the main navigation
2. Browse the theme previews
3. Click on your preferred theme
4. Click **Apply Theme** button
5. Changes apply immediately!

## 🔧 Technical Details

### Theme Persistence
Your theme preference is **automatically saved** in your browser's localStorage and will persist across:
- Page refreshes
- Browser sessions
- Different pages in the app

### How It Works
```javascript
// The theme is stored in localStorage
localStorage.getItem('integrityHoopsTheme')  // Returns: 'default' or 'heat'

// You can also programmatically switch themes using:
IntegrityHoopsTheme.setTheme('heat')     // Switch to Miami Heat
IntegrityHoopsTheme.setTheme('default')  // Switch to Default
IntegrityHoopsTheme.toggleTheme()        // Toggle between themes
IntegrityHoopsTheme.getCurrentTheme()    // Get current theme
```

## 📁 File Structure

```
testApp1/
├── static/
│   ├── css/
│   │   ├── miami-heat-theme.css          # Miami Heat theme styles
│   │   └── MIAMI_HEAT_THEME_GUIDE.md     # Theme component guide
│   └── js/
│       └── theme-manager.js               # Theme switching logic
├── templates/
│   ├── base.html                          # Includes theme switcher
│   ├── settings.html                      # Full settings page
│   ├── theme_switcher_widget.html         # Floating switcher widget
│   └── heat_theme_demo.html               # Theme component showcase
```

## 🌐 Pages with Theme Support

All pages that extend `base.html` automatically include the theme switcher:
- ✅ Home (`/`)
- ✅ SmartDash (`/smartdash`)
- ✅ Players (`/players`)
- ✅ Player Management (`/player-management`)
- ✅ Settings (`/settings`)
- ✅ And more...

## 🎨 Preview Themes Before Applying

Visit the **Miami Heat Theme Demo** to see all components:
```
http://localhost:8000/heat-theme-demo
```

This showcases:
- Typography styles
- Buttons and forms
- Cards and statistics
- Tables and progress bars
- Badges, alerts, and animations
- And more!

## 🔥 Miami Heat Theme Features

When you enable the Miami Heat theme, you get access to:

### Visual Effects
- **Neon red glows** on hover and focus
- **Pulsing animations** for important elements
- **Smooth transitions** throughout the interface
- **Animated progress bars** with shimmer effect

### Professional Typography
- **Orbitron**: For large numbers and display text
- **Rajdhani**: For headers and navigation
- **Inter**: For body text and content

### Color Coding
- **Red (#F9423A)**: Primary actions, highlights
- **Gold (#FFB81C)**: Special achievements, MVP status
- **Black/Dark Gray**: Sleek professional backgrounds
- **White/Off-White**: Clean, readable text

### Special Classes
Use these in your HTML when Heat theme is active:
```html
<h1 class="text-neon-red">TITLE</h1>
<button class="btn-heat btn-heat-primary">Action</button>
<div class="heat-card neon-red-glow">Content</div>
<div class="heat-stat-card">
    <div class="heat-stat-value">94.2</div>
    <div class="heat-stat-label">Rating</div>
</div>
```

## 🛠️ Customization

### Adding the Theme Switcher to New Pages
If you create a new page that doesn't extend `base.html`:

```html
<!-- Add before </body> -->
{% include 'theme_switcher_widget.html' %}
```

### Creating Theme-Aware Components
```javascript
// Listen for theme changes
window.addEventListener('themeChanged', function(event) {
    const newTheme = event.detail.theme;
    console.log('Theme changed to:', newTheme);
    // Update your components accordingly
});
```

### Conditional Styling Based on Theme
```html
<div class="my-component">
    Content
</div>

<style>
    /* Default theme */
    .my-component {
        background: white;
        color: #333;
    }
    
    /* Miami Heat theme */
    body.theme-heat .my-component {
        background: #1A1A1A;
        color: #F9423A;
    }
</style>
```

## 📱 Responsive Design

Both themes are fully responsive and work perfectly on:
- 💻 Desktop (1920px+)
- 💻 Laptop (1024px - 1920px)
- 📱 Tablet (768px - 1024px)
- 📱 Mobile (< 768px)

## 🎯 Best Practices

1. **Test both themes** when creating new pages
2. **Use theme-aware classes** for consistency
3. **Avoid hard-coded colors** - use CSS variables
4. **Check contrast** in both themes for accessibility
5. **Preview on different devices** for responsive behavior

## 🔍 Troubleshooting

### Theme Not Applying?
1. Clear browser cache (Cmd/Ctrl + Shift + R)
2. Check browser console for errors
3. Verify localStorage is enabled in your browser

### Theme Resets on Refresh?
- Check if localStorage is being cleared by browser settings
- Try a different browser
- Check browser privacy settings

### Floating Widget Not Showing?
- Verify `base.html` includes the widget
- Check for JavaScript errors in console
- Ensure Font Awesome is loaded (for icons)

## 🎨 Future Enhancements

Coming soon:
- Additional theme options (Lakers, Celtics, etc.)
- Custom color picker
- Font size adjustments
- Dark/Light mode toggle for each theme
- Theme scheduler (auto-switch by time of day)

## 📖 Additional Resources

- **Miami Heat Theme Guide**: `/static/css/MIAMI_HEAT_THEME_GUIDE.md`
- **Theme Demo**: http://localhost:8000/heat-theme-demo
- **Settings Page**: http://localhost:8000/settings

---

**Built with ❤️ for IntegrityHoops Basketball Analytics**

*Enjoy your personalized theme experience!* 🏀🔥
