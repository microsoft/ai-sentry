param([Parameter(mandatory=$true, HelpMessage="Subscirption ID")]
[string]
$subscriptionId,    

[Parameter(mandatory=$true, HelpMessage="Resource group name")]
[string]
$resourceGroupName,

[Parameter(mandatory=$true, HelpMessage="Location of resource group")]
[string]
$location)

$ProgressPreference = "SilentlyContinue"

# Login to Azure
#az login
#Connect-AzAccount
Write-Host "Setting context to subscriptionId:  $($subscriptionId)..."
az account set --subscription $subscriptionId

Write-Host "Deploying AI Sentry resources..."

# Check if the resource group exists
$resourceGroupExists = az group exists --name $resourceGroupName

if ($resourceGroupExists -eq 'false') {
    # Create the resource group
    az group create --name $resourceGroupName --location $location
}

$deploymentName = "deployment-" + (Get-Date -Format "yyyyMMddHHmmss")

az deployment group create --resource-group $resourceGroupName --template-file ./main.bicep --parameters ./main.param.json -n $deploymentName

Write-Host "Deployment complete."