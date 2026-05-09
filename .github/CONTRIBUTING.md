# Contributing to Claude Skills Collection

感谢你对本项目的关注！以下是贡献指南。

## 目录结构约定

每个 skill 必须满足以下最低结构，根 CI 会自动检查：

```
skills/<skill-name>/
  SKILL.md        # 必须包含 YAML frontmatter（以 --- 分隔）
  README.md       # 用途、安装、测试说明
  LICENSE         # 推荐 MIT（根 LICENSE 可作为默认）
```

可选但推荐的目录：

```
  CONTRIBUTING.md # 该 skill 的具体贡献指南
  references/     # 参考文档
  examples/       # 使用示例
  tests/          # 测试用例
  scripts/        # 可执行脚本
  tools/          # 工具函数
  prompts/        # Prompt 模板
```

## 开发环境

- **Python skills**（bestie, digital-self, last30days 等）：Python 3.10+，依赖见各 skill 的 `requirements.txt`
- **Node.js skills**（bishe-manual-skill, lunwen 等）：Node 18+，依赖见 `package.json`
- **大型项目**（lz-docforge）：使用 `uv` 管理 Python 环境，见其 `CONTRIBUTING.md`

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat: add new skill xyz
fix: correct SKILL.md frontmatter in abc
docs: update README with install instructions
chore: update dependabot config
ci: extend lint checks to top-level skills
```

## Pull Request 流程

1. Fork 本仓库，创建功能分支
2. 确保改动通过本地 CI 验证（见下方）
3. 提交 PR，填写 PR 模板
4. 关联相关 issue
5. 等待 CI 绿灯 + review

## CI 流程

根目录 `.github/workflows/ci.yml` 在每次 push/PR 到 `main` 时运行，检查 `skills/` 下所有子目录：

| 检查项 | 说明 | 严重度 |
|--------|------|--------|
| SKILL.md 存在 | 必须存在 | ❌ 阻断 |
| SKILL.md frontmatter | 必须包含 `---` 分隔符 | ❌ 阻断 |
| README.md 存在 | 必须存在 | ❌ 阻断 |
| LICENSE 存在 | 推荐存在 | ⚠️ 警告 |
| Python skill 验证 | bestie/digital-self 需有 requirements.txt 和 tests/ | ✅ 信息 |

本地模拟 CI：

```bash
# 在仓库根目录执行
for skill in skills/*/; do
  name=$(basename "$skill")
  echo "--- $name ---"
  [ -f "${skill}SKILL.md" ] && echo "  SKILL.md: OK" || echo "  SKILL.md: MISSING"
  grep -q '^---' "${skill}SKILL.md" 2>/dev/null && echo "  frontmatter: OK" || echo "  frontmatter: MISSING"
  [ -f "${skill}README.md" ] && echo "  README.md: OK" || echo "  README.md: MISSING"
  [ -f "${skill}LICENSE" ] && echo "  LICENSE: OK" || echo "  LICENSE: MISSING (warning)"
done
```

## 添加新 Skill

1. 在 `skills/` 下创建目录
2. 编写 `SKILL.md`（含 frontmatter）和 `README.md`
3. 放置 `LICENSE`（可复制根目录 MIT）
4. 本地跑 CI 验证
5. 提交 PR

## 子项目贡献指南

部分子项目有独立的 `CONTRIBUTING.md`，对代码风格、测试框架等有更详细的要求：

- **lz-docforge**：Ruff + MyPy + pre-commit，详见 `lz-docforge/CONTRIBUTING.md`
- **last30days-cn-skill**：pytest，详见 `last30days-cn-skill/CONTRIBUTING.md`
- **bishe-manual-skill / lunwen**：pytest + Playwright browser tests

## 行为准则

本项目采用 [Contributor Covenant](CODE_OF_CONDUCT.md) 行为准则。
