import os
import shutil
import pandas as pd

class FileManagerDAO:
    def __init__(self, download_dir: str):
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)

    def get_existing_csvs(self):
        return {f for f in os.listdir(self.download_dir) if f.endswith(".csv")}

    def move_file(self, src_path: str, final_filename: str):
        final_path = os.path.join(self.download_dir, final_filename)
        shutil.move(src_path, final_path)
        return final_path

    def read_csv(self, path: str):
        return pd.read_csv(path)

    @staticmethod
    def normalize_headers(df: pd.DataFrame):
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s", origin="unix")
        df = df.rename(columns={
            "especie": "ticker",
            "fecha": "date",
            "apertura": "open",
            "maximo": "high",
            "minimo": "low",
            "cierre": "close",
            "volumen": "volume"
        })
        return df
