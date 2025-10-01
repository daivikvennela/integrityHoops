# 🏀 IntegrityHoops - Basketball Analytics Dashboard

Basketball cognitive performance tracking and analytics platform.

## Quick Setup for Cursor

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd IntegrityHoops/testApp1
```

### 2. Create Virtual Environment
```bash
python3.12 -m venv venv312
source venv312/bin/activate  # Windows: venv312\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r config/requirements.txt
```

### 4. Run Application
```bash
python run_app.py
```

### 5. Open Browser
Navigate to: **http://localhost:8000**

## Key Routes

- `/` - Homepage (file upload)
- `/smartdash` - Main analytics dashboard
- `/scorecard` - Player scorecards
- `/players` - Player management

## Troubleshooting

**Port in use?**
```bash
lsof -ti:8000 | xargs kill -9
```

**Wrong Python version?**
Use Python 3.12 (recommended). Python 3.13 may have pandas issues.

**Database errors?**
```bash
python test_db_connection.py
```

## Project Structure

```
testApp1/
├── src/              # Source code
├── templates/        # HTML templates  
├── data/            # Data storage
├── config/          # Configuration
└── run_app.py       # Entry point
```

## Tech Stack

- **Backend**: Flask 3.0.0
- **Data**: pandas 2.3.1
- **Database**: SQLite
- **UI**: Bootstrap 5, white text theme

---

**Ready to go!** Upload CSV files via SmartDash to analyze basketball performance data.