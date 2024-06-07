param (
    [Parameter(Mandatory=$false)]
    [string]$jsonFilePath
)

# Read the JSON file
$json = Get-Content -Raw -Path $jsonFilePath | ConvertFrom-Json -Depth 99

# Convert the JSON object to a string
$jsonString = ConvertTo-Json -InputObject $json -Compress -Depth 99
$escapedJsonString = $jsonString | ConvertTo-Json -Depth 99

# Print the escaped JSON string
Write-Output $escapedJsonString