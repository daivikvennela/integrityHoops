# SmartDash Tally Table Feature

## Overview

The SmartDash tally table provides a comprehensive breakdown of all performance actions across basketball cognitive performance data. It creates a single, flattened table that shows every unique action, its frequency, percentage, and classification.

## Features

### 1. Flattened Tally Table
- **Column**: Shows which performance category the action belongs to
- **Action**: The specific action performed (e.g., "+ve Space Read: Catch")
- **Count**: Number of times this action occurred
- **Percentage**: Percentage of total rows this action represents
- **Type**: Classification as Positive, Negative, or Neutral

### 2. Automatic Classification
- **Positive**: Actions containing "+ve" in the description
- **Negative**: Actions containing "-ve" in the description  
- **Neutral**: All other actions

### 3. Smart Sorting
- Sorted by column name (alphabetical)
- Within each column, sorted by count (descending)

## Implementation Details

### Method: `create_flattened_tally_table(df)`

Located in `basketball_cognitive_processor.py`, this method:

```python
def create_flattened_tally_table(self, df):
    """
    Create a single tally table for all performance columns, with the column name included.
    """
    try:
        all_tallies = []
        performance_columns = list(self.performance_categories.values())
        for category in performance_columns:
            if category in df.columns:
                value_counts = df[category].value_counts()
                for action, count in value_counts.items():
                    all_tallies.append({
                        'Column': category,
                        'Action': action,
                        'Count': count,
                        'Percentage': round((count / len(df)) * 100, 2),
                        'Type': 'Positive' if '+ve' in str(action) else 'Negative' if '-ve' in str(action) else 'Neutral'
                    })
        # Create a DataFrame for easy display
        tally_df = pd.DataFrame(all_tallies)
        tally_df = tally_df.sort_values(['Column', 'Count'], ascending=[True, False])
        return tally_df
    except Exception as e:
        logger.error(f"Error creating flattened tally table: {e}")
        return pd.DataFrame()
```

### Integration Points

#### 1. Flask Route (`app.py`)
```python
@app.route('/smartdash/<filename>')
def smartdash_with_data(filename):
    # ... existing code ...
    
    # Get the flattened tally table
    flattened_tally = processor.create_flattened_tally_table(df)
    
    return render_template('smartdash.html', 
                         filename=filename,
                         original_filename=original_filename,
                         smart_metrics=smart_metrics,
                         flattened_tally=flattened_tally,
                         df=df)
```

#### 2. Template Display (`smartdash.html`)
```html
<!-- Performance Tally Table -->
{% if flattened_tally is not none and not flattened_tally.empty %}
<div class="row mb-4">
    <div class="col-12">
        <div class="dashboard-card">
            <div class="p-4">
                <h5 class="mb-3">
                    <i class="fas fa-list me-2"></i>
                    Performance Action Tally
                </h5>
                <div class="table-responsive">
                    <table class="table table-striped table-hover">
                        <thead class="table-dark">
                            <tr>
                                <th>Column</th>
                                <th>Action</th>
                                <th>Count</th>
                                <th>Percentage</th>
                                <th>Type</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for _, row in flattened_tally.iterrows() %}
                            <tr>
                                <td>{{ row.Column }}</td>
                                <td>{{ row.Action }}</td>
                                <td>{{ row.Count }}</td>
                                <td>{{ row.Percentage }}%</td>
                                <td>
                                    <span class="badge 
                                        {% if row.Type == 'Positive' %}bg-success
                                        {% elif row.Type == 'Negative' %}bg-danger
                                        {% else %}bg-secondary{% endif %}">
                                        {{ row.Type }}
                                    </span>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endif %}
```

## Usage

### For Users
1. Upload basketball cognitive performance data
2. Navigate to SmartDash dashboard
3. View the "Performance Action Tally" section
4. Analyze action frequencies and patterns

### For Developers
```python
from basketball_cognitive_processor import BasketballCognitiveProcessor

# Initialize processor
processor = BasketballCognitiveProcessor()

# Load your data
df = pd.read_csv('your_data.csv')

# Generate tally table
tally_df = processor.create_flattened_tally_table(df)

# Use the tally data
print(tally_df)
```

## Performance Categories Analyzed

The tally table processes these performance categories:
- Space Read
- DM Catch
- Driving
- QB12 DM
- Finishing
- Footwork
- Passing
- Positioning
- Relocation
- Cutting & Screening
- Transition

## Example Output

```
        Column                          Action  Count  Percentage      Type
0   Space Read           +ve Space Read: Catch      2        50.0  Positive
1   Space Read           -ve Space Read: Catch      1        25.0  Negative
2   Space Read    +ve Space Read: Live Dribble      1        25.0  Positive
3     DM Catch             +ve DM Catch: Drive      1        25.0  Positive
4     DM Catch             -ve DM Catch: Swing      1        25.0  Negative
...
```

## Benefits

1. **Comprehensive View**: All actions in one table
2. **Pattern Recognition**: Easy to spot common actions
3. **Performance Analysis**: Clear positive/negative breakdown
4. **Data-Driven Insights**: Quantified action frequencies
5. **User-Friendly**: Clean, sortable table interface

## Error Handling

- Graceful handling of missing columns
- Logging of errors for debugging
- Returns empty DataFrame on failure
- Safe string operations for type classification

## Future Enhancements

Potential improvements:
- Filtering by action type
- Export functionality
- Interactive sorting
- Drill-down capabilities
- Performance trend analysis 