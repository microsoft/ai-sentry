# Summary Logging Schema


| Key            | Description                                         |
| -------------- | --------------------------------------------------- |
| `id`           | Unique identifier for the chat completion           |
| `LogId`        | Identifier for the log entry                        |
| `model`        | Model used for the AI operation                     |
| `timestamp`    | Time when the log was created                       |
| `ProductId`    | Identifier for the product                          |
| `promptTokens` | Number of tokens used in the prompt                 |
| `responseTokens` | Number of tokens used in the response            |
| `totalTokens`  | Total number of tokens used (prompt + response)     |
| `month_year`   | Month and year when the log was created             |
| `_rid`         | Resource ID in Azure Cosmos DB                      |
| `_self`        | Self-link in Azure Cosmos DB                        |
| `_etag`        | Entity tag used for optimistic concurrency control  |
| `_attachments` | Link to attachments associated with the document    |
| `_ts`          | Timestamp of the last update operation on the document |


## Example JSON

```json
{
    "id": "chatcmpl-9XKn2H3CSlg91b6b3OuQBj6PdmVje",
    "LogId": "gpt-35-turbo_Product13_06_2024",
    "model": "gpt-35-turbo",
    "timestamp": "2024-06-07T03:42:59.400583+00:00",
    "ProductId": "Product13",
    "promptTokens": 42,
    "responseTokens": 645,
    "totalTokens": 687,
    "month_year": "06_2024",
    "_rid": "SxcAAOBkD+gIAAAAAAAAAA==",
    "_self": "dbs/SxcAAA==/colls/SxcAAOBkD+g=/docs/SxcAAOBkD+gIAAAAAAAAAA==/",
    "_etag": "\"a400f2ed-0000-1a00-0000-666281c30000\"",
    "_attachments": "attachments/",
    "_ts": 1717731779
}
```