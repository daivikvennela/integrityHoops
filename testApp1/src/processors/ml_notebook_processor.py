"""
ML Notebook Processor
Handles notebook execution, CSV integration, and template management
"""

import logging
import os
import base64
import json
from typing import Dict, List, Any, Optional
import pandas as pd
import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

logger = logging.getLogger(__name__)


class MLNotebookProcessor:
    """
    Processor for ML notebook operations including template management,
    CSV integration, and output formatting.
    """
    
    def __init__(self, data_folder: str):
        """
        Initialize the ML notebook processor.
        
        Args:
            data_folder: Path to data folder for CSV files
        """
        self.data_folder = data_folder
        
    def load_csv_to_dataframe(self, csv_path: str) -> Dict[str, Any]:
        """
        Load a CSV file and return DataFrame info.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Dictionary with DataFrame info and preview
        """
        try:
            df = pd.read_csv(csv_path)
            
            # Get basic info
            info = {
                'success': True,
                'shape': df.shape,
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.astype(str).to_dict(),
                'preview': df.head(10).to_dict('records'),
                'preview_html': df.head(10).to_html(classes='dataframe', border=0),
                'memory_usage': df.memory_usage(deep=True).sum() / (1024 ** 2),  # MB
                'null_counts': df.isnull().sum().to_dict()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_csv_load_code(self, csv_filename: str, variable_name: str = 'df') -> str:
        """
        Generate Python code to load a CSV file into a pandas DataFrame.
        
        Args:
            csv_filename: Name of CSV file
            variable_name: Variable name for the DataFrame
            
        Returns:
            Python code string
        """
        code = f"""# Load CSV data
import pandas as pd

{variable_name} = pd.read_csv('{csv_filename}')

# Display basic information
print(f"Dataset loaded: {{len({variable_name})}} rows, {{len({variable_name}.columns)}} columns")
print(f"\\nColumns: {{{variable_name}.columns.tolist()}}")
print(f"\\nFirst few rows:")
{variable_name}.head()
"""
        return code
    
    def format_output_for_display(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format execution results for frontend display.
        
        Args:
            execution_result: Raw execution result from kernel
            
        Returns:
            Formatted output ready for display
        """
        formatted = {
            'success': execution_result.get('success', False),
            'text_output': execution_result.get('output', ''),
            'error_output': execution_result.get('error', ''),
            'html_outputs': [],
            'image_outputs': [],
            'execution_count': execution_result.get('execution_count', 0)
        }
        
        # Process display data
        display_data = execution_result.get('display_data', [])
        for item in display_data:
            data = item.get('data', {})
            
            # Handle HTML (tables, etc.)
            if 'text/html' in data:
                formatted['html_outputs'].append({
                    'type': 'html',
                    'content': data['text/html']
                })
            
            # Handle images (matplotlib plots)
            if 'image/png' in data:
                # Image data is already base64 encoded
                formatted['image_outputs'].append({
                    'type': 'image',
                    'format': 'png',
                    'data': data['image/png']
                })
            
            # Handle plain text
            if 'text/plain' in data and not any(k in data for k in ['text/html', 'image/png']):
                formatted['text_output'] += data['text/plain'] + '\n'
        
        return formatted
    
    def create_linear_regression_template(self) -> List[Dict[str, str]]:
        """
        Create a linear regression template with pre-configured cells.
        
        Returns:
            List of cell dictionaries
        """
        cells = [
            {
                'type': 'markdown',
                'content': '# Linear Regression Analysis\n\nThis notebook demonstrates linear regression modeling on your dataset.'
            },
            {
                'type': 'code',
                'content': '''# Step 1: Load and explore the data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load your CSV (replace 'your_file.csv' with actual filename)
# df = pd.read_csv('your_file.csv')

print("Dataset loaded successfully!")
print(f"Shape: {df.shape}")
print(f"\\nColumns:\\n{df.columns.tolist()}")
df.head()'''
            },
            {
                'type': 'code',
                'content': '''# Step 2: Data exploration and visualization
# Display basic statistics
print("\\n=== Basic Statistics ===")
df.describe()'''
            },
            {
                'type': 'code',
                'content': '''# Check for missing values
print("\\n=== Missing Values ===")
missing = df.isnull().sum()
print(missing[missing > 0])

# Visualize correlations
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.show()'''
            },
            {
                'type': 'markdown',
                'content': '## Linear Regression Model\n\nNow let\'s build a linear regression model. Update the target and feature columns below.'
            },
            {
                'type': 'code',
                'content': '''# Step 3: Prepare data for modeling
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Define target and features (UPDATE THESE!)
target_column = 'target'  # Replace with your target column name
feature_columns = ['feature1', 'feature2']  # Replace with your feature column names

# Select features and target
X = df[feature_columns]
y = df[target_column]

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training set: {X_train.shape[0]} samples")
print(f"Testing set: {X_test.shape[0]} samples")'''
            },
            {
                'type': 'code',
                'content': '''# Step 4: Train the model
model = LinearRegression()
model.fit(X_train, y_train)

print("Model trained successfully!")
print(f"\\nModel coefficients:")
for feature, coef in zip(feature_columns, model.coef_):
    print(f"  {feature}: {coef:.4f}")
print(f"\\nIntercept: {model.intercept_:.4f}")'''
            },
            {
                'type': 'code',
                'content': '''# Step 5: Make predictions and evaluate
y_pred_train = model.predict(X_train)
y_pred_test = model.predict(X_test)

# Calculate metrics
train_r2 = r2_score(y_train, y_pred_train)
test_r2 = r2_score(y_test, y_pred_test)
train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
test_mae = mean_absolute_error(y_test, y_pred_test)

print("=== Model Performance ===")
print(f"\\nTraining Set:")
print(f"  R² Score: {train_r2:.4f}")
print(f"  RMSE: {train_rmse:.4f}")
print(f"\\nTesting Set:")
print(f"  R² Score: {test_r2:.4f}")
print(f"  RMSE: {test_rmse:.4f}")
print(f"  MAE: {test_mae:.4f}")'''
            },
            {
                'type': 'code',
                'content': '''# Step 6: Visualize results
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Actual vs Predicted
axes[0].scatter(y_test, y_pred_test, alpha=0.6)
axes[0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
axes[0].set_xlabel('Actual Values')
axes[0].set_ylabel('Predicted Values')
axes[0].set_title(f'Actual vs Predicted (R² = {test_r2:.4f})')
axes[0].grid(True, alpha=0.3)

# Residuals
residuals = y_test - y_pred_test
axes[1].scatter(y_pred_test, residuals, alpha=0.6)
axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
axes[1].set_xlabel('Predicted Values')
axes[1].set_ylabel('Residuals')
axes[1].set_title('Residual Plot')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()'''
            },
            {
                'type': 'markdown',
                'content': '## Summary\n\nYour linear regression model has been trained and evaluated. Review the metrics and visualizations above to assess model performance.'
            }
        ]
        
        return cells
    
    def create_data_exploration_template(self) -> List[Dict[str, str]]:
        """
        Create a data exploration template.
        
        Returns:
            List of cell dictionaries
        """
        cells = [
            {
                'type': 'markdown',
                'content': '# Data Exploration and Analysis\n\nComprehensive exploratory data analysis (EDA) for your dataset.'
            },
            {
                'type': 'code',
                'content': '''# Load the data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load your CSV
# df = pd.read_csv('your_file.csv')

print("Dataset Overview")
print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"\\nColumn Names:\\n{df.columns.tolist()}")'''
            },
            {
                'type': 'code',
                'content': '''# Display first and last few rows
print("=== First 5 Rows ===")
display(df.head())

print("\\n=== Last 5 Rows ===")
display(df.tail())'''
            },
            {
                'type': 'code',
                'content': '''# Data types and info
print("=== Data Types ===")
print(df.dtypes)

print("\\n=== Dataset Info ===")
df.info()'''
            },
            {
                'type': 'code',
                'content': '''# Statistical summary
print("=== Statistical Summary ===")
df.describe()'''
            },
            {
                'type': 'code',
                'content': '''# Check for missing values
print("=== Missing Values ===")
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100

missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Percentage': missing_pct
})
missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing Count', ascending=False)

if len(missing_df) > 0:
    print(missing_df)
    
    # Visualize missing values
    plt.figure(figsize=(10, 6))
    missing_df['Missing Count'].plot(kind='bar')
    plt.title('Missing Values by Column')
    plt.ylabel('Count')
    plt.tight_layout()
    plt.show()
else:
    print("No missing values found!")'''
            },
            {
                'type': 'code',
                'content': '''# Correlation analysis for numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns

if len(numeric_cols) > 1:
    plt.figure(figsize=(12, 10))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', center=0, 
                fmt='.2f', square=True, linewidths=1)
    plt.title('Correlation Matrix')
    plt.tight_layout()
    plt.show()
else:
    print("Not enough numeric columns for correlation analysis")'''
            },
            {
                'type': 'code',
                'content': '''# Distribution plots for numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns

if len(numeric_cols) > 0:
    n_cols = min(3, len(numeric_cols))
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, n_rows * 4))
    axes = axes.flatten() if len(numeric_cols) > 1 else [axes]
    
    for idx, col in enumerate(numeric_cols):
        if idx < len(axes):
            df[col].hist(bins=30, ax=axes[idx], edgecolor='black')
            axes[idx].set_title(f'Distribution of {col}')
            axes[idx].set_xlabel(col)
            axes[idx].set_ylabel('Frequency')
    
    # Hide empty subplots
    for idx in range(len(numeric_cols), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.show()'''
            },
            {
                'type': 'code',
                'content': '''# Detect outliers using IQR method
numeric_cols = df.select_dtypes(include=[np.number]).columns

print("=== Outlier Detection (IQR Method) ===")
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    if len(outliers) > 0:
        print(f"\\n{col}: {len(outliers)} outliers detected ({len(outliers)/len(df)*100:.2f}%)")'''
            },
            {
                'type': 'markdown',
                'content': '## Summary\n\nYour exploratory data analysis is complete. Review the statistics, visualizations, and data quality checks above.'
            }
        ]
        
        return cells
    
    def create_blank_template(self) -> List[Dict[str, str]]:
        """
        Create a blank notebook template with common imports.
        
        Returns:
            List of cell dictionaries
        """
        cells = [
            {
                'type': 'markdown',
                'content': '# Custom Analysis\n\nStart your custom analysis here.'
            },
            {
                'type': 'code',
                'content': '''# Import common libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

print("Libraries imported successfully!")'''
            },
            {
                'type': 'code',
                'content': '''# Load your data
# df = pd.read_csv('your_file.csv')

# Your analysis code here...'''
            }
        ]
        
        return cells
    
    def save_notebook_as_ipynb(self, cells: List[Dict[str, str]], output_path: str):
        """
        Save cells as a Jupyter notebook (.ipynb) file.
        
        Args:
            cells: List of cell dictionaries
            output_path: Path to save the notebook
        """
        try:
            nb = new_notebook()
            
            for cell in cells:
                if cell['type'] == 'code':
                    nb.cells.append(new_code_cell(cell['content']))
                elif cell['type'] == 'markdown':
                    nb.cells.append(new_markdown_cell(cell['content']))
            
            with open(output_path, 'w', encoding='utf-8') as f:
                nbformat.write(nb, f)
            
            logger.info(f"Notebook saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving notebook: {e}")
            return False
    
    def load_notebook_from_ipynb(self, notebook_path: str) -> List[Dict[str, str]]:
        """
        Load cells from a Jupyter notebook (.ipynb) file.
        
        Args:
            notebook_path: Path to notebook file
            
        Returns:
            List of cell dictionaries
        """
        try:
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)
            
            cells = []
            for cell in nb.cells:
                cells.append({
                    'type': cell.cell_type,
                    'content': cell.source
                })
            
            return cells
            
        except Exception as e:
            logger.error(f"Error loading notebook: {e}")
            return []

