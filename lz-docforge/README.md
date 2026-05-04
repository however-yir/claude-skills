<p align="center">
  <img loading="lazy" alt="文档炼金炉 DocForge" src="docs/assets/docforge_logo.svg" width="100%"/>
</p>

# 文档炼金炉 DocForge

> **非官方声明（Non-Affiliation）**  
> 本仓库为社区维护的衍生/二次开发版本，与上游项目及其权利主体不存在官方关联、授权背书或从属关系。  
> **商标声明（Trademark Notice）**  
> 相关项目名称、Logo 与商标归其各自权利人所有。本仓库仅用于说明兼容/来源，不主张任何商标权利。


面向中文与多格式文档处理的工程化分支，基于 Docling 做了品牌化、配置化和交付治理增强。

> **非官方声明（Non-Affiliation）**<br>
> `DocForge` 是基于 `docling-project/docling` 的社区维护衍生版，与上游项目及其权利主体不存在官方关联、授权背书或从属关系。<br>
> **商标声明（Trademark Notice）**<br>
> `Docling` 及相关项目名称、Logo 与商标归其各自权利人所有；本仓库仅用于说明上游来源与兼容关系。

## 快速开始 Quick Start

```bash
pip install -e .

# 新命令（推荐）
docforge --help

# 兼容命令（保留）
docling --help
```

## 首页简版说明

- 保留 `docling` 兼容生态
- 新增 `docforge` 命令入口
- 支持通过环境变量覆盖 VLM 与 Actor endpoint
- `.actor` 支持错误码与 output manifest
- 增加安全流程、漏洞模板、轻量治理 CI

## 详细文档索引 Detailed Docs

| 文档 | 用途 |
|---|---|
| [项目总览索引](docs/project/index.md) | 本仓库改造、功能边界、检查命令总入口 |
| [品牌文档入口](docs/branding/index.md) | 品牌、迁移、配置优先级与 GitHub 设置 |
| [Actor 说明](.actor/README.md) | 云端封装使用、错误码、manifest 规范 |
| [安全策略](SECURITY.md) | 漏洞响应流程、提交流程模板 |
| [路线图](ROADMAP.md) | 后续版本规划 |
| [中文贡献指南](CONTRIBUTING.zh-CN.md) | 中文协作与提交约定 |

## 环境与治理检查

```bash
python3 scripts/validate_env.py
bash scripts/check-secrets.sh
bash scripts/verify_repo_readiness.sh
```

## 与上游关系

- 上游基础：`docling-project/docling`
- 当前策略：在兼容主命名空间前提下做工程化和品牌增强
- 迁移参考：见 [从 Docling 迁移](docs/branding/migration-from-docling.md)

## 许可 License

- 继承代码：遵循 [MIT License](LICENSE)
- 本仓库补充条款：见 [LICENSE-DOCFORGE.md](LICENSE-DOCFORGE.md)
