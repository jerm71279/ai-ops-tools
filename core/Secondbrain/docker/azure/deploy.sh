#!/bin/bash
# Deploy Secondbrain containers to Azure Container Apps

set -e

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-secondbrain-rg}"
LOCATION="${LOCATION:-eastus}"
ACR_NAME="${ACR_NAME:-secondbrainacr}"

echo "=== Secondbrain Azure Container Apps Deployment ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location: $LOCATION"
echo "Container Registry: $ACR_NAME"
echo ""

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "Please login to Azure first: az login"
    exit 1
fi

# Create resource group if it doesn't exist
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# Create Azure Container Registry if it doesn't exist
echo "Creating container registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --output none || true

# Get ACR credentials
ACR_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)

echo "ACR Server: $ACR_SERVER"

# Login to ACR
echo "Logging into container registry..."
az acr login --name $ACR_NAME

# Build and push images
echo ""
echo "Building and pushing container images..."

cd "$(dirname "$0")/../.."

# Build each container
for service in data-processing rag-engine engineering-api call-flow agents; do
    echo "Building $service..."
    docker build -t $ACR_SERVER/secondbrain/$service:latest -f docker/$service/Dockerfile .
    docker push $ACR_SERVER/secondbrain/$service:latest
done

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Deploy using Bicep
echo ""
echo "Deploying to Azure Container Apps..."
az deployment group create \
    --resource-group $RESOURCE_GROUP \
    --template-file docker/azure/containerapp.bicep \
    --parameters \
        containerRegistryServer=$ACR_SERVER \
        containerRegistryUsername=$ACR_USERNAME \
        containerRegistryPassword=$ACR_PASSWORD \
        azureTenantId=$AZURE_TENANT_ID \
        azureClientId=$AZURE_CLIENT_ID \
        azureClientSecret=$AZURE_CLIENT_SECRET \
        anthropicApiKey=$ANTHROPIC_API_KEY

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "Container App URLs:"
az containerapp list --resource-group $RESOURCE_GROUP --query "[].{Name:name, URL:properties.configuration.ingress.fqdn}" -o table
