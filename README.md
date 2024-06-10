# AI-Sentry Facade


![AI-Sentry-features image](/content/images/AI-Sentry-features.png)

*Ai-Sentry* is transparent python + DAPR based pluggable Generative AI Facade layer, designed to support the following features for large enterprises developing and operating Generative AI solutions:

- Cross charge back on token usage across different openAI consumers
- Request/Response async based logging with ability to toggle PII stripping of information. This level of logging is useful for many things such as legal compliance as well as assessing and replaying back request/responses against newer models to help you deal with model upgrades without affecting your existing users.
- Smarter load balancing by taking into account Azure openAI's response header load metrics and pooling of multi backends with same model capabilities
- Support streaming and non streaming responses (including logging of these)
- Extensibility of custom adapters to help you deal with SDK / API deprecations from client side - so you can provide backwards compatibility if needed.


AI-Sentry is not designed to replace existing API Gateway solutions such as Azure APIM - rather it is designed to sit between API Gateway and the openAI endpoints - providing ultimate control for your openAI solutions.

We try to perform heavy processing outside of the direct HTTP calls pipeline to minimise latency to the consumers and rely on DAPR side cars and Pub / Sub patterns to perform the work asynchronously.

Because AI-Sentry uses DAPR; the technology choices for log persistence, and message brokers is swappable out via DAPR's native [components](https://docs.dapr.io/concepts/components-concept/). Our example uses REDIS and Event Hubs as the message broker for PUB/SUB, and CosmosDB as the Log persistence store.

## High Level Design

![ISentryHighLevel image](/content/images/AI-Sentry-HighLevel.drawio.png)



## Backend Configuration

The following environment variables need to exist. How you feed them in is up to you - i.e. Kubernetes secrets, configmaps, etc...

| Name | Value |
| -------- | -------- |
|  AI-SENTRY-ENDPOINT-CONFIG  | Example JSON value is located [here](/content/documentation/ai-sentry-config.json). This is used to map openai endpoints / deployments - so that when we are load balancing we are hitting group of same openAI models from the pool.  Make sure to include /openai in your endpoint url configuration. You can leverage the following [script](scripts/create-escaped-json.ps1) to help you generate JSON escaped string of this JSON.|
|AI-SENTRY-LANGUAGE-KEY| your Congnitive Services General API Key|
|AI-SENTRY-LANGUAGE-ENDPOINT| your language text anlaytics or general service endpoint url|


## Consumer Configuration

Whatever you front AI-Sentry with e.g. Azure APIM, some other API gateway technology - you will need to supply some mandatory HTTP headers.

|HTTP HEADER NAME| HTTP HEADER VALUE|
| -------- | --------|
|ai-sentry-consumer| this can be any string - it is used to represent a consumer or a product that uses generative ai backend. We use this for logging purposes|
| ai-sentry-log-level | This toggles logging level for the actual consumer. Accepted values are: COMPLETE, PII_STRIPPING_ENABLED or DISABLED |
|ai-sentry-backend-pool| Provide the name of the pool from the AI-SENTRY-ENDPOINT-CONFIG configuration. E.g. Pool1

## Getting started

For more information on setting up AI-Sentry in your environment please follow the following detailed sections.

- [Setting up CosmosDB dbs/table](/content/documentation/CosmosDBSetup.md)

- [Setting up AI-Sentry on AKS](/content/documentation/AKSDeployment.md)

- [CosmosDB Logging Schema](/content/documentation/ComsosDB-LoggingSchema.md)

- [Summary Logging Schema](/content/documentation/SummaryLog-schema.md)



## Running locally
```
# Need to move this logic into dockerfile scripts for workers using cognitive services
openssl x509 -in "/Users/ariannevjestic/Downloads/_.cognitive.microsoft.com.cer" -out "/Users/ariannevjestic/Downloads/cogcerts/_.cognitive.microsoft.com.pem" -outform PEM
openssl x509 -in "/Users/ariannevjestic/Downloads/2.cer" -out "/Users/ariannevjestic/Downloads/cogcerts/DigiCert_SHA2 Secure_ServerCA.pem" -outform PEM
openssl x509 -in "/Users/ariannevjestic/Downloads/1.cer" -out "/Users/ariannevjestic/Downloads/1.pem" -outform PEM
cat _.cognitive.microsoft.com.pem middle.pem cDigiCertGlobalRootCA.pem > combined_cert.pem
openssl x509 -outform der -in combined_cert -out combined-cert.crt

REQUESTS_CA_BUNDLE=/Users/ariannevjestic/Downloads/cogservices.pem

#check for python env variable

cd ./aoaifacadeapp
dapr run -f dapr.yaml
```


## Running individual apps:

### FacadeApp API:
```
dapr run --app-id facade-entry --app-port 6124 python3 aoaifacadeapp.py --resources-path components --log-level info
```

### CosmosDB Worker:

```
dapr run --app-id oai-cosmosdb-logging-processor --app-port 3001 python3 ./workers/CosmosDBLogging/app.py --resources-path components --log-level info
```






## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
