"""Script generators for submatrix data fetching."""

from __future__ import annotations


def generate_basic_fetcher_script(submatrix_id: int, measurement_quantities: list[str], output_format: str) -> str:
    """Generate a basic Python script for fetching submatrix data."""

    patterns_str = ", ".join(f'"{mq}"' for mq in measurement_quantities)

    output_code = ""
    if output_format == "csv":
        output_code = f'df.to_csv("submatrix_{submatrix_id}_data.csv", index=True)'
    elif output_format == "json":
        output_code = f'df.to_json("submatrix_{submatrix_id}_data.json", orient="records", indent=2)'
    elif output_format == "parquet":
        output_code = f'df.to_parquet("submatrix_{submatrix_id}_data.parquet")'
    elif output_format == "excel":
        output_code = f'df.to_excel("submatrix_{submatrix_id}_data.xlsx", index=True)'
    else:
        output_code = "print(\"Data loaded into DataFrame 'df'\")"

    return f'''#!/usr/bin/env python3
"""
Basic Submatrix Data Fetcher
Fetches data from submatrix {submatrix_id}
"""

import pandas as pd
from odsbox import ConI

def main():
    # Connect to ODS server
    with ConI(url="http://localhost:8087/api", auth=("your_username", "your_password")) as con_i:
    
        # Fetch data from submatrix
        df = con_i.bulk.data_read(
            submatrix_iid={submatrix_id},
            column_patterns=[{patterns_str}],
            date_as_timestamp=True,
            set_independent_as_index=True
        )
        
        print(f"Loaded data with shape: {{df.shape}}")
        print(f"Columns: {{list(df.columns)}}")
        print("\\nFirst 5 rows:")
        print(df.head())
        
        # Save to file
        {output_code}
        print("\\nData saved successfully!")

if __name__ == "__main__":
    main()
'''


def generate_advanced_fetcher_script(
    submatrix_id: int,
    measurement_quantities: list[str],
    output_format: str,
    include_visualization: bool,
    include_analysis: bool,
) -> str:
    """Generate an advanced Python script with error handling and logging."""

    patterns_str = ", ".join(f'"{mq}"' for mq in measurement_quantities)

    viz_code = ""
    if include_visualization:
        viz_code = """
        # Create visualizations
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            fig, axes = plt.subplots(len(numeric_cols), 1, figsize=(12, 4*len(numeric_cols)))
            if len(numeric_cols) == 1:
                axes = [axes]
            
            for i, col in enumerate(numeric_cols):
                df[col].plot(ax=axes[i], title=f'{col} over time')
                axes[i].set_xlabel('Time')
                axes[i].set_ylabel(col)
                axes[i].grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.savefig(f'submatrix_{submatrix_id}_plots.png', dpi=150, bbox_inches='tight')
            plt.show()
            logger.info(f"Visualizations saved to submatrix_{submatrix_id}_plots.png")
        """

    analysis_code = ""
    if include_analysis:
        analysis_code = """
        # Basic data analysis
        logger.info("Performing basic data analysis...")
        logger.info("Summary statistics:")
        logger.info(df.describe())
        
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            logger.info("Missing values per column:")
            logger.info(missing_data[missing_data > 0])
        """

    return f'''#!/usr/bin/env python3
"""
Advanced Submatrix Data Fetcher with Error Handling
Fetches data from submatrix {submatrix_id}
"""

import logging
import sys
import pandas as pd
import numpy as np
from odsbox import ConI

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'submatrix_{submatrix_id}_fetcher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SubmatrixDataFetcher:
    """Advanced data fetcher with error handling."""
    
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.con_i = None
    
    def connect(self):
        """Establish connection to ODS server."""
        try:
            self.con_i = ConI(url=self.url, auth=(self.username, self.password))
            logger.info("Successfully connected to ODS server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {{e}}")
            return False
    
    def fetch_submatrix_data(self, submatrix_id: int, column_patterns: list = None):
        """Fetch data from submatrix."""
        try:
            logger.info(f"Fetching data from submatrix {{submatrix_id}}")
            
            df = self.con_i.bulk.data_read(
                submatrix_iid=submatrix_id,
                column_patterns=column_patterns,
                date_as_timestamp=True,
                set_independent_as_index=True
            )
            
            logger.info(f"Successfully loaded: shape={{df.shape}}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data: {{e}}")
            raise

def main():
    ODS_URL = "http://localhost:8087/api"
    ODS_USERNAME = "your_username"
    ODS_PASSWORD = "your_password"
    SUBMATRIX_ID = {submatrix_id}
    COLUMN_PATTERNS = [{patterns_str}]
    OUTPUT_FORMAT = "{output_format}"
    
    fetcher = None
    try:
        fetcher = SubmatrixDataFetcher(ODS_URL, ODS_USERNAME, ODS_PASSWORD)
        
        if not fetcher.connect():
            sys.exit(1)
        
        df = fetcher.fetch_submatrix_data(SUBMATRIX_ID, COLUMN_PATTERNS)
        logger.info(f"Data preview:\\n{{df.head()}}")
        
        output_file = f"submatrix_{{SUBMATRIX_ID}}_data.{{OUTPUT_FORMAT}}"
        if OUTPUT_FORMAT == "csv":
            df.to_csv(output_file, index=True)
        elif OUTPUT_FORMAT == "json":
            df.to_json(output_file, orient="records", indent=2, date_format="iso")
        elif OUTPUT_FORMAT == "parquet":
            df.to_parquet(output_file)
        elif OUTPUT_FORMAT == "excel":
            df.to_excel(output_file, index=True)
        
        {analysis_code}
        {viz_code}
        
        logger.info("Data fetching completed successfully!")
        
    except Exception as e:
        logger.error(f"Script failed: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''


def generate_batch_fetcher_script(submatrix_id: int, measurement_quantities: list[str], output_format: str) -> str:
    """Generate a batch processing script for multiple submatrices."""

    patterns_str = ", ".join(f'"{mq}"' for mq in measurement_quantities)

    return f'''#!/usr/bin/env python3
"""
Batch Submatrix Data Fetcher
Processes multiple submatrices efficiently
"""

import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from odsbox import ConI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BatchSubmatrixFetcher:
    """Batch processor for multiple submatrices."""
    
    def __init__(self, url: str, username: str, password: str, max_workers: int = 4):
        self.url = url
        self.username = username
        self.password = password
        self.max_workers = max_workers
        self.con_i = None
    
    def connect(self):
        """Establish connection."""
        try:
            self.con_i = ConI(url=self.url, auth=(self.username, self.password))
            logger.info("Connected to ODS server")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {{e}}")
            return False
    
    def fetch_single_submatrix(self, submatrix_id: int, column_patterns: list = None):
        """Fetch data from a single submatrix."""
        try:
            df = self.con_i.bulk.data_read(
                submatrix_iid=submatrix_id,
                column_patterns=column_patterns,
                date_as_timestamp=True,
                set_independent_as_index=True
            )
            logger.info(f"Submatrix {{submatrix_id}}: loaded {{df.shape[0]}} rows")
            return {{'submatrix_id': submatrix_id, 'dataframe': df, 'success': True}}
        except Exception as e:
            logger.error(f"Failed submatrix {{submatrix_id}}: {{e}}")
            return {{'submatrix_id': submatrix_id, 'dataframe': None, 'success': False, 'error': str(e)}}

def main():
    ODS_URL = "http://localhost:8087/api"
    ODS_USERNAME = "your_username"
    ODS_PASSWORD = "your_password"
    SUBMATRIX_IDS = [{submatrix_id}]  # Add more IDs
    COLUMN_PATTERNS = [{patterns_str}]
    
    fetcher = BatchSubmatrixFetcher(ODS_URL, ODS_USERNAME, ODS_PASSWORD)
    
    if not fetcher.connect():
        sys.exit(1)
    
    logger.info(f"Processing {{len(SUBMATRIX_IDS)}} submatrices")
    successful = 0
    
    for sm_id in SUBMATRIX_IDS:
        result = fetcher.fetch_single_submatrix(sm_id, COLUMN_PATTERNS)
        if result['success']:
            df = result['dataframe']
            df.to_csv(f"submatrix_{{sm_id}}_data.{output_format}", index=True)
            successful += 1
    
    logger.info(f"Batch completed: {{successful}}/{{len(SUBMATRIX_IDS)}} successful")

if __name__ == "__main__":
    main()
'''


def generate_analysis_fetcher_script(
    submatrix_id: int, measurement_quantities: list[str], output_format: str, include_visualization: bool
) -> str:
    """Generate a script focused on data analysis and visualization."""

    patterns_str = ", ".join(f'"{mq}"' for mq in measurement_quantities)

    return f'''#!/usr/bin/env python3
"""
Submatrix Data Analysis Script
Fetches data and performs comprehensive analysis
"""

import logging
import sys
import pandas as pd
import numpy as np
from odsbox import ConI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def perform_statistical_analysis(df):
    """Perform comprehensive statistical analysis."""
    logger.info("=== STATISTICAL ANALYSIS ===")
    logger.info(f"Shape: {{df.shape}}")
    logger.info(f"Data Types:\\n{{df.dtypes}}")
    
    missing = df.isnull().sum()
    if missing.sum() > 0:
        logger.info(f"Missing Values:\\n{{missing[missing > 0]}}")
    
    logger.info(f"Descriptive Statistics:\\n{{df.describe()}}")
    
    return {{
        'shape': df.shape,
        'missing_values': int(missing.sum()),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
    }}

def main():
    ODS_URL = "http://localhost:8087/api"
    ODS_USERNAME = "your_username"
    ODS_PASSWORD = "your_password"
    SUBMATRIX_ID = {submatrix_id}
    COLUMN_PATTERNS = [{patterns_str}]
    OUTPUT_FORMAT = "{output_format}"
    
    try:
        with ConI(url=ODS_URL, auth=(ODS_USERNAME, ODS_PASSWORD)) as con_i:
            logger.info("Connected to ODS server")
            
            logger.info(f"Fetching data from submatrix {{SUBMATRIX_ID}}")
            df = con_i.bulk.data_read(
                submatrix_iid=SUBMATRIX_ID,
                column_patterns=COLUMN_PATTERNS,
                date_as_timestamp=True,
                set_independent_as_index=True
            )
        
        logger.info(f"Data loaded: shape={{df.shape}}")
        stats = perform_statistical_analysis(df)
        
        output_file = f"submatrix_{{SUBMATRIX_ID}}_analysis.{{OUTPUT_FORMAT}}"
        if OUTPUT_FORMAT == "csv":
            df.to_csv(output_file, index=True)
        elif OUTPUT_FORMAT == "json":
            df.to_json(output_file, orient="records", indent=2, date_format="iso")
        elif OUTPUT_FORMAT == "parquet":
            df.to_parquet(output_file)
        elif OUTPUT_FORMAT == "excel":
            df.to_excel(output_file, index=True)
        
        logger.info(f"Data saved to {{output_file}}")
        logger.info("Analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Analysis failed: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
