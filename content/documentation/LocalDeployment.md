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
