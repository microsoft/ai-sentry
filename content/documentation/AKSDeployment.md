# Prerequisites

## Client Tooling:

Make sure to have current version of below tools on your client/ci/cd server which will be used to build/publish the docker images as well as execute the helm chart deployment to your kubernetes cluster.

- az cli 
- docker
- helm
- kubectl


## Kuberenetes Cluster:

Please ensure that you have the following installed in your kuberenetes cluster:

 - DAPR extension if using AKS - otherwise pull in DAPR from open source.

 ### Install DAPR Extension on AKS

```bash
az extension add --name k8s-extension
az extension update --name k8s-extension

az provider list --query "[?contains(namespace,'Microsoft.KubernetesConfiguration')]" -o table
az provider register --namespace Microsoft.KubernetesConfiguration


az k8s-extension create --cluster-type managedClusters --cluster-name anevjes-aks --resource-group aks --name dapr --extension-type Microsoft.Dapr --auto-upgrade-minor-version false

More info here: https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/
```

### Install REDIS - (if using REDIS as your PUB/SUB DAPR component)
```
az aks get-credentials --admin --name anevjes-aks --resource-group aks
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install sentry-redis bitnami/redis-cluster
export REDIS_PASSWORD=$(kubectl get secret --namespace "default" sentry-redis-redis-cluster -o jsonpath="{.data.redis-password}" | base64 --decode)

 kubectl create secret generic redis --from-literal=redis-password=$REDIS_PASSWORD -n sentry-ai

```



# Build and publish container images

Prepare the facade and worker images and push them to your image registry.

``` bash
#Browse to build directory
cd build
```

When you list source you should see the following powershell script

```bash
ls

Dockerfile.facade               Dockerfile.worker               DockerfileSummary.worker        build-ai-sentry-containers.ps1
```

Login into az cli in the terminal sessions
```
az login
```

Now Login to your target container registry - in my example this is an Azure Container Registry

```bash
az acr login -n <your-ACR-name>
```

Now run the build-ai-sentry-containers.ps1 script

```bash
build-ai-sentry-containers.ps1 -version "0.1.1" -containerRegistry "your-ACR-name"
```

You can confirm against your ACR that the images are there with correct tags.

```bash
az acr repository show-tags --name <your-ACR-name> --repository <your-image-name> --output table
```


# Deploy AI-Sentry

Now its time to kick off the Ai-Sentry deployment.

- Browse to *deploy* directory at the root of the project level

- Now browse into the *AKS* directory


Currently I have not configured an end to end helm chart so for the inital deployment please update and use the ai-sentry-deployment.yaml file.


if you crack open the ai-sentry-deployment.yaml file you will notice it is broken up into several sections:


## Create ai-sentry namespace

Create the ai-sentry namespace by running the following command:

```kubectl
kuebctl apply -f namespace.yaml
```

## Ai-Sentry deployment into namespace

```bash
kubectl apply -f ai-sentry-deployment.yaml -n ai-sentry

service/facadeapp created
service/facadeapp-headless created
ingress.networking.k8s.io/facadeapp-ingress created
statefulset.apps/facadeapp created
statefulset.apps/cosmosdbloggerw created
statefulset.apps/cosmosdb-summary-loggerw created
component.dapr.io/openaipubsub created
component.dapr.io/cosmosdb-log created
component.dapr.io/summary-log created
```

Now lets confirm the pods exist - it should look like the following:

```bash
kubectl get pods -n ai-sentry

AME                         READY   STATUS    RESTARTS   AGEaks> kubectl get pods -n ai-sentry
cosmosdb-summary-loggerw-0   2/2     Running   0          82s
cosmosdb-summary-loggerw-1   2/2     Running   0          75s
cosmosdbloggerw-0            2/2     Running   0          82s
cosmosdbloggerw-1            2/2     Running   0          75s
facadeapp-0                  2/2     Running   0          82s
```

For ease of testing and getting the intial version up and running I've used a LoadBalancer service and an external IP. You will need to change this service type to meet your Cyber/Enterprise security posture -i.e. it could become ingress on a private IP address.


