# AKS Deployment



![AKS view](/content/images/AI-Sentry-AKS-view.drawio.png)


# Prerequisites

## Setup infrastructure


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

Login into az cli in the terminal session
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


If you crack open the ai-sentry-deployment.yaml file you will notice it is broken up into several sections:

1. **Service**: Two services are defined, `facadeapp` and `facadeapp-headless`. The `facadeapp` service is a LoadBalancer type, which exposes the `facadeapp` to network traffic. The `facadeapp-headless` service is a headless service (since `clusterIP` is set to `None`), used to expose pods directly without a load balancer. Both services select pods with the label `app: facadeapp` and expose the `facadeapp-http` port of those pods on their own port 80.

2. **Ingress**: This manages external access to the services in a cluster, typically HTTP. The Ingress `facadeapp-ingress` is routing traffic from the root path ("/") to the `facadeapp` service on port 80. The annotation `nginx.ingress.kubernetes.io/rewrite-target: /` indicates that the path in the request URL from the client is rewritten to "/" regardless of what the original path is.

3. **StatefulSet**: Three StatefulSets are defined for `facadeapp`, `cosmosdbloggerw`, and `cosmosdb-summary-loggerw`. StatefulSets are used for deploying, scaling, and managing stateful applications. Each StatefulSet has its own number of replicas, selectors, and container specifications. The `facadeapp` StatefulSet has Dapr annotations enabled, which means it's using DAPR for distributed application runtime.

4. **Component**: Three DAPR components are defined for `openaipubsub`, `cosmosdb-log`, and `summary-log`. These components are used for pub-sub messaging with Redis, and bindings with Azure Cosmos DB for logging and summary logging. The `openaipubsub` component is a Redis-based pub-sub component. The `cosmosdb-log` and `summary-log` components are bindings to Azure Cosmos DB for logging purposes.

5. **Images**: The images for the containers in the StatefulSets are pulled from a private Azure Container Registry (ACR) as indicated by the `youracr.azurecr.io` prefix in the image names.

6. **Environment Variables**: Various environment variables are set in the containers, including AI-SENTRY-ENDPOINT-CONFIG, LOG-LEVEL, AI-SENTRY-LANGUAGE-ENDPOINT, and AI-SENTRY-LANGUAGE-KEY. See [here](/content/documentation/ai-sentry-config.json) for example AI-SENTRY-ENDPOINT-CONFIG. You can leverage the following [script](scripts/create-escaped-json.ps1) to help you generate JSON escaped string of this JSON.

7. **Probes**: Liveness probes are defined for the `facadeapp` container to check the health of the application. If the application fails the liveness check, Kubernetes will restart the container.

8. **Commented Code**: There are commented sections for an Event Hub component for pub sub Dapr annotations. These can be uncommented and filled in as needed for additional functionality.


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


