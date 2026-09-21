# 平湖润泽调研报告网页 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将完整平湖润泽调研报告发布为可公开访问、来源完整且适合管理层阅读的 GitHub Pages 单页报告。

**Architecture:** 使用无外部依赖的静态 HTML/CSS/JavaScript。内容从现有 Markdown 转换并装配到页面中；人工设计的决策摘要和可视化位于正文之前，完整研究正文与来源附录继续保留。根目录索引提供公开入口。

**Tech Stack:** HTML5、CSS3、原生 JavaScript、Python 标准库生成与静态检查、GitHub Pages。

---

### Task 1: 建立页面生成器与完整正文

**Files:**
- Create: `work/build_pinghu_runze_report.py`
- Create: `reports/pinghu-runze-zhejiang-idc-compute-cooperation-2026.html`

- [ ] **Step 1: 实现 Markdown 块级解析**

实现标题、段落、加粗、列表、表格和链接的安全转换，并为来源编号生成可跳转锚点。

- [ ] **Step 2: 装配页面结构**

加入 Hero、指标全景、关系图、时间线、商业模式矩阵、90天路线图、完整正文和 provenance footer。

- [ ] **Step 3: 生成静态页面**

Run: `python3 work/build_pinghu_runze_report.py`

Expected: 输出 `reports/pinghu-runze-zhejiang-idc-compute-cooperation-2026.html`，且命令退出码为 0。

### Task 2: 更新公开索引

**Files:**
- Modify: `index.html`

- [ ] **Step 1: 添加报告入口**

在根页面首组报告中添加平湖润泽报告标题、日期和相对链接。

- [ ] **Step 2: 检查相对链接**

Run: `test -f reports/pinghu-runze-zhejiang-idc-compute-cooperation-2026.html`

Expected: 退出码为 0。

### Task 3: 内容与结构验证

**Files:**
- Verify: `reports/pinghu-runze-zhejiang-idc-compute-cooperation-2026.html`

- [ ] **Step 1: 运行静态内容检查**

核对十章、附录A、附录B、27项来源、来源链接、内部锚点、viewport、打印样式和移动端断点。

- [ ] **Step 2: 检查公开边界**

搜索本机绝对路径、Word下载、私人账户信息和缺失占位符，预期均为零命中。

- [ ] **Step 3: 浏览器视觉检查**

在桌面和手机宽度查看首屏、目录、表格、时间线和来源附录，确认无正文横向溢出，正文完整可达。

### Task 4: 发布与公网验证

**Files:**
- Commit: report page, index, design and plan documents

- [ ] **Step 1: 提交网页变更**

Run: `git add .gitignore docs/superpowers reports/pinghu-runze-zhejiang-idc-compute-cooperation-2026.html index.html && git commit -m "Publish Pinghu Runze IDC cooperation report"`

Expected: 创建新提交，工作区干净。

- [ ] **Step 2: 推送主分支**

Run: `git push origin main`

Expected: 远端 `main` 更新成功。

- [ ] **Step 3: 验证公开页面**

Run: `curl -L --retry 8 --retry-delay 5 --fail https://ewangwo.github.io/lff-reports/reports/pinghu-runze-zhejiang-idc-compute-cooperation-2026.html`

Expected: HTTP 200，响应包含报告标题、核心判断和来源附录。
