# ✅ Creates randomized student data
# ✅ Outputs to CSV, JSON, and Parquet
# ✅ Works with your existing workflow and test cases
# ✅ Keeps the PII structure the same (name, email_address) so your obfuscator continues to work

# Load Python code from PowerShell for creating dynamic test data

# Python code to generate randomized CSV, JSON, and Parquet
$pythonCode = @'
import pandas as pd
import random
import json

first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah"]
last_names = ["Smith", "Doe", "Johnson", "Williams", "Brown", "Prince", "Hunt", "Clark", "Nguyen", "Taylor"]
courses = ["Software", "Data Science", "Cyber Security", "AI", "Analytics", "Engineering", "Cloud Computing"]
cohorts = ["2024", "2025"]
graduation_dates = ["2024-03-31", "2025-05-15", "2024-07-20", "2025-06-10", "2024-09-05", "2025-12-01", "2024-11-22"]

students = []
for i in range(10):
    first = random.choice(first_names)
    last = random.choice(last_names)
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}@test.com"
    student = {
        "student_id": random.randint(1000, 9999),
        "name": name,
        "course": random.choice(courses),
        "cohort": random.choice(cohorts),
        "graduation_date": random.choice(graduation_dates),
        "email_address": email
    }
    students.append(student)

# Save CSV
df = pd.DataFrame(students)
df.to_csv("sample.csv", index=False)

# Save JSON
with open("sample.json", "w", encoding="utf-8") as f:
    json.dump(students, f, indent=2)

# Save Parquet
df.to_parquet("sample.parquet", index=False, engine="pyarrow")
'@

# Save Python script
$pythonCode | Set-Content -Path "create_test_data.py" -Encoding utf8

# Run it
python create_test_data.py

# Clean up
Remove-Item "create_test_data.py" -Force

Write-Host "`n✅ Created randomized sample.csv, sample.json, sample.parquet"
Write-Host "=== Test data is ready! ==="

