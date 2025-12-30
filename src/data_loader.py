"""
Data loading and management module for Prompt Firewall
Wrapper around DataManager for backward compatibility and additional utilities
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
from data_manager import DataManager


class DataLoader:
    """Lightweight wrapper for data loading - uses optimized DataManager internally"""
    
    def __init__(self):
        """Initialize data loader"""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.processed_dir = self.data_dir / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_dataset(self) -> pd.DataFrame:
        """Load combined dataset"""
        # Load from DataManager which returns a single DataFrame
        data = DataManager.load()
        if isinstance(data, tuple):
            # If it returns a tuple, concatenate train and test
            train_df, test_df = data
            return pd.concat([train_df, test_df], ignore_index=True)
        return data
    
    def save_processed_data(self, data: pd.DataFrame, split: str = "processed"):
        """Save processed data to processed directory"""
        output_path = self.processed_dir / f"{split}_data.parquet"
        data.to_parquet(str(output_path))
        print(f"✓ Data saved: {output_path}")
    
    def load_processed_data(self, split: str = "processed") -> Optional[pd.DataFrame]:
        """Load processed data from directory"""
        file_path = self.processed_dir / f"{split}_data.parquet"
        if file_path.exists():
            return pd.read_parquet(str(file_path))
        return None


if __name__ == "__main__":
    loader = DataLoader()
    train, test = loader.load_dataset()
    print(f"✓ Train shape: {train.shape}")
    print(f"✓ Test shape: {test.shape}")
