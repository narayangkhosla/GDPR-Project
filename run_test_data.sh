#!/bin/bash

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=eu-west-2
export AWS_ENDPOINT_URL=http://localhost:4566

bucket="test-bucket"
timestamp=$(date +"%Y%m%d_%H%M%S")
output_prefix="obfuscated_sample_$timestamp"
results_dir="results"
fields="name email_address"
extensions=("csv" "json" "parquet")

mkdir -p $results_dir
rm -f $results_dir/*

echo "🪣 Creating bucket if it doesn't exist..."
awslocal s3 mb s3://$bucket 2>/dev/null

echo "⬆️ Uploading test files to S3..."
awslocal s3 cp sample.csv s3://$bucket/sample.csv
awslocal s3 cp sample.json s3://$bucket/sample.json
awslocal s3 cp sample.parquet s3://$bucket/sample.parquet

# Run CLI for each format
for ext in "${extensions[@]}"; do
    input_file="sample.$ext"
    output_file="$results_dir/${output_prefix}.$ext"
    echo "🚀 Running CLI for $ext..."
    if python3 src/main.py --s3 s3://$bucket/$input_file --fields $fields --output $output_file; then
        if [[ -f "$output_file" ]]; then
            echo "✅ $ext written to $output_file"
        else
            echo "⚠️ No $ext output file was written — likely no matching fields"
        fi
    else
        echo "❌ Failed to obfuscate $ext"
    fi
done

# Summary block
echo ""
echo "========= SUMMARY =========="
for ext in "${extensions[@]}"; do
    output_file="$results_dir/${output_prefix}.$ext"
    if [[ -f "$output_file" ]]; then
        echo "✅ The obfuscated $ext data has been written to $output_file"
    else
        echo "⚠️ No $ext output file was written (possible error during obfuscation)"
    fi
done

echo ""
echo "📌 NOTE: If no fields were obfuscated, it's likely that the specified field names did not match the data headers."
echo "Please double-check the field names passed to '--fields' in the CLI."
