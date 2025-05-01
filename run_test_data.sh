#!/bin/bash

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=eu-west-2
export AWS_ENDPOINT_URL=http://localhost:4566

bucket="test-bucket"
timestamp=$(date +"%Y%m%d_%H%M%S")
output_prefix="obfuscated_sample_$timestamp"
extensions=("csv" "json" "parquet")
results_dir="results"

# the obfuscated files will be in the 'results' folder (created above)
# Ensure results directory exists and clean it
mkdir -p $results_dir
rm -f $results_dir/*

echo "� Creating bucket if it doesn't exist..."
awslocal s3 mb s3://$bucket 2>/dev/null

echo "⬆️ Uploading test files..."
awslocal s3 cp sample.csv s3://$bucket/sample.csv
awslocal s3 cp sample.json s3://$bucket/sample.json
awslocal s3 cp sample.parquet s3://$bucket/sample.parquet

echo "� Running CLI for CSV..."
if python3 src/main.py --s3 s3://$bucket/sample.csv --fields name email_address --output $results_dir/$output_prefix.csv; then
    echo "✅ CSV written to $output_prefix.csv"
else
    echo "❌ Failed to obfuscate CSV"
fi

echo "� Running CLI for JSON..."
if python3 src/main.py --s3 s3://$bucket/sample.json --fields name email_address --output $results_dir/$output_prefix.json; then
    echo "✅ JSON written to $output_prefix.json"
else
    echo "❌ Failed to obfuscate JSON"
fi

echo "� Running CLI for Parquet..."
if python3 src/main.py --s3 s3://$bucket/sample.parquet --fields name email_address --output $results_dir/$output_prefix.parquet; then
    echo "✅ Parquet written to $output_prefix.parquet"
else
    echo "❌ Failed to obfuscate PARQUET"
fi

echo "===========================================" 
for ext in "${extensions[@]}"; do 
    echo "The obfuscated $ext data has been written to ${output_prefix}.${ext}" 
done

echo "✅ Process Complete."
