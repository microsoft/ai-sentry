Each pool is represented as an object within the "pools" array. Each pool object has the following properties:

- name: The name of the pool.
- description: A description of the pool.
- endpoints: An array of endpoint objects that the pool can connect to.
Each endpoint object has the following properties:

- url: The URL of the OpenAI instance. You're expected to replace <your-open-ai-instance> with the actual instance name. You need to append
- api-key: The API key for accessing the OpenAI instance. You're expected to replace your-api-key with the actual API key. 

Please note: We also support JWT auth to backend openAI instances. If you simply set "api-Key": null within the property bags inside the facade layer config; you will leverage aks workload identity to connect to openAi backends - however you will need worklaod identity federated out with managed identity stood up with your AKS cluster - and ofcourse grant the RBAC to the managed identity across all the required openAI instances in the backend.