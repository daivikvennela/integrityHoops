# Cognitive Score Calculator

## Overview

The Cognitive Score Calculator analyzes basketball game CSV files to calculate cognitive performance scores based on positive (+ve) and negative (-ve) evaluations across multiple cognitive skill categories.

## Formula

```
Score = (Positives / (Positives + Negatives)) × 100
```

**Result Range**: 0% to 100%
- **0%** = All negative evaluations
- **50%** = Equal positives and negatives
- **100%** = All positive evaluations

## Cognitive Skill Categories

The calculator analyzes 11 cognitive skill categories:

1. **Cutting & Screening** - Movement without the ball
2. **DM Catch** - Decision making on catch
3. **Driving** - Paint penetration ability
4. **Finishing** - Completing plays at the rim
5. **Footwork** - Movement technique
6. **Passing** - Ball distribution decisions
7. **Positioning** - Court positioning
8. **QB12 DM** - Quarterback decision making
9. **Relocation** - Off-ball repositioning
10. **Space Read** - Reading defensive spacing
11. **Transition** - Fast break execution

## Usage

### Command Line

```bash
# Basic usage - print report to console
python scripts/calculate_cog_score.py "path/to/game.csv"

# Save as JSON file
python scripts/calculate_cog_score.py "path/to/game.csv" --json output.json

# Save JSON without printing
python scripts/calculate_cog_score.py "path/to/game.csv" --json output.json --no-print
```

### Python API

```python
from src.processors.cog_score_calculator import CogScoreCalculator

# Create calculator
calculator = CogScoreCalculator('path/to/game.csv')

# Get full report
report = calculator.get_full_report()

# Print formatted report
calculator.print_report()

# Save as JSON
calculator.save_report_json('output.json')
```

### Web API

**Endpoint**: `POST /api/cog-scores/calculate-from-csv`

**Request**: Multipart form data with CSV file

```javascript
const formData = new FormData();
formData.append('file', csvFile);

const response = await fetch('/api/cog-scores/calculate-from-csv', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result.data.overall_score); // e.g., 64.91
```

## Output Format

### Console Output

```
======================================================================
COGNITIVE SCORE REPORT: 10.04.25 Heat v Bucks Team
======================================================================

Overall Cognitive Score: 64.91%
Total Instances: 992

----------------------------------------------------------------------
Cognitive Skill             Positive   Negative      Total      Score
----------------------------------------------------------------------
Cutting & Screeing                62         83        145     42.76%
DM Catch                         173         71        244     70.90%
Driving                           99         15        114     86.84%
...
======================================================================
```

### JSON Output

```json
{
  "overall_score": 64.91,
  "breakdown": {
    "Cutting & Screeing": {
      "positive": 62,
      "negative": 83,
      "total": 145,
      "score": 42.76
    },
    "DM Catch": {
      "positive": 173,
      "negative": 71,
      "total": 244,
      "score": 70.90
    },
    ...
  },
  "metadata": {
    "game": "10.04.25 Heat v Bucks Team",
    "total_instances": 992,
    "csv_file": "10.06.25 Heat v Bucks (1).csv"
  }
}
```

## Example Results

**10.06.25 Heat v Bucks Game**:
- Overall Score: **64.91%**
- Best Categories: Driving (86.84%), Passing (79.56%), Finishing (79.31%)
- Needs Improvement: Footwork (19.05%), Cutting & Screening (42.76%)

## Integration

The calculator is integrated into the Analytics Dashboard:

1. Navigate to `/analytics-dashboard`
2. Scroll to "CSV ETL Upload" section
3. Select your game CSV file
4. Click "Upload"
5. View the calculated cognitive score in the alert
6. Check browser console for detailed breakdown

## Files

- `src/processors/cog_score_calculator.py` - Core calculation logic
- `scripts/calculate_cog_score.py` - CLI tool
- `scripts/heat_bucks_report.json` - Example output
- `src/core/app.py` - Web API endpoint (`/api/cog-scores/calculate-from-csv`)
- `static/js/analytics_dashboard.js` - Frontend integration

