import pandas as pd

data = {
    "student_id": [1234, 5678],
    "name": ["John Smith", "Jane Doe"],
    "course": ["Software", "Data Science"],
    "cohort": ["2024-03-31", "2025-05-15"],
    "graduation_date": ["2024-03-31", "2025-05-15"],
    "email_address": ["j.smith@email.com", "jane.doe@email.com"],
}

df = pd.DataFrame(data)
df.to_parquet("sample.parquet", index=False, engine="pyarrow")
