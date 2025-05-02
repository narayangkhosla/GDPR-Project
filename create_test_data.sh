#!/bin/bash

echo "� Creating dynamic test data..."

# Generate CSV
cat > sample.csv <<EOF
student_id,name,course,cohort,graduation_date,email_address
$(python3 -c "
import random

first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fiona', 'George', 'Hannah', 'Ivan', 'Jane']
last_names = ['Smith', 'Johnson', 'Brown', 'Williams', 'Miller', 'Davis', 'Garcia', 'Martinez', 'Lee', 'Taylor']

for i in range(10):
    sid = random.randint(1000, 9999)
    first = random.choice(first_names)
    last = random.choice(last_names)
    name = f'{first} {last}'
    course = f'Course{i%3}'
    cohort = 2024 if i % 2 == 0 else 2025
    grad = f'{cohort}-0{(i%12)+1}-15'
    email = f'{first.lower()}.{last.lower()}@example.com'
    print(f'{sid},{name},{course},{cohort},{grad},{email}')
")
EOF
echo "✅ Created sample.csv"

# Generate JSON
python3 <<EOF > sample.json
import json, random

first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fiona', 'George', 'Hannah', 'Ivan', 'Jane']
last_names = ['Smith', 'Johnson', 'Brown', 'Williams', 'Miller', 'Davis', 'Garcia', 'Martinez', 'Lee', 'Taylor']

data = []
for i in range(10):
    first = random.choice(first_names)
    last = random.choice(last_names)
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}@example.com"
    record = {
        "student_id": random.randint(1000, 9999),
        "name": name,
        "course": f"Course{i%3}",
        "cohort": "2024" if i % 2 == 0 else "2025",
        "graduation_date": f"2025-0{(i%12)+1}-15",
        "email_address": email
    }
    data.append(record)

json.dump(data, open("sample.json", "w"), indent=2)
EOF
echo "✅ Created sample.json"

# Generate Parquet
python3 <<EOF
import pandas as pd, random

first_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Ethan', 'Fiona', 'George', 'Hannah', 'Ivan', 'Jane']
last_names = ['Smith', 'Johnson', 'Brown', 'Williams', 'Miller', 'Davis', 'Garcia', 'Martinez', 'Lee', 'Taylor']

data = []
for i in range(10):
    first = random.choice(first_names)
    last = random.choice(last_names)
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}@example.com"
    record = {
        "student_id": random.randint(1000, 9999),
        "name": name,
        "course": f"Course{i%3}",
        "cohort": "2024" if i % 2 == 0 else "2025",
        "graduation_date": f"2025-0{(i%12)+1}-15",
        "email_address": email
    }
    data.append(record)

df = pd.DataFrame(data)
df.to_parquet("sample.parquet", index=False, engine="pyarrow")
EOF
echo "✅ Created sample.parquet"

echo "� Test data created with random records."
