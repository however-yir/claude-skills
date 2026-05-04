# DocForge Actor Error Codes

## 说明

本表定义 `.actor/actor.sh` 在运行过程中使用的标准错误码，便于排障、告警与自动重试。

## 代码表

| Code | Level | Meaning | Typical action |
|---|---|---|---|
| `A0000` | info | Success | No action needed |
| `A1001` | critical | `docling-serve` API failed to start | Check container log and runtime dependency |
| `A2001` | warning | API endpoint not fully ready but conversion attempted | Verify endpoint health and startup timeout |
| `A3001` | error | Output zip not found after conversion | Check input URL, API response, and conversion logs |
| `A3002` | error | Failed to upload OUTPUT artifact to KVS | Check Apify CLI permission and key-value store status |
| `A3003` | error | Failed to upload output manifest to KVS | Check Apify CLI permission and KVS write path |
| `A4001` | error | Invalid input JSON or missing required fields | Validate against `.actor/input_schema.json` |
| `A5001` | warning | Dataset push failed | Retry push or inspect CLI capability |

## 使用建议

- `A1xxx`：基础设施启动与可用性问题
- `A3xxx`：产物输出与归档问题
- `A4xxx`：输入数据质量问题
- `A5xxx`：外围平台写入问题
