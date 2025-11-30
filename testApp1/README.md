# IntegrityHoops - Basketball Analytics Platform

A comprehensive basketball analytics platform for processing game performance data, calculating cognitive scores, and visualizing team/player statistics.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.12-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 🏀 Overview

IntegrityHoops processes game performance CSV files to calculate cognitive scores and team statistics across 10 performance categories. The platform provides interactive dashboards for analyzing team and player performance over time.

### Key Features

- **📊 Analytics Dashboard**: Interactive charts showing performance trends across games
- **🎯 10 Performance Categories**: Cutting & Screening, DM Catch, Finishing, Footwork, Passing, Positioning, QB12 DM, Relocation, Space Read, Transition
- **🧠 Temporal & Pressure Visualizations**: Plotly-powered time-series, shot-clock heatmaps, and team insight center with radar, synergy matrix, and EPA waterfall
- **📈 Cognitive Score Calculation**: Automated calculation of overall and category-specific scores
- **👥 Player Management**: Individual player tracking and performance comparison
- **📄 PDF Export**: Generate player performance cards in 2K/Madden style
- **🗄️ SQLite Database**: Persistent storage for all games, players, and statistics

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12 (recommended) or Python 3.8+
- pip (Python package installer)

### Installation

   ```bash
# 1. Navigate to project directory
   cd testApp1

# 2. Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
   pip install -r requirements.txt

# 4. Run the application
python main.py

# 5. Open your browser
# Navigate to: http://localhost:8080
```

---

## 📖 CSV Processing Algorithm

### **Complete Technical Documentation**
For detailed step-by-step processing pipeline, see:
### [**CSV_PROCESSING_ALGORITHM.md**](CSV_PROCESSING_ALGORITHM.md)

### Quick Summary

The platform processes CSV files through a 5-phase pipeline:

```
CSV File → Validation → Preprocessing → Score Calculation → Database Storage → Dashboard
```

**Input Format:**
- Filename: `MM.DD.YY TEAM v OPPONENT.csv`
- Example: `10.28.25 MIA v CHA.csv`
- Must contain "Row" column and 10 category columns

**Output:**
- Game record with unique ID
- Scorecard with 78 statistical fields
- Team cognitive score (overall and per-category)
- 10 statistics records (one per category)

**Key Calculation:**
```
Category Percentage = (Positive Count / (Positive + Negative Count)) × 100
Overall Cog Score = Average of all category percentages
```

---

## 📁 Project Structure

```
testApp1/
├── main.py                          # Application entry point
├── CSV_PROCESSING_ALGORITHM.md      # Detailed processing documentation
├── requirements.txt                 # Python dependencies
│
├── src/
│   ├── core/
│   │   ├── app.py                   # Main Flask application
│   │   └── data/
│   │       └── basketball.db        # SQLite database
│   │
│   ├── models/
│   │   ├── game.py                  # Game data model
│   │   ├── player.py                # Player data model
│   │   └── scorecard.py             # Scorecard data model (78 fields)
│   │
│   ├── processors/
│   │   ├── csv_preprocessor.py      # CSV splitting and validation
│   │   ├── csv_to_database_importer.py  # Main processing pipeline
│   │   └── cog_score_calculator.py  # Cognitive score calculations
│   │
│   ├── services/
│   │   ├── game_validator.py        # Duplicate detection
│   │   └── pdf_export_service.py    # PDF generation
│   │
│   ├── utils/
│   │   ├── game_id_generator.py     # Unique ID generation
│   │   └── statistics_calculator.py # Percentage calculations
│   │
│   ├── database/
│   │   └── db_manager.py            # Database operations
│   │
│   └── api/
│       ├── database_viz_api.py      # Data visualization API
│       └── player_management_dashboard.py  # Player management API
│
├── templates/
│   ├── analytics_dashboard.html     # Main analytics dashboard
│   ├── player_management.html       # Player comparison page
│   └── scorecard.html               # Game scorecard view
│
├── static/
│   ├── js/
│   │   ├── analytics_dashboard.js   # Chart rendering and interactions
│   │   └── database_viz.js          # Data visualization logic
│   └── css/
│       └── styles.css               # Custom styling
│
└── testcases/
    └── test_csvs/                   # Sample game CSV files
```

---

## 🎯 Usage Guide

### 1. Upload Game CSV

Navigate to the **Scorecard** tab and:
1. Drag & drop your CSV file or click to browse
2. File must follow format: `MM.DD.YY TEAM v OPPONENT.csv`
3. CSV will be automatically validated and processed

### 2. View Analytics Dashboard

The analytics dashboard displays:
- **Line chart** showing performance trends over time
- **X-axis**: Game dates (one point per game)
- **Y-axis**: Performance percentages (0-100%)
- **Category filter**: Select specific categories or view all
- **Toggle buttons**: Show/hide individual category lines
- **Date range slider**: Zoom into specific time periods

### 3. Compare Players

In the **Player Management** tab:
1. Select players from dropdown menus
2. Click "Compare Selected Players"
3. View side-by-side comparison charts
4. Export comparison as PDF

### 4. Export Data

- **Single Player Card**: Click export button on player details
- **Comparison Card**: Export multi-player comparison as PDF
- **CSV Data**: Download raw statistics from API endpoints

### Advanced Visualization Modes

Switch between four dashboard modes using the new heat-card toggle:

1. **Standard View** – Existing ECharts + Chart.js visualizations
2. **Temporal Load** – Plotly animated scatter of every possession with estimated shot-clock phase, highlighting late-clock fatigue
3. **Shot Clock Pressure** – Gradient heatmap of quarter vs. phase showing cognitive drop-offs during crunch time
4. **Team Insights War Room** – Radar chart (Heat vs opponent pressure), lineup synergy heatmap, and DM Catch → Driving → Finishing EPA waterfall with coach takeaways

All modes auto-refresh when new CSVs are imported (via the `newGameUploaded` cross-tab event).

---

## 📊 Performance Categories

| Category | Description | Positive Indicators | Negative Indicators |
|----------|-------------|-------------------|-------------------|
| **Space Read** | Reading defensive spacing | Live Dribble, Catch | Poor reads |
| **DM Catch** | Decision-making on catches | Swing, Drive Pass, Uncontested Shot | Poor decisions |
| **Finishing** | Shot completion | Stride Pivot, Earn Foul, Ball Security | Missed opportunities |
| **Footwork** | Footwork technique | Step to Ball, Patient Pickup | Poor positioning |
| **Passing** | Passing decisions | Teammate on Move, Read Length | Turnovers |
| **Positioning** | Off-ball positioning | Create Shape, Advantage Awareness | Poor spacing |
| **QB12 DM** | Decision-making | Strong Side, Roller, Cutter | Hesitation |
| **Relocation** | Off-ball movement | Weak Corner, Fill Behind, 45 Cut | Static movement |
| **Cutting & Screening** | Screening actions | Denial, Movement, Body to Body | Ineffective screens |
| **Transition** | Transition play | Effort and Pace | Poor execution |

---

## 🗄️ Database Schema

### Tables

**games**
- `id` (TEXT, PRIMARY KEY): Unique 16-char game ID
- `date` (INTEGER): Unix timestamp
- `date_string` (TEXT): MM.DD.YY format
- `team` (TEXT): Team name
- `opponent` (TEXT): Opponent name
- `created_at` (INTEGER): Creation timestamp

**players**
- `name` (TEXT, PRIMARY KEY): Player name
- `date_created` (INTEGER): Creation timestamp

**scorecards** (78 statistical fields)
- `id` (INTEGER, PRIMARY KEY)
- `player_name` (TEXT, FOREIGN KEY)
- `game_id` (TEXT, FOREIGN KEY)
- `[category]_[subcategory]_positive` (INTEGER): Positive count
- `[category]_[subcategory]_negative` (INTEGER): Negative count
- Example: `footwork_step_to_ball_positive`, `passing_teammate_on_move_negative`

**team_cog_scores**
- `game_date` (INTEGER): Game timestamp
- `team` (TEXT)
- `opponent` (TEXT)
- `score` (REAL): Overall cognitive score
- UNIQUE constraint on (game_date, team, opponent)

**team_statistics** (one record per game-category combination)
- `game_date_iso` (TEXT): YYYY-MM-DD format
- `date_string` (TEXT): MM.DD.YY format
- `team` (TEXT)
- `opponent` (TEXT)
- `category` (TEXT): One of 10 categories
- `percentage` (REAL): Category percentage
- `positive_count` (INTEGER)
- `negative_count` (INTEGER)
- `overall_score` (REAL)

**possession_events**
- `game_id` (TEXT, FK): Linked to `games`
- `timestamp` (REAL): Seconds from game start (from CSV Start time)
- `duration` (REAL): Possession duration / action time
- `shot_clock_phase` (TEXT): Early/Middle/Late/Unknown
- `cognitive_score` (REAL): Per-possession signal strength
- `positive_count` / `negative_count`
- `shot_outcome`, `shot_location`, `quarter`, `opponent`

---

## 🔧 API Endpoints

### Analytics Data
```
GET /api/team-statistics-with-games
  Response: All games with statistics for dashboard
  
GET /api/team-statistics-overall-scores
  Response: Overall scores for each game
  
GET /api/team-statistics-game-info
  Response: Game metadata (dates, opponents)
```

### CSV Upload
```
POST /api/database-viz/upload-mega-csv
  Body: multipart/form-data with CSV file
  Response: {
    "success": true,
    "game_id": "f90720964031c6ba",
    "date": "10.28.25",
    "opponent": "CHA",
    "team_cog_score": 77.95
  }
```

### Player Management
```
GET /api/database-viz/players/<game_id>
  Response: All players for a specific game
  
POST /api/database-viz/export/player-card/<game_id>/<player_name>
  Response: PDF file download
  
POST /api/database-viz/export/comparison-card
  Body: { "players": [...] }
  Response: PDF comparison card
```

---

## 🧪 Testing

### Run Test Suite
```bash
# Unit tests
python -m pytest tests/

# Specific test file
python tests/test_csv_pipeline.py

# With coverage
python -m pytest --cov=src tests/
```

### Test Data
Sample CSV files are provided in `testcases/test_csvs/`:
- `10.04.25 Heat v Magic(team).csv`
- `10.28.25 MIA v CHA-Table 1.csv`
- `11.2.25 MIA v LAL-Table 1.csv`

---

## 🐛 Troubleshooting

### Common Issues

**1. "CSV file missing 'Row' column"**
- Ensure CSV has proper header with "Row" column
- Check for "Table 1" prefix (will be auto-skipped)

**2. "Duplicate game" error**
- Only ONE game per team per date allowed
- Delete existing game or use different date

**3. "No data in analytics dashboard"**
- Verify CSV was processed successfully
- Check database: `src/core/data/basketball.db`
- Hard refresh browser (Ctrl+Shift+R)

**4. "Toggle buttons not working"**
- Click "Reset Toggles" button in dashboard
- Watchdog timer auto-resets every 60 seconds

**5. "Missing Footwork/Passing statistics"**
- Ensure CSV has "Footwork" and "Passing" columns
- Reprocess CSV if columns were added later

### Debug Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python main.py
```

---

## 📈 Performance

- **Single CSV Processing**: 2-5 seconds
- **Batch Processing (9 CSVs)**: 20-30 seconds
- **Database Size**: ~100KB per game with full statistics
- **Dashboard Load**: <1 second for 50 games

---

## 🔒 Data Privacy

- All data stored locally in SQLite database
- No external API calls for game data
- PDF exports contain only selected data
- No telemetry or usage tracking

---

## 🛠️ Development

### Adding New Categories

1. **Update Scorecard Model** (`src/models/scorecard.py`)
   - Add new fields to `__init__`
   - Add to instance assignments
   - Add to `to_dict()` method

2. **Update Database Schema** (`src/database/db_manager.py`)
   - Add columns to `scorecards` table creation

3. **Update Statistics Calculator** (`src/utils/statistics_calculator.py`)
   - Add category to `CATEGORIES` dict with field mappings

4. **Update CSV Importer** (`src/processors/csv_to_database_importer.py`)
   - Add column mappings in `_create_scorecard_from_row`

5. **Reprocess Existing Games**
   - Run migration script or delete and reimport

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function signatures
- Document complex algorithms
- Add unit tests for new features

---

## 📝 Version History

### Version 2.0 (Current)
- ✅ Added Footwork, Passing, and Finishing categories
- ✅ Implemented player comparison feature
- ✅ Added PDF export functionality
- ✅ Fixed duplicate data points issue
- ✅ Added UNIQUE constraints to prevent duplicates
- ✅ Implemented toggle watchdog for chart reliability

### Version 1.0
- Initial release with 7 categories
- Basic analytics dashboard
- CSV import functionality
- Team cognitive score calculation

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📞 Support

For detailed technical questions about CSV processing:
- See [CSV_PROCESSING_ALGORITHM.md](CSV_PROCESSING_ALGORITHM.md)

For issues and bug reports:
- Check troubleshooting section above
- Review error logs in terminal
- Create detailed issue report

---

**Built with ❤️ for basketball analytics**

*Last Updated: November 2025*
