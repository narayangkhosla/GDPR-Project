import pandas as pd

df = pd.read_parquet("obfuscated_sample.parquet", engine="pyarrow")
print(df)
