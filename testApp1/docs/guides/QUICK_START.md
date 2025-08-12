# Quick Start Guide

## 🚀 Get Started in 3 Steps

### 1. Activate Virtual Environment
```bash
cd testApp1
source venv/bin/activate
```

### 2. Run the Application
```bash
python run.py
```

### 3. Open Your Browser
Go to: **http://localhost:5000**

## 📁 What You'll Find

### Sample Data
- `sample_companies.csv` - Ready-to-use test data with 10 companies

### Key Features to Try
1. **Upload the sample CSV** - Drag and drop `sample_companies.csv`
2. **Enable "Scrape Additional Data"** - See enriched company information
3. **Try all processing options** - Remove duplicates, fill missing values, add timestamps
4. **Explore the results table** - Search, sort, and export data

## 🎯 Demo Workflow

1. **Upload**: Select `sample_companies.csv`
2. **Process**: Check all processing options
3. **View**: See the enriched data with additional columns
4. **Export**: Download the processed file

## 🔧 Troubleshooting

### If the app doesn't start:
```bash
# Check if port 5000 is available
lsof -i :5000

# Kill any existing process
kill -9 <PID>

# Restart the app
python run.py
```

### If you get import errors:
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

## 📊 Expected Results

After processing `sample_companies.csv` with all options enabled, you'll see:
- Original 5 columns: Company_Name, Contact_Email, Phone_Number, Revenue, Employees
- Additional 7 columns: website, industry, employee_count, revenue_range, location, founded_year, description
- Plus: processed_timestamp

## 🎉 You're Ready!

The application is now running and ready to process your CSV files with powerful ETL capabilities! 