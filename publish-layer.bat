@echo off
.\.venv\Scripts\awslocal.bat lambda publish-layer-version ^
  --layer-name pandas-layer ^
  --region eu-west-2 ^
  --zip-file fileb://pandas-layer.zip ^
  --compatible-runtimes python3.11 python3.12 ^
  --description "Pandas + PyArrow Layer for GDPR Obfuscator (multi-runtime)"
