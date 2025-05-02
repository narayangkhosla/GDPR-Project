import pandas as pd
import argparse
import os
from glob import glob
import sys

# Setup CLI argument
parser = argparse.ArgumentParser(description="Read obfuscated Parquet output.")
parser.add_argument(
    "--file",
    help="Filename of the obfuscated Parquet file inside the 'results/' folder. "
    "If not provided, the latest matching file will be used.",
)

args = parser.parse_args()

# Determine file path
results_dir = "results"

if args.file:
    file_path = os.path.join(results_dir, args.file)
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
else:
    parquet_files = glob(os.path.join(results_dir, "obfuscated_sample_*.parquet"))
    if not parquet_files:
        print("❌ No obfuscated Parquet files found in 'results/' directory.")
        sys.exit(1)
    file_path = max(parquet_files, key=os.path.getmtime)
    print(f"📂 Auto-detected latest file: {file_path}")

# Read and display
df = pd.read_parquet(file_path, engine="pyarrow")
print(df)
