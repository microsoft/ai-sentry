# Logging Schema


| Property | Description |
| --- | --- |
| `date_time_utc` | The date and time in UTC when the event occurred. |
| `is_Streaming` | A boolean indicating whether the event is streaming or not. |
| `headers` | An object containing various headers related to the event. |
| `params` | An object containing parameters related to the event. |
| `request_body` | An object containing the request body of the event. |
| `response_body` | An object containing the response body of the event. |
| `sentry_ai_headers` | An object containing headers related to Sentry AI. |
| `usage` | An object containing usage statistics. |
| `model` | The model used for the event. |
| `openai_response_id` | The ID of the OpenAI response. |
| `LogId` | The log ID of the event. |
| `id` | The ID of the event. |
| `_rid` | The resource ID of the event. |
| `_self` | The self-reference of the event. |
| `_etag` | The ETag of the event. |
| `_attachments` | The attachments of the event. |
| `_ts` | The timestamp of the event. |

JSON definition example:

```json
{
        "date_time_utc": "2024-05-23T08:17:03.106257+00:00",
        "is_Streaming": false,
        "headers": {
            "Remote-Addr": "10.224.0.5",
            "Api-Key": "82c01474c9e540d1ae3f761d7d7e794b",
            "Arianwashere": "dfsdbgsdgsdgsdgs",
            "Ai-Sentry-Consumer": "Product1",
            "Ai-Sentry-Log-Level": "COMPLETE",
            "Content-Type": "application/json",
            "Postman-Token": "d9cdb055-9a82-45f7-abb6-d97e6b63c862"
        },
        "params": {
            "api-version": "2023-07-01-preview"
        },
        "request_body": {
            "messages": [
                {
                    "role": "system",
                    "content": "you are a Financial analyst employee studying tech companies"
                },
                {
                    "role": "user",
                    "content": "What are microsoft's most profitable products?"
                }
            ],
            "stream": false,
            "max_tokens": 800,
            "temperature": 0.7,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "top_p": 0.95,
            "stop": null
        },
        "response_body": {
            "choices": [
                {
                    "content_filter_results": {
                        "hate": {
                            "filtered": false,
                            "severity": "safe"
                        },
                        "self_harm": {
                            "filtered": false,
                            "severity": "safe"
                        },
                        "sexual": {
                            "filtered": false,
                            "severity": "safe"
                        },
                        "violence": {
                            "filtered": false,
                            "severity": "safe"
                        }
                    },
                    "finish_reason": "stop",
                    "index": 0,
                    "message": {
                        "content": "Microsoft's most profitable products include:\n\n1. Microsoft Office Suite: This includes popular software like Microsoft Word, Excel, PowerPoint, and Outlook, which are widely used by individuals and businesses for productivity and communication purposes.\n\n2. Windows Operating System: Microsoft's flagship operating system, Windows, is used by millions of individuals and businesses worldwide. It generates significant revenue through licensing fees, upgrades, and sales of pre-installed Windows on new devices.\n\n3. Azure Cloud Services: Microsoft's cloud computing platform, Azure, is one of the fastest-growing segments for the company. It provides infrastructure, platform, and software as a service (IaaS, PaaS, and SaaS) solutions, generating substantial revenue from businesses' cloud adoption.\n\n4. Xbox Gaming Console and Services: Microsoft's gaming division, including Xbox consoles and related services like Xbox Live and Xbox Game Pass, contributes significantly to the company's profits. Xbox hardware sales, game sales, and subscriptions generate substantial revenue.\n\n5. Surface Devices: Microsoft's range of Surface devices, including laptops, tablets, and accessories, has gained popularity among consumers and professionals. These products generate revenue through sales and contribute to Microsoft's profitability.\n\nIt is important to note that the profitability of these products may vary over time, and Microsoft's overall financial performance is influenced by various factors, including market conditions and competition.",
                        "role": "assistant"
                    }
                }
            ],
            "created": 1716452216,
            "id": "chatcmpl-9Rxv6geWpNxX0w00S9pQmIjxWK43p",
            "model": "gpt-35-turbo",
            "object": "chat.completion",
            "prompt_filter_results": [
                {
                    "prompt_index": 0,
                    "content_filter_results": {
                        "hate": {
                            "filtered": false,
                            "severity": "safe"
                        },
                        "self_harm": {
                            "filtered": false,
                            "severity": "safe"
                        },
                        "sexual": {
                            "filtered": false,
                            "severity": "safe"
                        },
                        "violence": {
                            "filtered": false,
                            "severity": "safe"
                        }
                    }
                }
            ],
            "system_fingerprint": null,
            "usage": {
                "completion_tokens": 268,
                "prompt_tokens": 28,
                "total_tokens": 296
            }
        },
        "sentry_ai_headers": {
            "Ai-Sentry-Consumer": "Product1",
            "Ai-Sentry-Log-Level": "COMPLETE"
        },
        "usage": {
            "completion_tokens": 268,
            "prompt_tokens": 28,
            "total_tokens": 296
        },
        "model": "gpt-35-turbo",
        "openai_response_id": "chatcmpl-9Rxv6geWpNxX0w00S9pQmIjxWK43p",
        "LogId": "gpt-35-turbo_Product1_05_2024",
        "id": "chatcmpl-9Rxv6geWpNxX0w00S9pQmIjxWK43p",
        "_rid": "vUpsAOlVEEuBAQAAAAAAAA==",
        "_self": "dbs/vUpsAA==/colls/vUpsAOlVEEs=/docs/vUpsAOlVEEuBAQAAAAAAAA==/",
        "_etag": "\"0200bb04-0000-1a00-0000-664efb7f0000\"",
        "_attachments": "attachments/",
        "_ts": 1716452223
    }
```