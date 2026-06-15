---
name: wc26-predict-text-only
description: Use this skill whenever the user needs a pure md/txt distributable version of the WC26 Predict project that can reconstruct a runnable local prediction app without downloading any upstream repository. This skill is specifically for rebuilding the text-only ELO-capable WC26 project from bundled markdown references. Also use it when the user says "只支持 md/txt", "给朋友发一个纯文本 skill", "安装后重建 WC26 预测项目", "不要依赖上游仓库", or wants the earlier modified project packaged in a text-only skill format.
---

# WC26 Predict Text-Only Skill

This skill rebuilds a runnable WC26 Predict project from bundled markdown references only.

It exists for environments where the distributable package may contain only:

- `.md`
- `.txt`
- or folders containing only those file types

The generated project is based on the already modified local WC26 Predict build, but expressed as text templates.

## What this skill should do

When triggered, reconstruct a local project by creating these files from the bundled references:

- `elo/app.R`
- `elo/simulation.R`
- `data/teams.csv`
- `data/matches.csv`
- `data/venues.csv`
- `data/score_dist.csv`
- `data/cache/results.tsv`

Then help the user install dependencies, run the app, and verify the output.

## Important scope

This is the **text-only** version of the project.

- It does not download the upstream GitHub repository.
- It does not require any binary model files to be bundled.
- It is designed to run the ELO-based workflow and the Chinese/weather/stadium enhancements.
- The Dixon-Coles UI may still appear in the generated app, but without the DC model file it is expected to be unavailable.

That trade-off is intentional so the project can be distributed in a pure markdown/text format.

## Reconstruction workflow

Follow this sequence exactly:

1. Create the target folder structure:
   - `elo/`
   - `data/`
   - `data/cache/`
2. Read the bundled reference files in `references/`.
3. Write each referenced file to disk with the exact contents from the code fences.
4. Install required R packages if the machine does not already have them.
5. Verify with a source check.
6. Launch the Shiny app if requested.

## Reference files

Use these reference files:

- `references/app-files.md`
- `references/data-core.md`
- `references/data-schedule.md`

Always copy the file contents exactly from those references. Do not paraphrase or regenerate them from memory if the reference exists.

## Required R packages

Install these if missing:

- `shiny`
- `dplyr`
- `DT`
- `future`
- `promises`
- `jsonlite`

Recommended install command:

```bash
Rscript -e "options(repos=c(CRAN='https://mirrors.tuna.tsinghua.edu.cn/CRAN/')); install.packages(c('shiny','dplyr','DT','future','promises','jsonlite'))"
```

## Verification

Always verify in two passes:

1. Source check

```bash
Rscript -e "setwd('/path/to/project/elo'); source('app.R', local = new.env()); cat('source_ok\\n')"
```

2. Runtime check

```bash
Rscript -e "shiny::runApp('/path/to/project/elo', host='127.0.0.1', port=3840, launch.browser=FALSE)"
```

Then confirm that the rendered app includes:

- `⚙️ 参数设置`
- `▶ 开始模拟`
- `🏅 小组积分榜`
- `🌦️ 天气与球场`

## Output expectations

When you finish, report:

- where the project was written
- which reference files were used
- whether R dependencies were installed
- whether the app was started
- the localhost URL if running
- that weather and stadium data are auxiliary analysis by default
- that Dixon-Coles is not bundled in this text-only version

## Example prompts this skill should handle

**Example 1**
User: `给我一个只含 md/txt 的 WC26 预测 skill。`

**Example 2**
User: `朋友那边只能装纯文本 skill，你帮我重建一个可运行的 WC26 预测项目。`

**Example 3**
User: `不要下载上游仓库，直接用这个 text-only skill 生成预测项目。`
