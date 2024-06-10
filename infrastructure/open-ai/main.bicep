// Parameters

@description('Specifies the name of the vnet to injeciton private endpoint to')
param vnetName string?

@description('private endpoint for openAI isntances')
param peSubnetName string?

param name string
param location string
param sku string
param customSubDomainName string?

@description('Optional. The managed identity definition for this resource.')
param managedIdentities managedIdentitiesType

@description('Specifies the openAI model deployment config required')
param deploymentConfig array


@description('Specifies the resource tags.')
param tags object


@description('Specifies whether or not public endpoint access is allowed for this account..')
@allowed([
  'Enabled'
  'Disabled'
])
param publicNetworkAccess string = 'Enabled'


@description('Specifies the workspace id of the Log Analytics used to monitor the Application Gateway.')
param workspaceId string?

// Variables
var diagnosticSettingsName = 'diagnosticSettings'
var openAiLogCategories = [
  'Audit'
  'RequestResponse'
  'Trace'
]
var openAiMetricCategories = [
  'AllMetrics'
]
var openAiLogs = [for category in openAiLogCategories: {
  category: category
  enabled: true
}]
var openAiMetrics = [for category in openAiMetricCategories: {
  category: category
  enabled: true
}]

var formattedUserAssignedIdentities = reduce(
  map((managedIdentities.?userAssignedResourceIds ?? []), (id) => { '${id}': {} }),
  {},
  (cur, next) => union(cur, next)
) // Converts the flat array to an object like { '${id1}': {}, '${id2}': {} }

var identity = !empty(managedIdentities)
  ? {
      type: (managedIdentities.?systemAssigned ?? false)
        ? (!empty(managedIdentities.?userAssignedResourceIds ?? {}) ? 'SystemAssigned,UserAssigned' : 'SystemAssigned')
        : (!empty(managedIdentities.?userAssignedResourceIds ?? {}) ? 'UserAssigned' : null)
      userAssignedIdentities: !empty(formattedUserAssignedIdentities) ? formattedUserAssignedIdentities : null
    }
  : null

// Resources

resource openAiDeployment 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  sku: {
    name: sku
  }
  kind: 'OpenAI'
  identity: identity
  tags: tags
  properties: {
    customSubDomainName: customSubDomainName
    publicNetworkAccess: publicNetworkAccess
  }
}

// module privateendpoints '../core/network/privateendpoint/main.bicep' = [for (openAi, i) in openAIConfig: {
//   name: 'openAI-privateendpoint-${i}'
//   params:{
//     privateEndpointName:'openAi-${openAi.name}-pe'
//     location:resourceGroup().location
//     subnetName:peSubnetName
//     vnetName:vnetName
//     privateLinkServiceId:openAiDeployment[i].id
//     groupIds:['account']
//   }
//   dependsOn:[
//     openAiDeployment
//   ] 
// }]

// What we want to do is iterate through all the models
// And deploy
// modelDeployments is an array of objects that contain the model name and version
@batchSize(1)
resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for deployment in deploymentConfig: {
  parent: openAiDeployment
  sku: {
    capacity: deployment.capacity
    name: deployment.sku
  }
  name: deployment.name
  properties: {
    model: {
      format: 'OpenAI'
      name: deployment.name
      version: deployment.version
    }
    raiPolicyName: contains(deployment, 'raiPolicyName') ? deployment.raiPolicyName : null
  }
}]

// @batchSize(1)
// resource model 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = [for (openAi, i) in openAIConfig: {
//   name: openAi.Name
//   parent: openAiDeployment[i]
//   sku: {
//     name:'Standard'
//     capacity: openAi.ModelDeployments[i].capacity
//   }
//   properties: {
//     model: {
//       format: 'OpenAI'
//       name: openAi.ModelDeployments[i].name
//       version: openAi.ModelDeployments[i].version
//     }
//     //raiPolicyName: openAi.ModelDeployments.raiPolicyName
//   }
// }]


// resource openAiDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = [for (openAi, i) in openAIConfig: {
//   name: diagnosticSettingsName
//   scope: openAiDeployment[i]
//   properties: {
//     workspaceId: workspaceId
//     logs: openAiLogs
//     metrics: openAiMetrics
//   }
// }]

// Outputs
output deployedopenAIAccount object = {
  openAIName: name
}


// =============== //
//   Definitions   //
// =============== //

type managedIdentitiesType = {
  @description('Optional. Enables system assigned managed identity on the resource.')
  systemAssigned: bool?

  @description('Optional. The resource ID(s) to assign to the resource.')
  userAssignedResourceIds: string[]?
}?
