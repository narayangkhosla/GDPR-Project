# This will scan all test_*.py files in the tests/ folder and extract function names that start with test_.
# Groups them by file

Get-ChildItem -Recurse -Path ./tests -Filter "test_*.py" | 
ForEach-Object {
    $file = $_.FullName
    $functions = Select-String -Path $file -Pattern 'def (test_[a-zA-Z0-9_]+)\s*\(' | ForEach-Object {
        $_.Matches.Groups[1].Value
    }
    [PSCustomObject]@{
        FileName = $_.Name
        Tests    = $functions
    }
} | Group-Object -Property FileName | ForEach-Object {
    $output = "`n# $($_.Name)`n"
    $output += ($_.Group.Tests | Sort-Object | ForEach-Object { "- $_" }) -join "`n"
    $output
} | Out-File test_names_grouped.txt -Encoding UTF8
