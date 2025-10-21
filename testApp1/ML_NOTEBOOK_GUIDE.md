# ML Notebook - User Guide

## Overview

The ML Notebook is a powerful, integrated Jupyter-style notebook interface built directly into IntegrityHoops. It allows you to perform advanced machine learning and data analysis directly in your browser, with full support for Python, pandas, scikit-learn, and visualization libraries.

## Key Features

✨ **Real-Time Code Execution**: Run Python code cells and see results immediately
📊 **CSV Integration**: Upload and work with your basketball data seamlessly  
📈 **Visualization Support**: Create matplotlib and seaborn plots inline
🤖 **ML Models**: Build and evaluate linear regression and other ML models
💾 **Auto-Save**: Your work is automatically saved every 30 seconds
📝 **Templates**: Pre-built templates for common analysis tasks
⚡ **M4 Optimized**: Leverages your M4 chip for fast execution

## Getting Started

### 1. Access the ML Notebook

Navigate to the ML Notebook from:
- Homepage → "ML Notebook" quick access card
- Main navigation → ML Notebook
- Direct URL: `http://localhost:8081/ml-notebook`

### 2. Interface Overview

The ML Notebook interface consists of two main tabs:

#### **Code Editor Tab**
- Write and edit Python code
- Add/delete cells
- Run individual cells or all cells at once
- Cell execution counter shows order of execution

#### **Output Viewer Tab**
- View all outputs from executed cells
- Text output, errors, tables, and plots
- Clear output when needed
- Automatic scrolling to latest output

### 3. Working with CSV Files

#### Option A: Load Existing CSV
1. Select a CSV file from the dropdown
2. Click "Load CSV"
3. A new cell will be created with the loading code
4. The cell auto-executes and loads data into variable `df`

#### Option B: Upload New CSV
1. Click "Upload CSV" button
2. Select your CSV file
3. File is uploaded and automatically loaded
4. Data is available as `df` in the notebook

#### CSV Data Access
```python
# Your CSV is automatically loaded as:
df = pd.read_csv('your_file.csv')

# You can immediately start working with it:
print(df.shape)
df.head()
df.describe()
```

### 4. Using Templates

The ML Notebook includes three pre-built templates:

#### **Linear Regression Template**
Perfect for predictive modeling:
```python
# After loading template:
# 1. Update target and feature columns
target_column = 'points_scored'  # Your target
feature_columns = ['assists', 'rebounds', 'minutes']  # Your features

# 2. Run all cells to:
# - Train the model
# - Get performance metrics
# - See visualizations
```

**Outputs**:
- Model coefficients and intercept
- R² Score, RMSE, MAE metrics
- Actual vs Predicted scatter plot
- Residual plot
- Feature importance chart

#### **Data Exploration Template**
Comprehensive EDA:
- Dataset overview (shape, columns, dtypes)
- Statistical summaries
- Missing value analysis
- Correlation heatmap
- Distribution plots
- Outlier detection

#### **Blank Template**
Start fresh with common imports already loaded.

### 5. Running Code

#### Run Single Cell
- Click the ▶️ play button in the cell toolbar
- Or press **Shift+Enter** while focused on the cell

#### Run All Cells
- Click "Run All" button in the editor controls
- Cells execute sequentially from top to bottom

#### Cell Execution Status
- **Running**: Yellow border with spinner
- **Success**: Green checkmark (✓)
- **Error**: Red X with error message
- Execution counter `[n]` shows run order

### 6. Managing Cells

#### Add New Cell
- Click "+ Add Cell" button
- New cell appears at the bottom
- Start typing Python code immediately

#### Delete Cell
- Click the 🗑️ trash icon in cell toolbar
- Cell is permanently removed

#### Edit Cell
- Click inside the cell to activate CodeMirror editor
- Syntax highlighting for Python
- Auto-completion and bracket matching
- Line numbers for reference

### 7. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Shift+Enter` | Run current cell |
| `Ctrl+S` / `Cmd+S` | Save notebook |
| `Tab` | Indent (4 spaces) |

### 8. Saving Your Work

#### Auto-Save
- Notebook state is saved to browser localStorage every 30 seconds
- Persists for 24 hours
- Resume work on page reload

#### Manual Save
1. Click "💾 Save" button
2. Enter a filename (e.g., `my_analysis.ipynb`)
3. Notebook saved to `testApp1/notebooks/saved/`
4. Can be opened in Jupyter Lab/Notebook later

### 9. Kernel Management

#### Kernel Status
- 🟢 Green circle: Kernel ready
- 🔴 Red circle: Kernel error

#### Restart Kernel
- Click "🔄 Restart Kernel" button
- All variables are cleared
- Execution counter resets to 0
- Use when you need a fresh start

### 10. Output Visualization

The Output Viewer displays multiple output types:

#### Text Output
```python
print("Hello, IntegrityHoops!")
# Output: Hello, IntegrityHoops!
```

#### DataFrames (Tables)
```python
df.head()
# Output: Styled HTML table
```

#### Plots (Images)
```python
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.title('My Plot')
plt.show()
# Output: PNG image embedded
```

#### Error Messages
```python
x = 1 / 0
# Output: Formatted Python traceback with line numbers
```

## Example Workflows

### Workflow 1: Quick Data Exploration

```python
# Cell 1: Load data
import pandas as pd
df = pd.read_csv('06.21.25_KP_v_MIN_Offense.csv')
print(f"Loaded {len(df)} rows")
df.head()

# Cell 2: Check data quality
print("Missing values:")
print(df.isnull().sum())

# Cell 3: Basic statistics
df.describe()

# Cell 4: Visualize
import seaborn as sns
import matplotlib.pyplot as plt

sns.heatmap(df.corr(), annot=True)
plt.title('Correlation Matrix')
plt.show()
```

### Workflow 2: Linear Regression on Basketball Data

```python
# Cell 1: Load and prepare
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pandas as pd

df = pd.read_csv('game_data.csv')

# Cell 2: Define features and target
X = df[['assists', 'rebounds', 'steals']]
y = df['points']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Cell 3: Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Cell 4: Evaluate
from sklearn.metrics import r2_score
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
print(f"R² Score: {r2:.4f}")

# Cell 5: Visualize
import matplotlib.pyplot as plt
plt.scatter(y_test, y_pred)
plt.plot([y_test.min(), y_test.max()], 
         [y_test.min(), y_test.max()], 'r--')
plt.xlabel('Actual Points')
plt.ylabel('Predicted Points')
plt.title(f'Model Performance (R²={r2:.3f})')
plt.show()
```

### Workflow 3: Player Performance Analysis

```python
# Cell 1: Load player data
df = pd.read_csv('player_cognitive_scores.csv')

# Cell 2: Calculate averages by player
player_avg = df.groupby('PLAYER').agg({
    'CogScore': 'mean',
    'Minutes': 'sum',
    'Positive_Actions': 'sum',
    'Negative_Actions': 'sum'
}).round(2)

player_avg

# Cell 3: Top performers
top_10 = player_avg.sort_values('CogScore', ascending=False).head(10)

import matplotlib.pyplot as plt
plt.figure(figsize=(10, 6))
plt.barh(top_10.index, top_10['CogScore'])
plt.xlabel('Average Cognitive Score')
plt.title('Top 10 Players by Cognitive Score')
plt.tight_layout()
plt.show()
```

## Advanced Features

### Custom Visualizations

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Set custom style
sns.set_style('darkgrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Create multi-plot figure
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Line chart
axes[0, 0].plot(df['date'], df['score'])
axes[0, 0].set_title('Score Over Time')

# Plot 2: Bar chart
df.groupby('team')['points'].mean().plot(kind='bar', ax=axes[0, 1])
axes[0, 1].set_title('Average Points by Team')

# Plot 3: Scatter
axes[1, 0].scatter(df['assists'], df['points'], alpha=0.6)
axes[1, 0].set_title('Assists vs Points')

# Plot 4: Histogram
axes[1, 1].hist(df['minutes'], bins=20)
axes[1, 1].set_title('Minutes Distribution')

plt.tight_layout()
plt.show()
```

### Working with Multiple DataFrames

```python
# Load multiple datasets
df_offense = pd.read_csv('offense_data.csv')
df_defense = pd.read_csv('defense_data.csv')

# Merge on player name
df_combined = pd.merge(
    df_offense, 
    df_defense, 
    on='PLAYER', 
    how='inner',
    suffixes=('_off', '_def')
)

print(f"Combined dataset: {df_combined.shape}")
df_combined.head()
```

### Exporting Results

```python
# Export processed data
df_processed = df.copy()
# ... your processing ...
df_processed.to_csv('processed_results.csv', index=False)
print("Results saved to processed_results.csv")

# Export plots
plt.figure(figsize=(10, 6))
plt.plot(data)
plt.savefig('my_plot.png', dpi=300, bbox_inches='tight')
print("Plot saved to my_plot.png")
```

## Troubleshooting

### Common Issues

**Issue**: "No module named 'sklearn'"
- **Solution**: Ensure all dependencies are installed: `pip install scikit-learn`

**Issue**: Kernel not responding
- **Solution**: Click "Restart Kernel" button

**Issue**: Cell won't execute
- **Solution**: Check for syntax errors, restart kernel if needed

**Issue**: Plot not showing
- **Solution**: Make sure to call `plt.show()` at the end

**Issue**: CSV file not found
- **Solution**: Upload CSV first or verify file path

### Performance Tips

1. **Large Datasets**: Sample data for quick exploration
   ```python
   df_sample = df.sample(n=10000, random_state=42)
   ```

2. **Memory Management**: Delete unused variables
   ```python
   del large_dataframe
   ```

3. **Optimize Plots**: Reduce DPI for faster rendering
   ```python
   plt.rcParams['figure.dpi'] = 72  # Lower = faster
   ```

4. **Batch Operations**: Use vectorized pandas operations instead of loops

## Best Practices

1. ✅ **Organize Code**: One logical operation per cell
2. ✅ **Comment Code**: Explain complex operations
3. ✅ **Name Variables**: Use descriptive names (`player_stats` not `df2`)
4. ✅ **Check Data**: Always inspect data after loading
5. ✅ **Handle Errors**: Use try-except for risky operations
6. ✅ **Save Frequently**: Use manual save for important work
7. ✅ **Clear Output**: Remove old outputs to keep workspace clean

## Technical Details

### Architecture
- **Backend**: Flask + Jupyter Client
- **Kernel**: IPython kernel with Python 3.13
- **Frontend**: CodeMirror editor + Custom JS
- **Storage**: localStorage (auto-save) + File system (manual save)

### Supported Libraries
- pandas 2.3.1
- numpy 1.26.3
- matplotlib 3.8.2
- seaborn 0.13.1
- scikit-learn 1.4.0
- And all standard Python libraries

### M4 Optimization
The kernel is configured to leverage your M4 chip's:
- Multiple performance cores
- Efficient memory access
- Accelerated numerical computations

## Support & Resources

### Documentation
- **Main Docs**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Template Docs**: [notebooks/README.md](notebooks/README.md)
- **Deployment**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Getting Help
1. Check the troubleshooting section above
2. Review example workflows
3. Inspect browser console for JavaScript errors
4. Check Flask logs for backend errors

## Next Steps

Now that you're familiar with the ML Notebook, try:

1. **Upload your own basketball data** and perform EDA
2. **Build a linear regression model** to predict player performance
3. **Create custom visualizations** for game analysis
4. **Save your best notebooks** as templates for future use
5. **Combine with other IntegrityHoops features** like SmartDash

Happy analyzing! 🏀📊🤖

