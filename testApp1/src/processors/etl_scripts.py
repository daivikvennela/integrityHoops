"""
ETL Scripts for CSV Data Processing
This module contains various ETL functions for data transformation and scraping
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """Main class for ETL data processing operations"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def clean_data(self, df):
        """Clean and standardize data"""
        try:
            # Remove leading/trailing whitespace from string columns
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str).str.strip()
            
            # Convert empty strings to NaN
            df = df.replace(['', 'nan', 'None', 'null'], pd.NA)
            
            # Standardize date columns
            date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
            for col in date_columns:
                try:
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                except:
                    pass
            
            return df
        except Exception as e:
            logger.error(f"Error cleaning data: {e}")
            return df
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone))
        return len(digits) >= 10
    
    def enrich_company_data(self, company_name):
        """Enrich company data with additional information"""
        try:
            # This is a mock implementation - in production, you'd integrate with real APIs
            # like Crunchbase, LinkedIn, or other business data providers
            
            enriched_data = {
                'company_name': company_name,
                'website': f"https://{company_name.lower().replace(' ', '')}.com",
                'industry': self._get_industry_category(company_name),
                'employee_count': self._get_employee_range(company_name),
                'revenue_range': self._get_revenue_range(company_name),
                'location': self._get_location(company_name),
                'founded_year': self._get_founded_year(company_name),
                'description': f"{company_name} is a leading company in their industry.",
                'social_media': {
                    'linkedin': f"https://linkedin.com/company/{company_name.lower().replace(' ', '')}",
                    'twitter': f"https://twitter.com/{company_name.lower().replace(' ', '')}",
                    'facebook': f"https://facebook.com/{company_name.lower().replace(' ', '')}"
                }
            }
            
            return enriched_data
        except Exception as e:
            logger.error(f"Error enriching company data for {company_name}: {e}")
            return {'company_name': company_name}
    
    def _get_industry_category(self, company_name):
        """Mock function to determine industry category"""
        industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing', 'Education']
        # Simple hash-based selection for demo purposes
        hash_val = hash(company_name) % len(industries)
        return industries[hash_val]
    
    def _get_employee_range(self, company_name):
        """Mock function to get employee count range"""
        ranges = ['1-10', '11-50', '51-200', '201-1000', '1001-5000', '5000+']
        hash_val = hash(company_name) % len(ranges)
        return ranges[hash_val]
    
    def _get_revenue_range(self, company_name):
        """Mock function to get revenue range"""
        ranges = ['<$1M', '$1M-$10M', '$10M-$50M', '$50M-$100M', '$100M-$1B', '$1B+']
        hash_val = hash(company_name) % len(ranges)
        return ranges[hash_val]
    
    def _get_location(self, company_name):
        """Mock function to get company location"""
        locations = ['San Francisco, CA', 'New York, NY', 'Austin, TX', 'Seattle, WA', 'Boston, MA', 'Chicago, IL']
        hash_val = hash(company_name) % len(locations)
        return locations[hash_val]
    
    def _get_founded_year(self, company_name):
        """Mock function to get founded year"""
        return str(2010 + (hash(company_name) % 20))
    
    def scrape_web_data(self, url, selectors=None):
        """Scrape data from a website using CSS selectors"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            if not selectors:
                # Default selectors for common data
                selectors = {
                    'title': 'title',
                    'description': 'meta[name="description"]',
                    'keywords': 'meta[name="keywords"]'
                }
            
            scraped_data = {}
            for key, selector in selectors.items():
                element = soup.select_one(selector)
                if element:
                    if key == 'description' or key == 'keywords':
                        scraped_data[key] = element.get('content', '')
                    else:
                        scraped_data[key] = element.get_text().strip()
            
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {}
    
    def transform_data(self, df, transformations):
        """Apply various data transformations"""
        try:
            processed_df = df.copy()
            
            for transformation in transformations:
                if transformation['type'] == 'rename_column':
                    processed_df = processed_df.rename(columns=transformation['mapping'])
                
                elif transformation['type'] == 'add_column':
                    processed_df[transformation['column_name']] = transformation['value']
                
                elif transformation['type'] == 'filter_rows':
                    condition = transformation['condition']
                    processed_df = processed_df.query(condition)
                
                elif transformation['type'] == 'sort_data':
                    processed_df = processed_df.sort_values(transformation['columns'])
                
                elif transformation['type'] == 'aggregate':
                    group_cols = transformation['group_by']
                    agg_dict = transformation['aggregations']
                    processed_df = processed_df.groupby(group_cols).agg(agg_dict).reset_index()
                
                elif transformation['type'] == 'pivot':
                    processed_df = processed_df.pivot_table(
                        index=transformation['index'],
                        columns=transformation['columns'],
                        values=transformation['values'],
                        aggfunc=transformation.get('aggfunc', 'mean')
                    ).reset_index()
            
            return processed_df
            
        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            return df
    
    def validate_data_quality(self, df):
        """Validate data quality and return quality metrics"""
        try:
            quality_report = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'missing_values': df.isnull().sum().to_dict(),
                'duplicate_rows': df.duplicated().sum(),
                'data_types': df.dtypes.to_dict(),
                'unique_values': {col: df[col].nunique() for col in df.columns}
            }
            
            # Calculate completeness percentage
            total_cells = len(df) * len(df.columns)
            missing_cells = df.isnull().sum().sum()
            quality_report['completeness_percentage'] = ((total_cells - missing_cells) / total_cells) * 100
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Error validating data quality: {e}")
            return {}

def create_sample_csv():
    """Create a sample CSV file for testing"""
    sample_data = {
        'Company_Name': [
            'TechCorp Solutions',
            'InnovateSoft Inc',
            'DataFlow Systems',
            'CloudTech Partners',
            'Digital Dynamics',
            'Smart Solutions Ltd',
            'FutureTech Group',
            'CyberNet Security',
            'AI Innovations',
            'Blockchain Ventures'
        ],
        'Contact_Email': [
            'contact@techcorp.com',
            'info@innovatesoft.com',
            'hello@dataflow.com',
            'support@cloudtech.com',
            'contact@digitaldynamics.com',
            'info@smartsolutions.com',
            'hello@futuretech.com',
            'support@cybernet.com',
            'contact@aiinnovations.com',
            'info@blockchainventures.com'
        ],
        'Phone_Number': [
            '+1-555-0101',
            '+1-555-0102',
            '+1-555-0103',
            '+1-555-0104',
            '+1-555-0105',
            '+1-555-0106',
            '+1-555-0107',
            '+1-555-0108',
            '+1-555-0109',
            '+1-555-0110'
        ],
        'Revenue': [
            5000000,
            12000000,
            8500000,
            25000000,
            15000000,
            8000000,
            30000000,
            18000000,
            22000000,
            12000000
        ],
        'Employees': [
            50,
            120,
            85,
            250,
            150,
            80,
            300,
            180,
            220,
            120
        ]
    }
    
    df = pd.DataFrame(sample_data)
    return df

if __name__ == "__main__":
    # Create sample CSV for testing
    sample_df = create_sample_csv()
    sample_df.to_csv('sample_companies.csv', index=False)
    print("Sample CSV file created: sample_companies.csv") 