$envFile = Get-Content -Path .\..\.env

# Loop through each line in the file
foreach ($line in $envFile) {
    # Split the line into name and value
    $parts = $line -split '=', 2

    # Set the environment variable
    [Environment]::SetEnvironmentVariable($parts[0], $parts[1], 'User')
}