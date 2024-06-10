// -- PARAMETERS -- 
@description('Required - Environment Type')
@allowed([
  'dev'
  'test'
  'prod'
] )
param environmentType string = 'dev'

@description('Required - tags')
param tags object = {
  Environment: environmentType
  Role: 'ai-sentry'
}

@description('Required - AKS name')
param aksName string

param aksPrimaryAgentPoolProfile array = [
  {
    count: 3
    mode: 'System'
    name: 'systempool'
    vmSize: 'Standard_DS2_v2'
  }
]

@description('Required - Azure Container Registry Name')
param containerRegistryName string

@description('Required - Cosmos DB Name')
param cosmosDbName string

@description('Optional. List of Cosmos DB capabilities for the account. Some capabilities are not compatible with each other.')
@allowed([
  'EnableCassandra'
  'EnableTable'
  'EnableGremlin'
  'EnableMongo'
  'DisableRateLimitingResponses'
  'EnableServerless'
])
param capabilitiesToAdd string[] = [
  'EnableServerless'
  'EnableGremlin'
  'DisableRateLimitingResponses'
]

@description('Required - Cosmos data locations')
param cosmosDbLocations object[] = [
  {
    failoverPriority: 0
    isZoneRedundant: false
    locationName: resourceGroup().location // where the data is located
  }
]

@description('Required - Open AI Name')
param openAiName string = 'ai-sentry-openai'

@description('Required - Open AI Location')
param openAiLocation string = 'australiaeast'

@description('Required - Open AI SKU')
param openAiSku string = 'S0'

@description('Required - OpenAI Model Config')
param modelDeploymentConfig array = [
  {
    name: 'text-embedding-ada-002'
    version: '2'
    capacity: 1
    scaleType: 'Standard'
    raiPolicyName: ''
  }
  {
    name: 'gpt-35-turbo'
    version: '0613'
    capacity: 1
    scaleType: 'Standard'
    raiPolicyName: ''
  }
]

@description('Required - API Management Name')
param apimName string = 'ai-sentry-apim001'

// @description('The name of the virtual network subnet to be associated with the API Management service.')
// param apimSubnetName string = 'apim-subnet'

// @description('The name of the public ip to be associated with the API Management service.')
// param apimPublicIp string = 'apim-pip-001'

@description('The name of the publisher email to be associated with the API Management service.')
param apimPublisherEmail string = 'publisher@email.com'

@description('The name of the publisher name to be associated with the API Management service.')
param apimPublisherName string = 'APIM Publisher'

@description('The sku to be associated with the API Management service.')
param apimSku string = 'Developer'

// @description('The desired Availability Zones for the API Management service. e.g. [1,2] for deployment in Availability Zones 1 and 2')
// param apimZones []?

// @description('The desired custom hostnames for the API Management service endpoints')
// param apimHostnameConfigurations object[] = []


// -- RESOURCE CREATION ORCHESTRATOR -- 

// 1. Create Azure Kubernetes Managed Cluster with defaults via AVM module
module managedCluster 'br/public:avm/res/container-service/managed-cluster:0.1.7' = {
  name: 'managedClusterDeployment'
  params: {
    // Required parameters
    name: aksName
    primaryAgentPoolProfile: aksPrimaryAgentPoolProfile
    // Non-required parameters
    location: resourceGroup().location
    enableContainerInsights: false
    managedIdentities: {
      systemAssigned: true
    }
  }
}

// 2. Create Container Registry resources
module registry 'br/public:avm/res/container-registry/registry:0.2.0' = {
  name: '${uniqueString(deployment().name)}-containerRegistryCreation'
  params: {
    // Required parameters
    name: containerRegistryName
    // Non-required parameters
    publicNetworkAccess: 'Enabled'
    acrAdminUserEnabled: false
    zoneRedundancy: 'Disabled'
    managedIdentities: {
      systemAssigned: true
    }
    acrSku: 'Standard'
    location: resourceGroup().location
    tags: tags
  }
}

// 3. Create CosmosDB resources
module databaseAccount 'br/public:avm/res/document-db/database-account:0.5.4' = {
  name: '${uniqueString(deployment().name)}-cosmosDbCreation'
  params: {
    // Required parameters
    locations: cosmosDbLocations
    name: cosmosDbName
    // Non-required parameters
    capabilitiesToAdd: capabilitiesToAdd
    managedIdentities: {
      systemAssigned: true
    }
    location: resourceGroup().location
    tags: tags
  }
}

// 4. Create OpenAI resources
module openAI 'open-ai/main.bicep' = {
  name: '${uniqueString(deployment().name)}-openAICreation'
  params:{
    // vnetName:vnetName
    // peSubnetName:peSubnetName
    name: openAiName
    location: openAiLocation
    sku: openAiSku
    managedIdentities: {
      systemAssigned: true
    }
    tags: tags
    publicNetworkAccess: 'Enabled'
    deploymentConfig: modelDeploymentConfig
    // workspaceId:logAnalytics.outputs.logAnalyticsWorkspaceId
  }
}

// 5. Create API Management Service resources
module apimService 'br/public:avm/res/api-management/service:0.1.7' = {
  name: '${uniqueString(deployment().name)}-ApiManagementCreation'
  params: {
    // Required parameters
    name: apimName
    sku: apimSku
    // apimPublicIpName: apimPublicIp
    // virtualNetworkType: 'External'
    // subnetResourceId:  '/subscriptions/${vnetSubscriptionId}/resourceGroups/${vnetResourceGroupName}/providers/Microsoft.Network/virtualNetworks/${vnetName}/subnets/${apimSubnetName}'
    publisherEmail: apimPublisherEmail
    publisherName: apimPublisherName
    managedIdentities: {
      systemAssigned: true
    }
    // Non-required parameters
    // hostnameConfigurations: apimHostnameConfigurations
    // zones: apimZones
    location: resourceGroup().location
    minApiVersion: '2021-08-01'
    tags: tags
  }
}

