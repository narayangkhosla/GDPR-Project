#!/bin/bash

echo "� Creating dynamic test data..."

# Generate CSV
cat > sample.csv <<EOF
student_id,name,course,cohort,graduation_date,email_address
$(python3 -c "
import random
for i in range(10):
    sid = random.randint(1000, 9999)
    name = f'Name{i}'
    course = f'Course{i%3}'
    cohort = 2024 if i % 2 == 0 else 2025
    grad = f'{cohort}-0{(i%12)+1}-15'
    email = f'name{i}@example.com'
    print(f'{sid},{name},{course},{cohort},{grad},{email}')
")
EOF
echo "✅ Created sample.csv"

# Generate JSON
python3 <<EOF > sample.json
import json, random
data = [{
    "student_id": random.randint(1000, 9999),
    "name": f"Name{i}",
    "course": f"Course{i%3}",
    "cohort": "2024" if i % 2 == 0 else "2025",
    "graduation_date": f"2025-0{(i%12)+1}-15",
    "email_address": f"name{i}@example.com"
} for i in range(10)]
json.dump(data, open("sample.json", "w"), indent=2)
EOF
echo "✅ Created sample.json"

# Generate Parquet
python3 <<EOF
import pandas as pd, random
data = [{
    "student_id": random.randint(1000, 9999),
    "name": f"Name{i}",
    "course": f"Course{i%3}",
    "cohort": "2024" if i % 2 == 0 else "2025",
    "graduation_date": f"2025-0{(i%12)+1}-15",
    "email_address": f"name{i}@example.com"
} for i in range(10)]
df = pd.DataFrame(data)
df.to_parquet("sample.parquet", index=False, engine="pyarrow")
EOF
echo "✅ Created sample.parquet"

echo "� Test data created with random records."
