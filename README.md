# 简介

本项目发布适用于 `DOMAIN-SET` 匹配引擎的 AI 服务域名列表。

仓库中的源文件位于 `source/providers/*.txt`，GitHub Actions 会自动生成发布用的 TXT 文件，并强制推送到 `release` 分支，供 `raw.githubusercontent.com` 和 `jsDelivr` 直接引用。

## DOMAIN-SET 说明

- 每行一个域名
- 以 `.` 开头的行会匹配该域名本身及其所有子域名
- 源文件中可以使用 `*.example.com`，构建时会自动转换为 `.example.com`
- 空行和以 `#` 开头的注释会被忽略

## 在线地址（URL）

> 当前仓库尚未配置远程地址，以下示例使用 `<owner>/<repo>` 占位。连接到 GitHub 后，将其替换为实际仓库路径即可。

- `cursor.txt`
  - `https://raw.githubusercontent.com/<owner>/<repo>/release/cursor.txt`
  - `https://cdn.jsdelivr.net/gh/<owner>/<repo>@release/cursor.txt`
- `ai.txt`
  - `https://raw.githubusercontent.com/<owner>/<repo>/release/ai.txt`
  - `https://cdn.jsdelivr.net/gh/<owner>/<repo>@release/ai.txt`

后续新增 `openai.txt`、`anthropic.txt`、`gemini.txt` 等提供方文件时，发布地址遵循相同命名规则。

## 源文件与构建

- 源文件目录：`source/providers/`
- 每个文件对应一个提供方，例如 `cursor.txt`
- 聚合文件 `ai.txt` 会在构建时自动生成

本地构建命令：

```bash
python3 scripts/build_domainsets.py
```

构建结果会输出到本地 `publish/` 目录，仅用于预览和校验，不需要提交到默认分支。

## 发布方式

仓库内置工作流：`.github/workflows/run.yml`

- 触发方式：`workflow_dispatch` 或推送到 `main`
- `README.md` 单独变更时不会触发发布
- 工作流会重新生成 TXT 文件并强制更新 `release` 分支
- 发布完成后会主动刷新 jsDelivr CDN 缓存
