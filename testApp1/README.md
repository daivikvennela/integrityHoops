# 🏀 Basketball Cognitive Performance Dashboard

A comprehensive web application for managing basketball players, scorecards, and cognitive performance data with advanced analytics and real-time monitoring.

## 📁 Project Structure

```
testApp1/
├── 📁 src/                          # Source code
│   ├── 📁 core/                     # Core application files
│   │   ├── app.py                   # Main Flask application
│   │   └── run.py                   # Application startup script
│   ├── 📁 api/                      # API endpoints
│   │   ├── player_api.py            # Basic player CRUD operations
│   │   └── player_management_dashboard.py  # Advanced dashboard API
│   ├── 📁 models/                   # Data models
│   │   ├── player.py                # Player model
│   │   ├── scorecard.py             # Scorecard model
│   │   └── __init__.py              # Model package initialization
│   ├── 📁 database/                 # Database management
│   │   ├── db_manager.py            # Database operations
│   │   └── __init__.py              # Database package initialization
│   ├── 📁 processors/               # Data processing modules
│   │   ├── basketball_cognitive_processor.py  # Cognitive data processing
│   │   ├── custom_etl_processor.py  # ETL processing
│   │   └── etl_scripts.py           # ETL utilities
│   └── 📁 utils/                    # Utility functions
├── 📁 templates/                    # HTML templates
│   ├── base.html                    # Base template
│   ├── index.html                   # Upload page
│   ├── players.html                 # Basic player management
│   ├── player_management_dashboard.html  # Advanced dashboard
│   ├── scorecard.html               # Scorecard view
│   ├── scorecard_plus.html          # Enhanced scorecard
│   ├── smartdash.html               # Smart dashboard
│   └── results.html                 # Results display
├── 📁 static/                       # Static assets
│   ├── 📁 css/                      # Stylesheets
│   ├── 📁 js/                       # JavaScript files
│   └── 📁 images/                   # Images and icons
├── 📁 data/                         # Data storage
│   ├── 📁 uploads/                  # Uploaded files
│   ├── 📁 processed/                # Processed data files
│   ├── 📁 exports/                  # Exported data
│   ├── basketball.db                # Main database
│   └── test_basketball.db           # Test database
├── 📁 docs/                         # Documentation
│   ├── 📁 guides/                   # User and developer guides
│   ├── �� api/                      # API documentation
│   └── 📁 deployment/               # Deployment guides
├── 📁 tests/                        # Test files
│   └── test_models.py               # Model testing
├── 📁 config/                       # Configuration files
│   └── requirements.txt             # Python dependencies
├── main.py                          # Application entry point
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (recommended)
- pip3

### Installation
1. **Clone the repository**
   ```bash
   cd testApp1
   ```

2. **Create virtual environment**
   ```bash
   python3.12 -m venv venv312
   source venv312/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip3 install -r config/requirements.txt
   ```

4. **Run the application**
   ```bash
   python3 main.py
   ```

5. **Access the application**
   - Main Dashboard: http://localhost:5001
   - Player Management: http://localhost:5001/player-management
   - Basic Players: http://localhost:5001/players

## 🎯 Features

### 📊 **Advanced Player Management Dashboard**
- Real-time statistics and analytics
- Interactive charts and visualizations
- Custom scorecard creation system
- API monitoring terminal
- Bulk operations and data export

### 🔧 **Core Functionality**
- File upload and processing (CSV, Excel)
- ETL data transformation
- Basketball cognitive performance analysis
- Player and scorecard management
- Smart dashboard with metrics

### 🎨 **Modern UI**
- Responsive Bootstrap 5 design
- Real-time updates and notifications
- Interactive data tables
- Modal dialogs and forms
- Chart.js visualizations

## 📚 Documentation

### **User Guides**
- `docs/guides/README.md` - Main application guide
- `docs/guides/PLAYER_MANAGEMENT_GUIDE.md` - Player management system
- `docs/guides/ADVANCED_PLAYER_MANAGEMENT_GUIDE.md` - Advanced dashboard guide
- `docs/guides/UPLOAD_GUIDE.md` - File upload instructions
- `docs/guides/BASKETBALL_COGNITIVE_GUIDE.md` - Cognitive processing guide

### **API Documentation**
- REST API endpoints for player management
- Custom scorecard creation
- Bulk operations
- Data export functionality

## 🧪 Testing

Run the test suite:
```bash
python3 tests/test_models.py
```

## 🔧 Development

### **Project Structure Benefits**
- **Modular Design**: Clear separation of concerns
- **Scalability**: Easy to add new features
- **Maintainability**: Organized code structure
- **Testing**: Dedicated test directory
- **Documentation**: Comprehensive guides

### **Key Components**
- **Core**: Main application logic and routing
- **API**: REST endpoints and API management
- **Models**: Data models and business logic
- **Database**: Database operations and management
- **Processors**: Data processing and ETL operations
- **Templates**: HTML templates and UI components

## 📊 Data Management

### **Database**
- SQLite database (`data/basketball.db`)
- Player and scorecard tables
- Foreign key relationships
- Automatic table creation

### **File Processing**
- Upload directory: `data/uploads/`
- Processed files: `data/processed/`
- Export directory: `data/exports/`

## 🚀 Deployment

### **Development**
```bash
python3 main.py
```

### **Production**
```bash
gunicorn -w 4 -b 0.0.0.0:5001 src.core.app:app
```

## 🔧 Configuration

### **Environment Variables**
- `FLASK_ENV`: Development/production mode
- `FLASK_DEBUG`: Debug mode (1/0)
- `UPLOAD_FOLDER`: Upload directory path
- `PROCESSED_FOLDER`: Processed files directory

### **Database Configuration**
- Database path: `data/basketball.db`
- Test database: `data/test_basketball.db`
- Auto-creation of tables and directories

## 📈 Performance

### **Optimizations**
- Database indexing for fast queries
- Lazy loading of data
- Client-side caching
- Efficient ETL processing
- Real-time API monitoring

### **Monitoring**
- API call logging and monitoring
- Performance metrics tracking
- Error handling and reporting
- Real-time dashboard updates

## 🤝 Contributing

1. Follow the established project structure
2. Add tests for new features
3. Update documentation
4. Follow Python coding standards
5. Use meaningful commit messages

## 📄 License

This project is open source and available under the MIT License.

---

**Built with ❤️ using Flask, Bootstrap, Chart.js, and modern web technologies**
