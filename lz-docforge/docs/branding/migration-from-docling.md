# 从 Docling 迁移到 DocForge / Migration Guide

## 1. 迁移目标

本文档用于帮助已有 `docling` 使用者快速迁移到当前仓库维护的 `DocForge` 分支，并尽可能保持运行行为一致。

## 2. 兼容性策略

- Python 代码层：继续使用 `import docling`，不强制修改命名空间。
- CLI 层：保留 `docling`，新增 `docforge` 作为品牌化入口。
- 配置层：默认值保持原行为，同时允许环境变量覆盖。

## 3. 关键差异

| 项目 | Docling | DocForge |
|---|---|---|
| 发布名 | `docling` | `lz-docforge` |
| CLI 命令 | `docling` | `docling` + `docforge` |
| VLM 地址 | 代码默认 | 代码默认 + ENV 覆盖 |
| Actor 名称 | `docling` | `docforge-actor` |

## 4. 迁移步骤

### 4.1 安装

```bash
pip uninstall -y docling
pip install lz-docforge
```

### 4.2 命令替换（可选）

```bash
# 旧命令（仍可用）
docling <source>

# 新命令（推荐）
docforge <source>
```

### 4.3 环境变量配置

复制并修改：

```bash
cp .env.example .env
```

重点关注：

- `DOCLING_VLM_API_URL`
- `DOCLING_VLM_OLLAMA_URL`
- `DOCLING_VLM_LMSTUDIO_URL`
- `DOCLING_VLM_OPENAI_URL`

### 4.4 Actor 迁移

- 将旧 Actor 名称迁移为 `docforge-actor`
- 使用 `DOCLING_SERVE_API_ENDPOINT` 覆盖内部转换地址
- 使用 `DOCLING_ACTOR_LOG_KEY` 统一日志键名

## 5. 回滚方案

若迁移后出现兼容性问题，可执行：

```bash
pip uninstall -y lz-docforge
pip install docling
```

并移除新增环境变量配置，恢复原行为。
