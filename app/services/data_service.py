import io
import pandas as pd
from typing import Dict, Any, List
from fastapi import UploadFile

class DataService:
    @staticmethod
    async def process_upload(file: UploadFile) -> pd.DataFrame:
        """Reads an uploaded file into a Pandas DataFrame."""
        contents = await file.read()
        filename = file.filename or ""
        if filename.endswith('.csv'):
            return pd.read_csv(io.BytesIO(contents))
        else:
            return pd.read_excel(io.BytesIO(contents))

    @staticmethod
    def generate_statistical_summary(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generates statistical metadata for each column."""
        summary = []
        for col in df.columns:
            col_data = df[col]
            summary.append({
                "name": col,
                "type": str(col_data.dtype),
                "null_count": int(col_data.isnull().sum()),
                "unique_values_count": int(col_data.nunique()),
                # Safe casting to string for sample values to avoid JSON serialization issues
                "sample_values": col_data.dropna().astype(str).head(3).tolist()
            })
        return summary
