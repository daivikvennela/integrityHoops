# ML Notebook Templates

This directory contains Jupyter notebook templates for the ML Notebook interface.

## Available Templates

### 1. Linear Regression Template (`linear_regression_template.ipynb`)
A comprehensive template for building linear regression models:
- Data loading and exploration
- Correlation analysis
- Model training and evaluation
- Performance metrics (R², RMSE, MAE)
- Visualization of predictions and residuals
- Feature importance analysis

**Use Case**: Predicting continuous outcomes (e.g., player performance scores, game outcomes)

### 2. Data Exploration Template (`data_exploration_template.ipynb`)
Comprehensive exploratory data analysis (EDA):
- Dataset overview and statistics
- Missing value detection and visualization
- Correlation matrices
- Distribution plots
- Outlier detection using IQR method

**Use Case**: Understanding your dataset before modeling

### 3. Custom Analysis Blank (`custom_analysis_blank.ipynb`)
A minimal starter template with:
- Common library imports (pandas, numpy, matplotlib, seaborn, sklearn)
- Basic structure for custom analysis

**Use Case**: Starting from scratch with your own analysis

## How to Use

1. **Via Web Interface**: 
   - Navigate to `/ml-notebook` in the application
   - Select a template from the dropdown
   - The template will load automatically

2. **Direct Use**:
   - Open templates directly in Jupyter Lab/Notebook
   - Customize for your specific needs
   - Save as new notebooks

## Saved Notebooks

User-created notebooks are automatically saved in the `saved/` subdirectory when using the "Save Notebook" feature in the web interface.

## Requirements

All templates require:
- pandas >= 2.3.1
- numpy >= 1.26.3
- matplotlib >= 3.8.2
- seaborn >= 0.13.1
- scikit-learn >= 1.4.0

## Tips

- **Update Variable Names**: Remember to update column names (e.g., `target_column`, `feature_columns`) to match your dataset
- **CSV Loading**: Replace `# df = pd.read_csv('your_file.csv')` with actual file paths
- **M4 Optimization**: The kernel is optimized for Apple M4 chips with multi-core support
- **Auto-Save**: The web interface auto-saves your work every 30 seconds to browser localStorage

## Creating Custom Templates

To create your own template:

1. Build your notebook in the ML Notebook interface
2. Click "Save Notebook" and give it a name
3. Find it in the `saved/` directory
4. Copy to this directory to make it a permanent template
5. Update `ml_notebook_processor.py` to add it to the template list

## Support

For issues or questions about the ML Notebook interface, refer to the main application documentation or contact the development team.

