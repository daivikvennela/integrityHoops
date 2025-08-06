# Scorecard Attributes & Autofill Functionality

## 🏀 New Scorecard Attributes

The scorecard model has been enhanced with new Space Read metrics for basketball performance analysis.

### **New Attributes Added:**

1. **`space_read_live_dribble`** (int)
   - Count of positive space read live dribble actions
   - Auto-calculated from "+ve Space Read: Live Dribble" entries in column 58
   - Default value: 0

2. **`space_read_catch`** (int)
   - Count of positive space read catch actions
   - Auto-calculated from "+ve Space Read: Catch" entries in column 58
   - Default value: 0

### **Database Schema Updates:**

The `scorecards` table now includes:
```sql
CREATE TABLE scorecards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    date_created INTEGER NOT NULL,
    space_read_live_dribble INTEGER DEFAULT 0,
    space_read_catch INTEGER DEFAULT 0,
    FOREIGN KEY (player_name) REFERENCES players (name)
);
```

## 🔄 Autofill Functionality

### **How It Works:**

1. **Data Parsing**: The system automatically scans the "Space Read" column (column 58) in uploaded basketball data
2. **Pattern Matching**: Looks for specific patterns:
   - `"+ve Space Read: Live Dribble"` → increments `space_read_live_dribble`
   - `"+ve Space Read: Catch"` → increments `space_read_catch`
3. **Auto-Calculation**: Counts occurrences and populates form fields automatically

### **User Interface:**

- **Autofill Buttons**: Next to each Space Read field
- **Real-time Calculation**: Processes current data table
- **Visual Feedback**: Shows counts and success messages
- **Manual Override**: Users can still manually edit values

### **Technical Implementation:**

#### **ScorecardAutofillProcessor Class:**
- `calculate_space_read_metrics()`: Core calculation logic
- `autofill_scorecard_attributes()`: Main autofill function
- `validate_data_for_autofill()`: Data validation

#### **JavaScript Autofill Function:**
- `autofillSpaceRead()`: Client-side autofill
- Column detection and pattern matching
- Form field updates

## 📊 Usage Examples

### **Creating a Scorecard with Autofill:**

1. **Upload basketball data** → Process & Analyze
2. **Select player** from dropdown
3. **Click "Autofill"** buttons next to Space Read fields
4. **Review calculated values** (can be manually adjusted)
5. **Click "Create Scorecard"** → Saves with calculated metrics

### **Manual Entry:**

Users can also manually enter values:
- Type directly into number fields
- Values are validated (minimum 0)
- Form submission includes all attributes

## 🔧 API Endpoints

### **Create Scorecard:**
```
POST /create-scorecard
{
    "player_name": "Player Name",
    "space_read_live_dribble": 5,
    "space_read_catch": 3
}
```

### **Autofill Scorecard:**
```
POST /autofill-scorecard
{
    "file": "basketball_data.csv"
}
```

## 🎯 Benefits

1. **Automated Analysis**: Reduces manual counting errors
2. **Consistent Metrics**: Standardized calculation across all scorecards
3. **Time Savings**: Instant calculation from uploaded data
4. **Flexibility**: Manual override capability for edge cases
5. **Data Integrity**: Validated input and database constraints

## 🚀 Future Enhancements

- Additional Space Read metrics
- More complex pattern matching
- Batch processing for multiple files
- Export functionality for calculated metrics
- Historical trend analysis 