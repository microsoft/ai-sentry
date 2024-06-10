Each pool is represented as an object within the "pools" array. Each pool object has the following properties:

- name: The name of the pool.
- description: A description of the pool.
- endpoints: An array of endpoint objects that the pool can connect to.
Each endpoint object has the following properties:

- url: The URL of the OpenAI instance. You're expected to replace <your-open-ai-instance> with the actual instance name. You need to append
- api-key: The API key for accessing the OpenAI instance. You're expected to replace your-api-key with the actual API key.