# Output Manifest Spec

## 目标

每次 Actor 运行都会生成一个 `OUTPUT_MANIFEST`（键名可配置），用于标准化记录请求、产物、日志与错误码。

## 默认 Key

- Manifest key: `OUTPUT_MANIFEST`
- Log key: `DOCFORGE_LOG`
- Output key: `OUTPUT`

## JSON 结构

```json
{
  "manifest_version": "1.0.0",
  "actor_name": "docforge-actor",
  "generated_at": "2026-04-09T10:00:00Z",
  "status": "success",
  "error_code": "A0000",
  "error_message": null,
  "source_document_url": "https://example.com/input.pdf",
  "output": {
    "key": "OUTPUT",
    "url": "https://api.apify.com/v2/key-value-stores/<STORE>/records/OUTPUT",
    "content_type": "application/zip",
    "size_bytes": 12345
  },
  "records": {
    "manifest_key": "OUTPUT_MANIFEST",
    "log_key": "DOCFORGE_LOG"
  },
  "runtime": {
    "curl_exit_code": 0
  },
  "request": {
    "http_sources": [{"url": "https://example.com/input.pdf"}],
    "options": {"to_formats": ["md", "json"]}
  }
}
```

## 字段约束

- `status`: `success` or `error`
- `error_code`: 参考 `ERROR_CODES.md`
- `output.size_bytes`: 整数，失败时为 `0`
- `request.http_sources`: 原始输入 URL 列表
- `request.options`: 原始转换参数

## 失败场景规范

- 当转换失败时，`status=error`
- `error_code` 设置为对应错误码（如 `A3001`）
- `output.url` 可为空字符串
- `error_message` 必须填写可读错误摘要
