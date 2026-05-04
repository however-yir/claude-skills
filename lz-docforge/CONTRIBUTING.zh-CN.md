# 贡献指南（中文）

## 1. 总体原则

- 优先保持兼容性：避免破坏现有 `docling` 命名空间使用方式。
- 变更要可验证：功能改动至少附带最小测试或复现说明。
- 配置不硬编码：新增地址、密钥、凭据一律走环境变量。

## 2. 开发环境

推荐使用 `uv`：

```bash
uv sync
```

如需指定 Python：

```bash
uv venv --python 3.12
uv sync
```

## 3. 代码规范

- Lint/format：Ruff
- 类型检查：MyPy
- 提交前建议执行：

```bash
pre-commit run --all-files
```

## 4. 提交流程

1. 从最新主分支拉出功能分支。
2. 变更尽量聚焦单一主题。
3. 补充必要测试和文档。
4. 提交前运行：

```bash
bash scripts/check-secrets.sh
python3 scripts/validate_env.py
```

5. 发起 PR 并说明：
- 变更目的
- 影响范围
- 回归验证方式

## 5. 文档贡献

以下文档建议同步维护：

- `README.md`（使用与定位）
- `docs/branding/*`（品牌与迁移说明）
- `SECURITY.md`（安全策略）
- `ROADMAP.md`（演进计划）

## 6. 高风险改动清单

以下改动请务必在 PR 中显式标注：

- `pyproject.toml` 依赖变更
- `docling/datamodel/*` 的默认配置行为变更
- `.actor/*` 的执行入口与输出协议变更
- CI workflow 变更
