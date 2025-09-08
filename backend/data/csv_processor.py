import pandas as pd
import dask.dataframe as dd
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

from backend.config.settings import settings

class CSVProcessor:
    def __init__(self):
        self.sample_size = settings.SAMPLE_SIZE
        self.chunk_size = settings.CHUNK_SIZE
        
    async def process_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Process CSV file and extract metadata, sample, and statistics
        """
        try:
            # Check file size
            file_size = Path(file_path).stat().st_size / (1024 * 1024)  # MB
            
            if file_size > 100:  # Use Dask for large files
                return await self._process_large_csv(file_path)
            else:
                return await self._process_small_csv(file_path)
                
        except Exception as e:
            raise Exception(f"Failed to process CSV: {str(e)}")
    
    async def _process_small_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Process small CSV files using pandas
        """
        df = pd.read_csv(file_path)
        
        return {
            "total_rows": len(df),
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample": df.head(self.sample_size).to_dict('records'),
            "statistics": self._calculate_statistics(df),
            "dataframe": df,  # Keep for analysis
            "noun_mapping": self._create_noun_mapping(df)
        }
    
    async def _process_large_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Process large CSV files using Dask
        """
        ddf = dd.read_csv(file_path, blocksize=f"{self.chunk_size}KB")
        
        # Get basic info
        columns = ddf.columns.tolist()
        total_rows = len(ddf)
        
        # Get sample
        sample_df = ddf.head(self.sample_size)
        
        # Calculate statistics on sample
        stats = self._calculate_statistics(sample_df)
        
        return {
            "total_rows": total_rows,
            "columns": columns,
            "dtypes": {col: str(dtype) for col, dtype in ddf.dtypes.items()},
            "sample": sample_df.to_dict('records'),
            "statistics": stats,
            "is_large_file": True,
            "noun_mapping": self._create_noun_mapping(sample_df)
        }
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate basic statistics for numerical columns
        """
        stats = {}
        
        for col in df.select_dtypes(include=[np.number]).columns:
            stats[col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "null_count": int(df[col].isnull().sum())
            }
        
        # Add categorical column stats
        for col in df.select_dtypes(include=['object']).columns:
            stats[col] = {
                "unique_values": int(df[col].nunique()),
                "top_values": df[col].value_counts().head(5).to_dict(),
                "null_count": int(df[col].isnull().sum())
            }
        
        return stats
    
    def _create_noun_mapping(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Create noun-to-column mapping for better query understanding
        """
        mapping = {}
        
        for col in df.columns:
            # Extract potential nouns from column name
            nouns = self._extract_nouns(col)
            for noun in nouns:
                if noun not in mapping:
                    mapping[noun] = []
                mapping[noun].append(col)
            
            # Sample unique values for categorical columns
            if df[col].dtype == 'object':
                unique_values = df[col].dropna().unique()[:10]
                for value in unique_values:
                    value_nouns = self._extract_nouns(str(value))
                    for noun in value_nouns:
                        if noun not in mapping:
                            mapping[noun] = []
                        if col not in mapping[noun]:
                            mapping[noun].append(col)
        
        return mapping
    
    def _extract_nouns(self, text: str) -> List[str]:
        """
        Extract potential nouns from text (simplified version)
        """
        # Simple extraction based on common patterns
        words = text.lower().replace('_', ' ').replace('-', ' ').split()
        
        # Filter common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        nouns = [w for w in words if w not in stop_words and len(w) > 2]
        
        return nouns

class DataCache:
    """
    Cache processed data for faster retrieval
    """
    def __init__(self):
        self.cache_dir = Path(settings.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str) -> Optional[Dict]:
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def set(self, key: str, data: Dict):
        cache_file = self.cache_dir / f"{key}.json"
        with open(cache_file, 'w') as f:
            json.dump(data, f)
    
    def clear(self):
        for file in self.cache_dir.glob("*.json"):
            file.unlink()