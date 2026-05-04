# 配置优先级说明 / Configuration Priority

## 目标

在不破坏默认行为的前提下，让本地、测试、生产环境能够用最小改动切换 API 地址与运行参数。

## 优先级规则

按优先级从高到低：

1. 显式传参（代码中直接传入 `url`）
2. 环境变量
3. 代码内默认值

## VLM 相关变量

- `DOCLING_VLM_API_URL`
- `DOCLING_VLM_OLLAMA_URL`
- `DOCLING_VLM_LMSTUDIO_URL`
- `DOCLING_VLM_OPENAI_URL`

## Actor 相关变量

- `DOCLING_SERVE_API_ENDPOINT`
- `DOCLING_ACTOR_LOG_KEY`

## 示例

```bash
export DOCLING_VLM_OLLAMA_URL="http://10.0.0.22:11434/v1/chat/completions"
export DOCLING_SERVE_API_ENDPOINT="http://10.0.0.30:5001/v1alpha/convert/source"
```

## 建议

- 开发环境：使用 `.env` 与本地地址
- 测试环境：使用 CI 注入环境变量
- 生产环境：使用 Secret Manager 注入，禁止明文落盘
