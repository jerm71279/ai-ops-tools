// Azure Container Apps Bicep Template for Secondbrain
// Deploy with: az deployment group create --resource-group <rg> --template-file containerapp.bicep

@description('Location for all resources')
param location string = resourceGroup().location

@description('Container registry login server')
param containerRegistryServer string

@description('Container registry username')
param containerRegistryUsername string

@secure()
@description('Container registry password')
param containerRegistryPassword string

@secure()
@description('Azure Tenant ID')
param azureTenantId string

@secure()
@description('Azure Client ID')
param azureClientId string

@secure()
@description('Azure Client Secret')
param azureClientSecret string

@secure()
@description('Anthropic API Key')
param anthropicApiKey string

// Container Apps Environment
resource containerAppEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: 'secondbrain-env'
  location: location
  properties: {
    zoneRedundant: false
  }
}

// Shared secrets
var sharedSecrets = [
  {
    name: 'azure-tenant-id'
    value: azureTenantId
  }
  {
    name: 'azure-client-id'
    value: azureClientId
  }
  {
    name: 'azure-client-secret'
    value: azureClientSecret
  }
  {
    name: 'anthropic-api-key'
    value: anthropicApiKey
  }
  {
    name: 'registry-password'
    value: containerRegistryPassword
  }
]

// Data Processing Container App
resource dataProcessingApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'sb-data-processing'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
      }
      registries: [
        {
          server: containerRegistryServer
          username: containerRegistryUsername
          passwordSecretRef: 'registry-password'
        }
      ]
      secrets: sharedSecrets
    }
    template: {
      containers: [
        {
          name: 'data-processing'
          image: '${containerRegistryServer}/secondbrain/data-processing:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'AZURE_TENANT_ID', secretRef: 'azure-tenant-id' }
            { name: 'AZURE_CLIENT_ID', secretRef: 'azure-client-id' }
            { name: 'AZURE_CLIENT_SECRET', secretRef: 'azure-client-secret' }
            { name: 'ANTHROPIC_API_KEY', secretRef: 'anthropic-api-key' }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

// RAG Engine Container App
resource ragEngineApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'sb-rag-engine'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
      }
      registries: [
        {
          server: containerRegistryServer
          username: containerRegistryUsername
          passwordSecretRef: 'registry-password'
        }
      ]
      secrets: sharedSecrets
    }
    template: {
      containers: [
        {
          name: 'rag-engine'
          image: '${containerRegistryServer}/secondbrain/rag-engine:latest'
          resources: {
            cpu: json('1')
            memory: '2Gi'
          }
          env: [
            { name: 'ANTHROPIC_API_KEY', secretRef: 'anthropic-api-key' }
          ]
        }
      ]
      scale: {
        minReplicas: 1  // Keep warm for fast queries
        maxReplicas: 5
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '5'
              }
            }
          }
        ]
      }
    }
  }
}

// Engineering API Container App
resource engineeringApiApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: 'sb-engineering-api'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
      }
      registries: [
        {
          server: containerRegistryServer
          username: containerRegistryUsername
          passwordSecretRef: 'registry-password'
        }
      ]
      secrets: sharedSecrets
    }
    template: {
      containers: [
        {
          name: 'engineering-api'
          image: '${containerRegistryServer}/secondbrain/engineering-api:latest'
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
          env: [
            { name: 'AZURE_TENANT_ID', secretRef: 'azure-tenant-id' }
            { name: 'AZURE_CLIENT_ID', secretRef: 'azure-client-id' }
            { name: 'AZURE_CLIENT_SECRET', secretRef: 'azure-client-secret' }
            { name: 'ANTHROPIC_API_KEY', secretRef: 'anthropic-api-key' }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 3
        rules: [
          {
            name: 'http-scaling'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

// Outputs
output dataProcessingUrl string = 'https://${dataProcessingApp.properties.configuration.ingress.fqdn}'
output ragEngineUrl string = 'https://${ragEngineApp.properties.configuration.ingress.fqdn}'
output engineeringApiUrl string = 'https://${engineeringApiApp.properties.configuration.ingress.fqdn}'
