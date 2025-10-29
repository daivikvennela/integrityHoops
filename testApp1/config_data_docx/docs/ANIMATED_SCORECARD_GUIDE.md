# Animated Scorecard Guide

## Overview

The Animated Scorecard is an NBA 2K and Madden-inspired visualization dashboard that transforms basketball cognitive CSV data into a stunning, animated presentation. It features a black background with neon red accents (#F9423A) and provides comprehensive game analytics through circular indicators, horizontal bars, and pie charts.

## Features

### Visual Components

1. **Header Section**
   - Player/Team information
   - Game date and opponent
   - PPP (Points Per Possession) stats
   - Shared Cognition percentage
   - Game moments and turnovers
   - Time modifier

2. **On Ball Cognition (Left Section)**
   - Overall percentage display
   - Space Read circular indicator
   - Decision on the Catch circular indicator
   - Driving circular indicator
   - QB12 Decision Making circular indicator
   - Each shows positive/negative ratios

3. **Technical Breakdown (Center Section)**
   - Overall percentage display
   - Horizontal bar charts for:
     - Read the Length
     - Teammate on the Move
     - Step to Ball
     - Patient Pickups
     - Read Length - Finishing
     - Ball Security
     - Earn a Foul
     - Physicality - Finishing
     - Stride Pivot
     - Stride Holds

4. **Off Ball Cognition (Right Section)**
   - Overall percentage display
   - Positioning circular indicator
   - Cutting & Screening circular indicator
   - Relocation circular indicator
   - Transition circular indicator

5. **Shot Distribution (Top Right)**
   - Animated pie chart
   - Shot type breakdown (3PT, Deep 2, Short 2, Long 2)
   - Points scored display

### Animations

- **Card Entrance**: Slides up from bottom with fade-in (1s)
- **Header Fade**: Fades in at 0.5s
- **Circular Progress**: Draws progressively from 1s onwards
- **Counter Animation**: Numbers animate from 0 to target value
- **Bar Charts**: Fill horizontally with staggered timing
- **Pie Chart**: Draws segments sequentially at 2.5s
- **Glow Effects**: Pulsing neon red shadows on hover
- **Parallax Scroll**: Subtle depth effect when scrolling

## How to Use

### Accessing the Animated Scorecard

1. Navigate to `/animated-scorecard` in the application
2. Or click "Scorecard" in the navigation bar
3. Or access from Analytics Dashboard → "Animated Scorecard" button

### Uploading Data

1. **Upload New CSV File**
   - Click "Upload Game Data" section
   - Select a processed basketball cognitive CSV file
   - Click "Generate Scorecard" button
   - The system will process the data and display the animated scorecard

2. **Select from Recent Files**
   - View list of recently processed files
   - Click on any file to load its scorecard instantly

### CSV Data Format

The animated scorecard expects processed cognitive CSV files with the following columns:

- `Timeline`: Game timeline information (e.g., "10.04.25 Heat v Bucks Team")
- `Row`: Category name (Space Read, DM Catch, Driving, etc.)
- `BREAKDOWN`: Performance breakdown with +ve/-ve indicators
- `Shot Location`: Shot type (3pt, Deep 2, Short 2, Long 2)
- `Shot Outcome`: Made, Miss, Fouled
- Additional cognitive performance columns

### Example Data Flow

```
CSV Upload → Backend Processing → Data Extraction →
JSON Response → Frontend Animations → Visual Display
```

## Technical Implementation

### Backend

**File**: `src/processors/basketball_cognitive_processor.py`

Method: `generate_animated_scorecard_data(df)`
- Extracts game information
- Calculates On Ball metrics
- Calculates Technical Breakdown metrics
- Calculates Off Ball metrics
- Calculates Shot Distribution

### Routes

**File**: `src/core/app.py`

1. `GET /animated-scorecard` - Main dashboard page
2. `GET /animated-scorecard/<filename>` - Scorecard with specific file
3. `GET /api/scorecard-data/<filename>` - JSON API endpoint

### Frontend

**Files**:
- `templates/animated_scorecard.html` - HTML structure
- `static/css/animated-scorecard.css` - Styling and animations
- `static/js/animated-scorecard.js` - Animation logic

## Customization

### Color Scheme

The scorecard uses the following colors:
- **Primary**: `#F9423A` (Neon Red)
- **Background**: `#000` (Black)
- **Dark Gray**: `#1a1a1a`
- **Glow**: `rgba(249, 66, 58, 0.6)`

To customize colors, edit `animated-scorecard.css`:

```css
:root {
    --neon-red: #F9423A;
    --neon-red-glow: rgba(249, 66, 58, 0.6);
    --black-base: #000;
    --dark-gray: #1a1a1a;
}
```

### Animation Timing

Adjust animation delays in `animated-scorecard.css`:

```css
.circular-metric:nth-child(1) { animation-delay: 1s; }
.bar-metric:nth-child(1) { animation-delay: 1.5s; }
```

Or in `animated-scorecard.js`:

```javascript
setTimeout(() => {
    animateCircularIndicators();
    animateHorizontalBars();
    animateShotDistribution(data);
}, 500); // Main delay
```

## Performance Optimization

1. **Lazy Loading**: Animations start after DOM is fully loaded
2. **RequestAnimationFrame**: Used for smooth 60fps animations
3. **CSS Transforms**: Hardware-accelerated transformations
4. **Staggered Loading**: Sequential animations prevent performance bottlenecks

## Browser Compatibility

- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support (with fallback for backdrop-filter)
- **Edge**: Full support
- **Mobile**: Responsive design with touch support

## Troubleshooting

### Animations Not Playing

1. Check browser console for JavaScript errors
2. Verify CSV data is properly formatted
3. Ensure data contains required columns (Timeline, Row, BREAKDOWN)
4. Clear browser cache and reload

### Data Not Displaying

1. Verify CSV file is a processed cognitive performance file
2. Check that file exists in processed folder
3. Review Flask logs for processing errors
4. Ensure BasketballCognitiveProcessor is working correctly

### Styling Issues

1. Check that `animated-scorecard.css` is loaded
2. Verify no CSS conflicts with base theme
3. Test in different browsers
4. Use browser dev tools to inspect elements

## Future Enhancements

Planned improvements:
- Real-time data updates via WebSocket
- Export scorecard as image/PDF
- Comparison view (multiple games)
- Custom theme selection
- Player photo integration
- Advanced filters and sorting
- Interactive tooltips with detailed stats

## API Reference

### GET /api/scorecard-data/<filename>

Returns JSON data for scorecard visualization.

**Response Format**:
```json
{
    "success": true,
    "data": {
        "date": "10.06.25",
        "player": "Miami Heat",
        "opponent": "MIL",
        "ppp": 7,
        "positive_count": 420,
        "negative_count": 217,
        "shared_cognition": 66.0,
        "turnovers": 18,
        "on_ball": {
            "overall_percentage": 69.7,
            "space_read": {...},
            "dm_catch": {...},
            "driving": {...},
            "qb12": {...}
        },
        "technical": {
            "overall_percentage": 67.4,
            "read_the_length": {...},
            ...
        },
        "off_ball": {
            "overall_percentage": 61.5,
            "positioning": {...},
            ...
        },
        "shot_distribution": {
            "three_pt": {...},
            "points_scored": 15,
            ...
        }
    }
}
```

## Support

For issues or questions:
1. Check this guide first
2. Review Flask application logs
3. Inspect browser console for errors
4. Test with sample data
5. Contact development team

## Credits

Inspired by:
- NBA 2K player card designs
- Madden player pop-ups
- Modern sports analytics dashboards

Built with:
- Flask (Backend)
- JavaScript (Animations)
- CSS3 (Styling)
- HTML Canvas (Pie Chart)
- SVG (Circular Progress)

