# 🏀 IntegrityHoops - Basketball Cognitive Performance Dashboard

An advanced basketball analytics platform for tracking and analyzing player cognitive performance, featuring real-time data processing, interactive dashboards, and comprehensive player scorecards.

## 🚀 Quick Start Guide for Cursor

### Prerequisites
- Python 3.12 (recommended) or Python 3.8+ (minimum)
- Git
- macOS, Linux, or Windows

### 📋 Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd IntegrityHoops
```

#### 2. Navigate to Application Directory
```bash
cd testApp1
```

#### 3. Set Up Python Virtual Environment

**For Python 3.12 (Recommended):**
```bash
python3.12 -m venv venv312
source venv312/bin/activate  # On Windows: venv312\Scripts\activate
```

**For Python 3.13+ (Alternative):**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 4. Install Dependencies
```bash
pip install -r config/requirements.txt
```

#### 5. Test Database Connection
```bash
python test_db_connection.py
```

#### 6. Start the Application
```bash
python run_app.py
```

#### 7. Access the Application
Open your web browser and navigate to: **http://localhost:8000**

## 🌟 Features Overview

### 📊 Main Dashboards

1. **Homepage** (`/`) 
   - File upload and basic ETL processing
   - General data transformation tools

2. **SmartDash** (`/smartdash`)
   - Basketball cognitive performance metrics
   - Advanced analytics visualization
   - Player performance insights

3. **ScoreCard** (`/scorecard`)
   - Individual player performance scoring
   - Cognitive assessment tracking

4. **ScoreCard Plus** (`/scorecard-plus`)
   - Comprehensive performance analysis
   - Detailed metrics breakdown

5. **Player Management** (`/players`, `/player-management`)
   - Player database management
   - Historical performance tracking

### 🔧 Key Capabilities

- **File Upload**: CSV/Excel basketball performance data
- **ETL Processing**: Specialized basketball cognitive data transformation
- **Real-time Analytics**: Live performance metrics calculation
- **Database Integration**: SQLite for persistent data storage
- **Interactive UI**: Modern, responsive web interface with white text theme

## 📁 Project Structure

```
IntegrityHoops/
├── testApp1/                          # Main application directory
│   ├── src/                          # Source code
│   │   ├── core/                     # Core application logic
│   │   │   ├── app.py               # Main Flask application
│   │   │   ├── dashboard.py         # Dashboard blueprints
│   │   │   └── run.py               # Application runner
│   │   ├── api/                     # API endpoints
│   │   ├── database/                # Database management
│   │   ├── models/                  # Data models
│   │   ├── processors/              # Data processing modules
│   │   └── utils/                   # Utility functions
│   ├── templates/                   # HTML templates
│   ├── data/                        # Data storage
│   │   ├── uploads/                 # Uploaded files
│   │   └── processed/               # Processed data
│   ├── config/                      # Configuration files
│   ├── docs/                        # Documentation
│   ├── tests/                       # Test files
│   ├── main.py                      # Alternative entry point
│   ├── run_app.py                   # Primary entry point
│   └── test_db_connection.py        # Database test utility
└── README.md                        # This file
```

## 🛟 Troubleshooting

### Common Issues

#### Port Already in Use
If you get a port error:
```bash
# Kill any processes using port 8000
lsof -ti:8000 | xargs kill -9
# Or use a different port by modifying run_app.py
```

#### Python Version Issues
- **Recommended**: Use Python 3.12 for best compatibility
- **Python 3.13**: May have pandas compatibility issues
- **Solution**: Install Python 3.12 and use `venv312`

#### Virtual Environment Activation
Make sure to activate the virtual environment before running:
```bash
source venv312/bin/activate  # macOS/Linux
# or
venv312\Scripts\activate     # Windows
```

#### Database Issues
If you encounter database errors:
```bash
# Test database connectivity
python test_db_connection.py

# Check if database file exists
ls -la *.db data/*.db
```

### Verification Steps

1. **Check Python Version**: `python --version` (should show 3.12.x in venv312)
2. **Check Dependencies**: `pip list | grep Flask` (should show Flask 3.0.0)
3. **Test Database**: `python test_db_connection.py` (should show existing players)
4. **Check Application**: `curl http://localhost:8000` (should return HTML)

## 🔄 Development Workflow

### Making Changes
1. **Create a new branch**: `git checkout -b feature-name`
2. **Make your changes**
3. **Test the application**: `python run_app.py`
4. **Commit changes**: `git add . && git commit -m "Description"`
5. **Push to GitHub**: `git push origin feature-name`

### File Upload Testing
1. Navigate to SmartDash (`/smartdash`)
2. Upload a CSV file with basketball performance data
3. Select processing options
4. View results in the dashboard

## 📊 Data Format

### Expected CSV Structure
The application processes basketball cognitive performance data with columns like:
- `PLAYER`: Player name
- Various cognitive metrics (space reading, decision making, etc.)
- Performance indicators (positive/negative outcomes)

### Sample Data
Check the `data/uploads/` directory for example CSV files.

## 🎨 UI Customization

The application features a modern dark theme with white text. Key styling is in:
- `templates/base.html`: Global styles
- `templates/scorecard.html`: ScoreCard specific styles
- `templates/scorecard_plus.html`: ScoreCard Plus styles

## 📱 Browser Compatibility

Tested and optimized for:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🔐 Security Notes

- Application runs in development mode by default
- Database is SQLite (local file)
- File uploads are validated and secured
- For production deployment, use a proper WSGI server

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request with clear description

## 📞 Support

If you encounter issues:

1. **Check this README** for troubleshooting steps
2. **Verify prerequisites** are correctly installed
3. **Test database connectivity** using the test script
4. **Check application logs** in the terminal

## 🏷️ Version History

- **Current**: Basketball cognitive performance analytics
- **Features**: File upload, ETL processing, multiple dashboards
- **Database**: SQLite with player and scorecard management

---

**🎯 Ready to analyze basketball performance data!** 

Start by uploading your CSV files through the SmartDash interface and explore the comprehensive analytics dashboard.
