import json
import csv
import os
from datetime import datetime
from typing import List, Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class DataExporter:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _generate_filename(self, prefix: str = "comments", format: str = "json") -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{format}"

    def to_json(self, comments: List[Dict], filename: str = None) -> str:
        if filename is None:
            filename = self._generate_filename(format="json")

        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(comments, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported to JSON: {filepath}")
        return filepath

    def to_csv(self, comments: List[Dict], filename: str = None) -> str:
        if filename is None:
            filename = self._generate_filename(format="csv")

        filepath = os.path.join(self.output_dir, filename)

        if not comments:
            logger.warning("No comments to export")
            return None

        df = pd.DataFrame(comments)
        df.to_csv(filepath, index=False, encoding="utf-8")

        logger.info(f"Exported to CSV: {filepath}")
        return filepath

    def to_excel(self, comments: List[Dict], filename: str = None) -> str:
        if filename is None:
            filename = self._generate_filename(format="xlsx")

        filepath = os.path.join(self.output_dir, filename)

        if not comments:
            logger.warning("No comments to export")
            return None

        df = pd.DataFrame(comments)

        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Comments")

            worksheet = writer.sheets["Comments"]
            for idx, col in enumerate(df.columns, 1):
                max_length = max(
                    df[col].astype(str).str.len().max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(64 + idx)].width = min(max_length + 2, 50)

        logger.info(f"Exported to Excel: {filepath}")
        return filepath

    def export_all_formats(self, comments: List[Dict], prefix: str = "comments") -> Dict[str, str]:
        results = {
            "json": self.to_json(comments, f"{prefix}.json"),
            "csv": self.to_csv(comments, f"{prefix}.csv"),
            "excel": self.to_excel(comments, f"{prefix}.xlsx"),
        }
        return results

    def get_export_summary(self, comments: List[Dict]) -> Dict:
        if not comments:
            return {"total_comments": 0}

        df = pd.DataFrame(comments)

        return {
            "total_comments": len(comments),
            "total_likes": int(df["likes"].sum()),
            "total_replies": int(df["replies"].sum()),
            "avg_likes": float(df["likes"].mean()),
            "avg_replies": float(df["replies"].mean()),
            "verified_users": int(df["user_verified"].sum()),
        }
