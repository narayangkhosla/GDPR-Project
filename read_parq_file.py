# import pandas as pd

# df = pd.read_parquet("obfuscated_sample.parquet", engine="pyarrow")
# print(df)
import pandas as pd
import argparse
import os
from glob import glob
import sys

# Setup CLI argument
parser = argparse.ArgumentParser(description="Read obfuscated Parquet output.")
parser.add_argument(
    "--file",
    help="Path to the obfuscated Parquet file. If not provided,"
    "the latest matching file from 'results/' will be used.",
)

args = parser.parse_args()

# Determine file to use
if args.file:
    file_path = args.file
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
else:
    parquet_files = glob("results/obfuscated_sample_*.parquet")
    if not parquet_files:
        print("❌ No obfuscated Parquet files found in 'results/' directory.")
        sys.exit(1)
    file_path = max(parquet_files, key=os.path.getmtime)
    print(f"� Auto-detected latest file: {file_path}")

# Read and display
df = pd.read_parquet(file_path, engine="pyarrow")
print(df)
