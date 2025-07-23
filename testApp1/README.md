# CSV ETL Processor Web Application

A modern web application for processing CSV files with ETL (Extract, Transform, Load) capabilities and data scraping functionality. Built with Flask, Pandas, and BeautifulSoup.

## Features

### 🚀 Core Features
- **File Upload**: Drag-and-drop CSV/Excel file upload with validation
- **ETL Processing**: Comprehensive data transformation capabilities
- **Data Scraping**: Web scraping functionality for enriching data
- **Interactive Table**: Modern, responsive data table with search and sort
- **Export Options**: Download processed data in CSV or JSON format

### 🔧 Processing Options
- **Remove Duplicates**: Eliminate duplicate rows from the dataset
- **Fill Missing Values**: Replace null/empty values with 'N/A'
- **Add Timestamp**: Include processing timestamp for data tracking
- **Scrape Additional Data**: Enrich data with web-scraped information

### 📊 Data Visualization
- **Real-time Search**: Filter table data on-the-fly
- **Column Sorting**: Click headers to sort data
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Data Summary**: Processing statistics and quality metrics

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   cd testApp1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## Usage Guide

### 1. Upload Your File
- Drag and drop your CSV or Excel file onto the upload area
- Or click to browse and select a file
- Supported formats: `.csv`, `.xlsx`, `.xls`

### 2. Configure Processing Options
- **Remove Duplicates**: Check to eliminate duplicate rows
- **Fill Missing Values**: Check to replace empty cells with 'N/A'
- **Add Timestamp**: Check to add processing timestamp
- **Scrape Additional Data**: Check to enrich data with web information

### 3. Process Data
- Click "Process Data" to start the ETL pipeline
- Wait for processing to complete
- View results in the interactive table

### 4. Export Results
- Use the search box to filter data
- Click column headers to sort
- Download processed data as CSV or JSON

## Sample Data

The application includes a sample CSV file generator. To create a sample file:

```python
python etl_scripts.py
```

This will create `sample_companies.csv` with test data for demonstration.

## API Endpoints

### POST /upload
Upload and process a CSV file
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: CSV/Excel file
  - `remove_duplicates`: boolean
  - `fill_missing`: boolean
  - `add_timestamp`: boolean
  - `scrape_additional_data`: boolean

### POST /api/process
Process CSV data via API
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "csv_data": "csv_content_as_string",
    "processing_options": {
      "remove_duplicates": true,
      "fill_missing": true,
      "add_timestamp": true,
      "scrape_additional_data": true
    }
  }
  ```

### GET /download/<filename>
Download processed file
- Returns the processed CSV file as attachment

## Project Structure

```
testApp1/
├── app.py                 # Main Flask application
├── etl_scripts.py         # ETL processing functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template with styling
│   ├── index.html        # Upload page
│   └── results.html      # Results display page
├── uploads/              # Uploaded files (auto-created)
└── processed/            # Processed files (auto-created)
```

## ETL Processing Features

### Data Cleaning
- Remove leading/trailing whitespace
- Standardize date formats
- Convert empty strings to NaN
- Data type validation

### Data Enrichment
- Company information scraping
- Website data extraction
- Industry classification
- Contact information validation

### Data Transformation
- Column renaming
- Data filtering
- Aggregation operations
- Pivot table creation

### Quality Validation
- Missing value detection
- Duplicate row identification
- Data completeness metrics
- Format validation (email, phone)

## Customization

### Adding New Processing Options
1. Modify `app.py` in the `process_data_etl` function
2. Add new checkbox in `templates/index.html`
3. Update the processing logic as needed

### Custom Scraping Functions
1. Extend the `DataProcessor` class in `etl_scripts.py`
2. Add new scraping methods
3. Integrate with the main processing pipeline

### Styling Changes
- Modify CSS in `templates/base.html`
- Update Bootstrap classes in templates
- Customize color scheme and layout

## Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Processing errors
- Network timeouts during scraping
- Data validation failures
- File upload issues

## Security Considerations

- File upload validation
- Secure filename handling
- Request size limits
- Input sanitization
- Error message filtering

## Performance Optimization

- Efficient pandas operations
- Lazy loading for large datasets
- Optimized database queries
- Caching for repeated operations

## Troubleshooting

### Common Issues

1. **File upload fails**
   - Check file format (CSV, XLSX, XLS only)
   - Ensure file size is under 16MB
   - Verify file is not corrupted

2. **Processing takes too long**
   - Large files may take time to process
   - Disable scraping for faster processing
   - Check system resources

3. **Scraping doesn't work**
   - Network connectivity issues
   - Website blocking requests
   - Rate limiting from target sites

### Debug Mode
Run with debug enabled for detailed error messages:
```bash
export FLASK_ENV=development
python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs
3. Create an issue with detailed information

---

**Built with ❤️ using Flask, Pandas, and Bootstrap** 