# AKS Workload Identity setup

## Enable Workload identity against existing AKS cluster
```powershell
az aks update --resource-group "aks-devtest-rg" --name "anevjes-aks-dev" --enable-oidc-issuer --enable-workload-identity
```

## MI creation
```powershell
az account set --subscription "subscriptionID"
```

```powershell
az identity create --name "ai-sentry-be-mi" --resource-group "ai-sentry" --location "australiaeast" --subscription "879bb272-07db-4784-816a-a9fac90f49ae"
```

```bash
export USER_ASSIGNED_CLIENT_ID="$(az identity show --resource-group "ai-sentry" --name "ai-sentry-be-mi" --query 'clientId' -otsv)"
```
## Grant MI access to openAI resources

![alt text](..\images\openai_rbac.png)

and assign your newly built managed identity to above role:

![alt text](..\images\openai_rbac2.png)


## Env variables for service account in AKS

```bash
export SERVICE_ACCOUNT_NAME="default"
export SERVICE_ACCOUNT_NAMESPACE="ai-sentry"
```

## OIDC Issuer url

```bash
export AKS_OIDC_ISSUER="$(az aks show --name anevjes-aks-dev --resource-group aks-devtest-rg --query "oidcIssuerProfile.issuerUrl" -o tsv)"
```

## Create AKS Service Account

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: ${USER_ASSIGNED_CLIENT_ID}
  name: ${SERVICE_ACCOUNT_NAME}
  namespace: ${SERVICE_ACCOUNT_NAMESPACE}
EOF
```
## Establish federated identity credential trust

```powershell
az identity federated-credential create --name ai-sentry-be-fed --identity-name ai-sentry-be-mi --resource-group ai-sentry --issuer ${AKS_OIDC_ISSUER} --subject system:serviceaccount:${SERVICE_ACCOUNT_NAMESPACE}:${SERVICE_ACCOUNT_NAME} --audience api://AzureADTokenExchange
```
