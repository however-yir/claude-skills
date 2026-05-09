## 变更摘要

<!-- 简要描述本次 PR 做了什么 -->

## 变更类型

- [ ] 新增 skill
- [ ] bug 修复
- [ ] 文档更新
- [ ] CI / 工程配置
- [ ] 重构
- [ ] 其他

## 关联 Issue

<!-- 格式: Closes #123 或 Relates to #123 -->

## 测试方式

<!-- 如何验证本次变更？ -->

```bash
# 本地 CI 验证
for skill in skills/*/; do
  name=$(basename "$skill")
  [ -f "${skill}SKILL.md" ] && grep -q '^---' "${skill}SKILL.md" && [ -f "${skill}README.md" ] \
    && echo "✅ $name" || echo "❌ $name"
done
```

## 检查清单

- [ ] SKILL.md 包含正确的 YAML frontmatter
- [ ] README.md 包含用途、安装、测试说明
- [ ] LICENSE 文件存在
- [ ] 本地 CI 验证通过
- [ ] 如有 Python 代码，测试通过
- [ ] 如有 Node.js 代码，测试通过
- [ ] 遵循 Conventional Commits 规范
