param(
    [string]$version = "0.1.1",
    [string]$containerRegistry = "ariantestacr001.azurecr.io"
)
#Uncomment first line for very first time to set to the right acr context
# az acr login --name ariantestacr001
Write-Host "Building AI-Sentry Facade:$version"
docker build --platform linux/amd64 -t ai-sentry-facadeapp:$version -f Dockerfile.facade ../aisentry/
docker tag ai-sentry-facadeapp:$version $containerRegistry/ai-sentry-facadeapp:$version
docker push $containerRegistry/ai-sentry-facadeapp:$version


Write-Host "Building summary logger worker:$version"
docker build --platform linux/amd64 -t ai-sentry-summary-logger:$version -f DockerfileSummary.worker ../aisentry/
docker tag ai-sentry-summary-logger:$version $containerRegistry/ai-sentry-summary-logger:$version
docker push $containerRegistry/ai-sentry-summary-logger:$version

Write-Host "Building cosmosdb logger worker:$version"
docker build --platform linux/amd64 -t ai-sentry-cosmosdblogger:$version -f Dockerfile.worker ../aisentry/
docker tag ai-sentry-cosmosdblogger:$version $containerRegistry/ai-sentry-cosmosdblogger:$version
docker push $containerRegistry/ai-sentry-cosmosdblogger:$version