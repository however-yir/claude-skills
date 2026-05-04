# /last30days v3.0-local（中文改编版）

🔥 A China-focused last-30-days trend analysis skill across X, Weibo, Xiaohongshu, and Douyin.  
🚀 Produces structured Chinese insight reports with cross-platform overlap, regional split, and emerging signals.  
⭐ Designed for fast trend intelligence, content planning, and decision-ready briefs.

> 中文别名建议：**last30中国趋势**（为兼容现有调用，技能名仍保留 `last30days`）

这个版本是基于原仓库改编的本地变体，定位是：

- 最近 30 天趋势扫描
- 严格平台范围：**X / Weibo / Xiaohongshu / Douyin**
- 输出中文、结构化、可直接用于洞察汇报

---

## 这版和原版的核心差异

相对原技能（多平台通用研究助手），这版做了定向收敛：

- 从“泛全网研究”收敛到“中外社媒趋势对照”
- 明确只使用 4 个平台作为证据源
- Weibo / Douyin 不再依赖限域 `WebSearch`，改为 **native connector**
- 输出模板、执行流程、策略文档改为中文趋势分析导向
- 保留原工程的评分、去重、诊断、可观测能力

---

## 新增能力（Phase 2）

### Weibo Native Connector

- 新增 `scripts/lib/weibo.py`
- 通过 Weibo cookie（`WEIBO_SUB`，可选 `WEIBO_SUBP`）进行原生抓取
- 自动清洗 HTML、解析时间、提取互动信号并归一化

### Douyin Native Connector

- 新增 `scripts/lib/douyin.py`
- 使用 Douyin 热榜原生接口进行趋势抓取（无需 API Key）
- 按主题相关性过滤并生成可评分条目

### 主流程接入

- `scripts/last30days.py` 已支持：
  - `--search weibo,douyin`
  - `--diagnose` 输出 `weibo` / `douyin` 状态
  - 把 Weibo / Douyin 条目并入统一 `web` 桶（带 `source_domain`）
- `render` 和 `ui` 已新增 Weibo / Douyin 状态展示

---

## 快速开始

## 1) 环境诊断

```bash
python3 scripts/last30days.py --diagnose
```

重点看这些字段：

- `x_source`：X 是否可用
- `weibo`、`weibo_auth_method`：Weibo cookie 是否可用
- `xiaohongshu`：小红书本地服务是否可用且已登录
- `douyin`：Douyin native connector 是否可用

## 2) 运行四平台趋势采集

```bash
python3 scripts/last30days.py "你的主题" \
  --emit=json \
  --search x,weibo,xiaohongshu,douyin \
  --no-native-web \
  --days=30
```

说明：

- `--no-native-web`：关闭通用网页搜索后端（本改编版建议始终开启）
- `--search ...`：只跑你指定的平台 connector

## 3) 平台配置要求

- X：Bird 登录态或 `XAI_API_KEY`
- Weibo：`WEIBO_SUB`（可选 `WEIBO_SUBP`）
- Xiaohongshu：本地 `xiaohongshu-mcp` 服务可达且账号已登录
- Douyin：默认可用（无需 key）

---

## 输出结构（本改编版）

为保持工程兼容，Weibo / Xiaohongshu / Douyin 目前统一落在 `web` 数组中，用 `source_domain` 区分：

- `x`：X 结果
- `web`：`weibo.com` / `xiaohongshu.com` / `douyin.com`

推荐在上层合成时按 `source_domain` 重新分组，得到平台维度报告。

---

## 改编是否合法？（结论）

**允许。**

本仓库许可证为 **MIT License**，明确允许：

- 使用、复制、修改、合并、发布、分发、再许可、商用

你需要做的是：

- 保留原版权声明
- 保留 MIT 许可证文本（`LICENSE`）

这也是本改编版保持 `LICENSE` 文件不变的原因。

---

## 建议的后续增强

- Weibo connector 增加更多时间格式与列表页兼容策略
- Douyin connector 增加主题榜/话题挑战二级抓取
- `web` 桶进一步拆分为独立 `weibo` / `douyin` / `xiaohongshu` 字段（可选）

---

## 致谢

本项目基于原作者仓库进行本地化改编：

- 原项目：`mvanhorn/last30days-skill`
- 许可证：MIT
