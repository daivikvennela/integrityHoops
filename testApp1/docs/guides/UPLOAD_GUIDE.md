# 📊 CSV Upload & Customization Guide

## 🎯 How to Upload Your CSV File

### Step 1: Access the Application
1. Open your browser and go to: **http://localhost:5001**
2. You'll see the modern upload interface

### Step 2: Upload Your CSV File
1. **Drag and drop** your CSV file onto the upload area, OR
2. **Click "Browse"** to select your file
3. Supported formats: `.csv`, `.xlsx`, `.xls`

### Step 3: Configure Processing Options
The application will automatically detect your data type and apply specialized processing:

#### 🔍 **Automatic Data Type Detection**
- **Basketball Stats**: Detects columns like Points, Rebounds, Assists, etc.
- **Financial Data**: Detects Revenue, Profit, Sales, etc.
- **Sports Analytics**: Detects Wins, Losses, Records, etc.
- **Performance Metrics**: Detects Scores, Ratings, Efficiency, etc.
- **Survey Data**: Detects Responses, Ratings, Feedback, etc.
- **Time Series**: Detects Date, Time, Period columns

#### ⚙️ **Processing Options**
- ✅ **Remove Duplicates**: Eliminates duplicate rows
- ✅ **Fill Missing Values**: Replaces empty cells with 'N/A'
- ✅ **Add Timestamp**: Adds processing timestamp
- ✅ **Scrape Additional Data**: Enriches data with additional information

### Step 4: Process Your Data
1. Click **"Process Data"**
2. Wait for processing to complete
3. View results in the interactive table

## 🏀 **Basketball Statistics Processing**

If your CSV contains basketball stats, the system will automatically calculate:

### **Advanced Metrics**
- **Points Per Game**: Total points ÷ Games played
- **Field Goal Percentage**: (FG Made ÷ FG Attempted) × 100
- **3-Point Percentage**: (3P Made ÷ 3P Attempted) × 100
- **Free Throw Percentage**: (FT Made ÷ FT Attempted) × 100
- **Total Impact**: Points + Rebounds + Assists + Steals + Blocks

### **Performance Categories**
- **Scoring Category**: Low/Average/High/Elite Scorer
- **Efficiency Ratings**: Based on shooting percentages

## 💰 **Financial Data Processing**

For financial data, the system calculates:

### **Growth Metrics**
- **Revenue Growth Rate**: Percentage change in revenue
- **Sales Growth Rate**: Percentage change in sales
- **Profit Margin**: (Revenue - Expenses) ÷ Revenue × 100

### **Financial Health Indicators**
- **Revenue Categories**: Low/Medium/High/Very High Revenue
- **Trend Analysis**: Moving averages and growth patterns

## 📈 **Sports Analytics Processing**

For sports team data:

### **Performance Metrics**
- **Win Percentage**: Wins ÷ (Wins + Losses) × 100
- **Point Differential**: Points For - Points Against
- **Performance Tiers**: Poor/Below Average/Above Average/Excellent

## 📊 **Performance Metrics Processing**

For performance data:

### **Normalized Scores**
- **0-100 Scale**: All scores normalized to 0-100 range
- **Composite Scores**: Average of multiple performance metrics
- **Trend Analysis**: Performance changes over time

## 🔍 **Survey Data Processing**

For survey responses:

### **Response Analysis**
- **Response Rates**: Percentage of completed surveys
- **Average Ratings**: Mean of all rating questions
- **Sentiment Analysis**: Comment length and presence analysis

## 📅 **Time Series Data Processing**

For time-based data:

### **Trend Analysis**
- **Moving Averages**: 3-period rolling averages
- **Trend Calculations**: Period-over-period changes
- **Date Standardization**: Consistent date formatting

## 🎯 **Customizing for Your Specific Data**

### **To Customize Processing:**

1. **Upload your CSV file** first
2. **Note the detected data type** in the results
3. **Tell me what columns** are in your data
4. **Describe what processing** you want

### **Example Customization Requests:**

```
"My CSV has basketball stats with columns:
- Player Name
- Team
- Games Played
- Points
- Rebounds
- Assists

I want to calculate:
- Points per game
- Total impact score
- Performance rating"
```

## 📋 **Expected Results**

After processing, you'll see:

### **Enhanced Data Table**
- Original columns + calculated metrics
- Performance categories and ratings
- Data quality indicators

### **Summary Statistics**
- Data completeness percentage
- Missing value analysis
- Statistical summaries for numeric columns

### **Export Options**
- Download as CSV
- Download as JSON
- Interactive table with search/sort

## 🚀 **Ready to Upload?**

1. **Prepare your CSV file** with your stats data
2. **Go to http://localhost:5001**
3. **Upload and process** your data
4. **Share the results** with me for further customization

The application is now ready to handle your specific statistical data with intelligent processing and beautiful visualization! 