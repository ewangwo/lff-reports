#!/usr/bin/env python3
"""Build the public Pinghu Runze research webpage from the canonical Markdown report."""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "2026-09-21" / "xiang" / "outputs" / "平湖润泽_浙江IDC与算力产业及合作落地调研报告_20260921.md"
OUTPUT = ROOT / "reports" / "pinghu-runze-zhejiang-idc-compute-cooperation-2026.html"


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def source_links(value: str) -> str:
    pattern = re.compile(r"\[(S\d{2})([^\]]*)\]")
    return pattern.sub(
        lambda match: (
            f'<a class="source-ref" href="#source-{match.group(1).lower()}" '
            f'aria-label="跳转到来源 {match.group(1)}">[{match.group(1)}{match.group(2)}]</a>'
        ),
        value,
    )


def inline_markup(value: str) -> str:
    escaped = html.escape(value, quote=False)
    links: list[str] = []

    def store_link(match: re.Match[str]) -> str:
        label = match.group(1)
        url = html.escape(match.group(2), quote=True)
        links.append(
            f'<a href="{url}" target="_blank" rel="noopener noreferrer">{label}<span class="external" aria-hidden="true">↗</span></a>'
        )
        return f"@@LINK{len(links) - 1}@@"

    escaped = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", store_link, escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = source_links(escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    for index, link in enumerate(links):
        escaped = escaped.replace(f"@@LINK{index}@@", link)
    return escaped


def heading_id(text: str, counters: dict[str, int]) -> str:
    source = re.search(r"\[?(S\d{2})\]?", text)
    if source:
        return f"source-{source.group(1).lower()}"
    chapter = re.match(r"([一二三四五六七八九十]+)、", text)
    if chapter:
        mapping = {
            "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
            "六": "6", "七": "7", "八": "8", "九": "9", "十": "10",
        }
        return f"chapter-{mapping.get(chapter.group(1), chapter.group(1))}"
    sub = re.match(r"(\d+)\.(\d+)", text)
    if sub:
        return f"section-{sub.group(1)}-{sub.group(2)}"
    if text.startswith("附录A"):
        return "appendix-a"
    if text.startswith("附录B"):
        return "appendix-b"
    counters["heading"] += 1
    return f"section-extra-{counters['heading']}"


def paragraph_class(text: str) -> str:
    classes: list[str] = []
    if text.startswith("**商业判断：**") or text.startswith("**商业洞察：**"):
        classes.append("insight")
    if text.startswith("**建议") or text.startswith("**供应商策略：**") or text.startswith("**停止或降级条件：**"):
        classes.append("recommendation")
    if text.startswith("**已发生事项：**") or text.startswith("**已披露事项：**"):
        classes.append("fact")
    if text.startswith("**证据边界：**"):
        classes.append("caveat")
    if re.match(r"\*\*\[S\d{2}\]", text):
        classes.append("source-entry")
    return " ".join(classes)


def render_markdown(markdown_text: str) -> tuple[str, list[tuple[str, str, int]]]:
    lines = markdown_text.splitlines()
    output: list[str] = []
    toc: list[tuple[str, str, int]] = []
    counters = {"heading": 0}
    i = 0

    if lines and lines[0].startswith("# "):
        i = 1

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue

        heading = re.match(r"^(#{2,4})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            anchor = heading_id(title, counters)
            output.append(f'<h{level} id="{anchor}">{inline_markup(title)}</h{level}>')
            toc.append((anchor, re.sub(r"^\d+\.\d+\s*", "", title), level))
            i += 1
            continue

        if (
            line.lstrip().startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1])
        ):
            headers = split_table_row(line)
            i += 2
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(split_table_row(lines[i]))
                i += 1
            output.append('<div class="table-scroll" tabindex="0" role="region" aria-label="可横向滚动的数据表"><table><thead><tr>')
            output.extend(f"<th>{inline_markup(cell)}</th>" for cell in headers)
            output.append("</tr></thead><tbody>")
            for row in rows:
                output.append("<tr>")
                for index in range(len(headers)):
                    cell = row[index] if index < len(row) else ""
                    output.append(f"<td>{inline_markup(cell)}</td>")
                output.append("</tr>")
            output.append("</tbody></table></div>")
            continue

        ordered = re.match(r"^(\d+)\.\s+(.+)$", line)
        if ordered:
            items: list[str] = []
            start = ordered.group(1)
            while i < len(lines):
                match = re.match(r"^(\d+)\.\s+(.+)$", lines[i].rstrip())
                if not match:
                    break
                items.append(match.group(2))
                i += 1
            output.append(f'<ol start="{start}">')
            output.extend(f"<li>{inline_markup(item)}</li>" for item in items)
            output.append("</ol>")
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", line)
        if unordered:
            items: list[str] = []
            while i < len(lines):
                match = re.match(r"^[-*]\s+(.+)$", lines[i].rstrip())
                if not match:
                    break
                items.append(match.group(1))
                i += 1
            output.append("<ul>")
            output.extend(f"<li>{inline_markup(item)}</li>" for item in items)
            output.append("</ul>")
            continue

        paragraph = [line.strip()]
        i += 1
        while i < len(lines):
            next_line = lines[i].rstrip()
            if not next_line.strip():
                break
            if re.match(r"^(#{2,4})\s+", next_line):
                break
            if next_line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1]):
                break
            if re.match(r"^(\d+)\.\s+", next_line) or re.match(r"^[-*]\s+", next_line):
                break
            paragraph.append(next_line.strip())
            i += 1
        joined = " ".join(paragraph)
        classes = paragraph_class(joined)
        source_match = re.match(r"\*\*\[(S\d{2})\]", joined)
        source_id = f' id="source-{source_match.group(1).lower()}"' if source_match else ""
        class_attr = f' class="{classes}"' if classes else ""
        output.append(f"<p{source_id}{class_attr}>{inline_markup(joined)}</p>")

    return "\n".join(output), toc


def build_nav(toc: list[tuple[str, str, int]]) -> str:
    major = [(anchor, title) for anchor, title, level in toc if level == 2]
    return "\n".join(
        f'<a href="#{anchor}"><span>{index:02d}</span>{html.escape(title)}</a>'
        for index, (anchor, title) in enumerate(major, 1)
    )


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    article, toc = render_markdown(source)
    nav = build_nav(toc)
    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="平湖润泽在浙江IDC与算力产业中的商业位置、合作模式、优先机会和90天落地路径。">
<meta property="og:title" content="平湖润泽：浙江IDC与算力产业及合作落地调研报告">
<meta property="og:description" content="值得合作，但要围绕实际订单与总部决策开展。">
<meta property="og:type" content="article">
<meta property="og:url" content="https://ewangwo.github.io/lff-reports/reports/pinghu-runze-zhejiang-idc-compute-cooperation-2026.html">
<title>平湖润泽｜浙江IDC与算力产业及合作落地调研报告</title>
<style>
:root{
  --paper:#f3efe6;--paper-2:#ebe4d7;--ink:#173044;--muted:#61717b;--navy:#12364b;
  --navy-2:#1d4b60;--teal:#2c7774;--teal-soft:#d9e9e4;--orange:#d8653e;--orange-soft:#f2dfd2;
  --gold:#b4873f;--red:#a84c43;--line:#d5cec0;--white:#fffdf8;--shadow:0 16px 44px rgba(28,46,58,.1);
  --radius:18px;--serif:"Songti SC","STSong","Noto Serif CJK SC",serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:28px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.82}
a{color:var(--teal);text-decoration-thickness:1px;text-underline-offset:3px}
a:hover{color:var(--orange)}
a:focus-visible,button:focus-visible,[tabindex]:focus-visible{outline:3px solid #e9985d;outline-offset:3px}
.skip{position:absolute;left:-9999px;top:8px;background:#fff;padding:8px 12px;z-index:100}
.skip:focus{left:8px}
.progress{position:fixed;left:0;top:0;width:100%;height:4px;z-index:90;background:transparent}
.progress span{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--teal),var(--orange))}
.hero{min-height:92vh;display:flex;align-items:flex-end;color:#f7f2e8;position:relative;overflow:hidden;background:
  radial-gradient(circle at 83% 17%,rgba(75,151,145,.32),transparent 27%),
  linear-gradient(132deg,#0d2a3d 0%,#153f52 54%,#204d55 100%)}
.hero:before{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:44px 44px;mask-image:linear-gradient(to bottom,#000,transparent 88%)}
.hero:after{content:"";position:absolute;width:540px;height:540px;border:1px solid rgba(255,255,255,.12);border-radius:50%;right:-110px;top:-150px;box-shadow:0 0 0 78px rgba(255,255,255,.025),0 0 0 156px rgba(255,255,255,.02)}
.hero-inner{width:min(1180px,calc(100% - 40px));margin:0 auto;padding:92px 0 72px;position:relative;z-index:2}
.eyebrow{font-size:.77rem;letter-spacing:.18em;text-transform:uppercase;color:#9dd5ce;font-weight:750}
.hero h1{font-family:var(--serif);font-size:clamp(2.6rem,6.8vw,6.3rem);line-height:1.04;letter-spacing:-.045em;margin:.2em 0 .26em;max-width:1040px}
.hero h1 em{font-style:normal;color:#f1a86e}
.hero-lead{font-family:var(--serif);font-size:clamp(1.16rem,2.1vw,1.65rem);line-height:1.65;max-width:900px;color:#e0ebe8;margin:0}
.hero-meta{display:flex;flex-wrap:wrap;gap:10px;margin-top:30px}
.hero-meta span{padding:7px 12px;border:1px solid rgba(255,255,255,.2);border-radius:999px;font-size:.78rem;color:#d7e5e4;background:rgba(255,255,255,.045);backdrop-filter:blur(4px)}
.hero-action{margin-top:34px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.hero-action a{display:inline-flex;align-items:center;gap:8px;color:#173044;background:#f4a26b;border-radius:999px;padding:11px 18px;font-weight:750;text-decoration:none}
.hero-action small{color:#bcd0d1}
.layout{width:min(1240px,calc(100% - 40px));margin:0 auto;display:grid;grid-template-columns:245px minmax(0,1fr);gap:54px;padding:64px 0 100px}
.sidebar{align-self:start;position:sticky;top:28px;min-width:0}
.sidebar-label{font-size:.68rem;text-transform:uppercase;letter-spacing:.14em;color:var(--muted);font-weight:800;margin-bottom:12px}
.sidebar nav{border-left:1px solid var(--line)}
.sidebar nav a{display:flex;gap:10px;color:#647680;text-decoration:none;font-size:.79rem;line-height:1.35;padding:7px 10px;border-left:2px solid transparent;margin-left:-1px}
.sidebar nav a span{font-variant-numeric:tabular-nums;color:#9d8d75}
.sidebar nav a.active{border-left-color:var(--orange);color:var(--ink);font-weight:700;background:linear-gradient(90deg,var(--orange-soft),transparent)}
.sidebar-note{margin-top:22px;padding:13px;border:1px solid var(--line);border-radius:12px;font-size:.72rem;color:var(--muted);background:rgba(255,255,255,.3)}
.content{min-width:0}
.decision{background:var(--white);border:1px solid var(--line);box-shadow:var(--shadow);border-radius:var(--radius);padding:clamp(24px,5vw,54px);position:relative;overflow:hidden}
.decision:after{content:"DECISION BRIEF";position:absolute;right:-16px;top:22px;color:rgba(18,54,75,.045);font-size:4rem;font-weight:900;letter-spacing:-.05em}
.kicker{font-size:.72rem;letter-spacing:.16em;text-transform:uppercase;color:var(--orange);font-weight:850}
.decision h2{font-family:var(--serif);font-size:clamp(1.75rem,3vw,2.8rem);line-height:1.33;margin:.35em 0 .45em;position:relative;z-index:1}
.decision>p{font-size:1.05rem;color:#425c69;max-width:850px;position:relative;z-index:1}
.first-move{margin-top:24px;padding:18px 20px;background:var(--orange-soft);border-left:5px solid var(--orange);border-radius:0 12px 12px 0}
.first-move b{display:block;font-size:.73rem;letter-spacing:.1em;text-transform:uppercase;color:#9c472d;margin-bottom:4px}
.metric-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:28px 0}
.metric{background:rgba(255,255,255,.68);border:1px solid var(--line);border-radius:14px;padding:18px 16px;min-height:128px}
.metric strong{display:block;font-family:var(--serif);font-size:1.72rem;line-height:1.2;color:var(--navy);margin-bottom:6px}
.metric span{font-size:.8rem;color:var(--muted);line-height:1.5}
.metric small{display:block;color:#8d806d;margin-top:6px;font-size:.66rem}
.visual-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:18px 0 56px}
.visual{background:var(--white);border:1px solid var(--line);border-radius:var(--radius);padding:24px;box-shadow:0 8px 26px rgba(28,46,58,.06)}
.visual.wide{grid-column:1/-1}
.visual h3{font-size:1rem;margin:0 0 4px}
.visual .caption{font-size:.74rem;color:var(--muted);margin-bottom:18px}
.entity-flow{display:grid;grid-template-columns:1fr 34px 1fr 34px 1fr;align-items:center;gap:6px}
.entity{padding:14px 10px;background:var(--teal-soft);border-radius:10px;text-align:center;font-size:.77rem;line-height:1.5}
.entity strong{display:block;color:var(--navy)}
.arrow{text-align:center;color:var(--orange);font-size:1.2rem}
.opportunity{display:grid;gap:9px}
.opp-row{display:grid;grid-template-columns:29px 1fr auto;align-items:center;gap:10px;padding:11px;background:#f5f1e8;border-radius:10px}
.opp-row b{display:grid;place-items:center;width:27px;height:27px;border-radius:50%;background:var(--navy);color:#fff;font-size:.72rem}
.opp-row span{font-size:.79rem;font-weight:700}
.opp-row small{font-size:.67rem;color:var(--teal);border:1px solid #9cc7c1;border-radius:999px;padding:3px 7px}
.timeline{display:grid;grid-template-columns:repeat(6,1fr);gap:8px}
.time-item{border-top:4px solid var(--teal);padding:12px 8px 8px;background:#f7f3eb;min-height:132px}
.time-item:nth-child(3n){border-color:var(--orange)}
.time-item b{display:block;font-size:.72rem;color:var(--orange);margin-bottom:6px}
.time-item span{display:block;font-size:.73rem;line-height:1.5}
.mode-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.mode{padding:14px;border:1px solid var(--line);border-radius:12px;background:#f9f6f0}
.mode b{font-size:.78rem;display:block;margin-bottom:7px}
.mode p{font-size:.69rem;color:var(--muted);line-height:1.5;margin:0}
.route{display:grid;grid-template-columns:repeat(5,1fr);gap:0;margin-top:12px}
.phase{padding:15px 12px;background:var(--navy);color:#eaf4f2;min-height:138px;position:relative}
.phase:nth-child(even){background:var(--navy-2)}
.phase:not(:last-child):after{content:"";position:absolute;right:-8px;top:50%;border-left:8px solid currentColor;border-top:8px solid transparent;border-bottom:8px solid transparent;z-index:2;color:var(--navy)}
.phase:nth-child(even):after{color:var(--navy-2)}
.phase b{font-size:.76rem;color:#f0a26d}
.phase span{display:block;font-size:.7rem;line-height:1.55;margin-top:7px}
.legend{display:flex;flex-wrap:wrap;gap:8px;margin:48px 0 8px}
.tag{font-size:.68rem;font-weight:750;padding:4px 9px;border-radius:999px;border:1px solid}
.tag.fact-tag{color:#236660;border-color:#79aaa5;background:#e2efec}
.tag.management-tag{color:#7b5c27;border-color:#c8a761;background:#f3ead5}
.tag.judgment-tag{color:#8d462f;border-color:#d68c6d;background:#f6e3d9}
.tag.action-tag{color:#394e69;border-color:#8ca0ba;background:#e8edf3}
.research{margin-top:16px}
.research h2{font-family:var(--serif);font-size:clamp(1.7rem,3.2vw,2.65rem);line-height:1.32;margin:3.4em 0 .85em;padding-top:20px;border-top:1px solid var(--line)}
.research h2:first-child{margin-top:1.2em}
.research h3{font-size:1.2rem;line-height:1.45;margin:2.3em 0 .75em;color:var(--navy)}
.research p{font-size:.94rem;color:#314d5b;margin:.8em 0}
.research strong{color:#102f43}
.research ol,.research ul{padding-left:1.4rem;font-size:.92rem;color:#314d5b}
.research li{margin:.45em 0}
.research .insight,.research .recommendation,.research .fact,.research .caveat{padding:16px 18px;border-radius:0 11px 11px 0;background:#fff;border-left:4px solid}
.research .insight{border-color:var(--orange);background:#fbefe7}
.research .recommendation{border-color:#587493;background:#e9eff4}
.research .fact{border-color:var(--teal);background:#e7f1ee}
.research .caveat{border-color:var(--gold);background:#f5eddc}
.research .source-entry{font-size:.82rem;padding:13px 0;border-bottom:1px dotted var(--line);scroll-margin-top:20px}
.source-entry:target{background:#fff2c8;border-radius:8px;padding:13px 10px;animation:flash 1.4s ease}
@keyframes flash{from{background:#ffd979}to{background:#fff2c8}}
.source-ref{white-space:nowrap;font-size:.86em;font-weight:700;text-decoration:none;color:#2a6d68}
.external{font-size:.65em;margin-left:3px;vertical-align:top}
.table-scroll{overflow-x:auto;margin:18px 0 24px;border:1px solid var(--line);border-radius:13px;background:var(--white);box-shadow:0 6px 18px rgba(28,46,58,.04)}
table{border-collapse:collapse;width:100%;min-width:650px;font-size:.79rem;line-height:1.55}
th{background:var(--navy);color:#fff;text-align:left;font-weight:700;padding:11px 12px;vertical-align:top}
td{padding:11px 12px;border-top:1px solid #e3ddd2;vertical-align:top;color:#334e5b}
tbody tr:nth-child(even){background:#f8f5ef}
.provenance{margin-top:74px;padding:34px;border-radius:var(--radius);background:var(--navy);color:#d7e6e4}
.provenance h2{font-family:var(--serif);font-size:1.45rem;margin:0 0 12px;color:#fff}
.provenance p{font-size:.78rem;line-height:1.7;color:#c5d7d6;margin:6px 0}
.provenance code{background:rgba(255,255,255,.09);padding:2px 6px;border-radius:5px;color:#fff}
.backtop{display:inline-flex;margin-top:12px;color:#f0a26d}
footer{text-align:center;color:#78868d;padding:0 20px 46px;font-size:.7rem}
@media(max-width:1000px){
  .layout{grid-template-columns:1fr;gap:20px;padding-top:30px}
  .sidebar{position:relative;top:auto}
  .sidebar nav{display:flex;width:100%;max-width:100%;overflow-x:auto;border-left:0;border-bottom:1px solid var(--line);padding-bottom:8px}
  .sidebar nav a{min-width:max-content;border-left:0;margin:0;border-bottom:2px solid transparent}
  .sidebar nav a.active{border-bottom-color:var(--orange)}
  .sidebar-note{display:none}
  .metric-grid{grid-template-columns:repeat(3,1fr)}
  .timeline{grid-template-columns:repeat(3,1fr)}
  .mode-grid{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:720px){
  .hero{min-height:auto}
  .hero-inner{padding:72px 0 54px}
  .hero h1{font-size:clamp(2.35rem,13vw,4.2rem)}
  .hero-action small{width:100%}
  .layout{width:min(100% - 24px,1240px)}
  .decision{padding:25px 20px}
  .decision:after{font-size:2.2rem}
  .metric-grid{grid-template-columns:repeat(2,1fr);gap:8px}
  .metric{min-height:118px;padding:15px 12px}
  .visual-grid{grid-template-columns:1fr}
  .visual.wide{grid-column:auto}
  .entity-flow{grid-template-columns:1fr}
  .arrow{transform:rotate(90deg)}
  .timeline{grid-template-columns:1fr 1fr}
  .mode-grid{grid-template-columns:1fr}
  .route{grid-template-columns:1fr}
  .phase{min-height:auto}
  .phase:not(:last-child):after{right:50%;top:auto;bottom:-8px;transform:rotate(90deg)}
  .research h2{font-size:1.65rem;margin-top:2.6em}
  .research h3{font-size:1.08rem}
  .research p,.research li{font-size:.9rem}
  .table-scroll:before{content:"← 左右滑动查看完整表格 →";display:block;padding:8px 10px;color:#846d4a;background:#f2e7d3;font-size:.68rem}
  .provenance{padding:25px 20px}
}
@media(max-width:430px){
  .metric-grid{grid-template-columns:1fr 1fr}
  .metric strong{font-size:1.45rem}
  .timeline{grid-template-columns:1fr}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
@media print{
  body{background:#fff}.progress,.sidebar,.hero-action{display:none}.hero{min-height:auto;background:#fff;color:#000;border-bottom:2px solid #000}.hero:before,.hero:after{display:none}.hero-inner{padding:30px 0}.hero h1,.hero-lead{color:#000}.layout{display:block;width:100%;padding:20px}.decision,.visual,.table-scroll{box-shadow:none;break-inside:avoid}.research h2{break-after:avoid}.provenance{background:#fff;color:#000;border:1px solid #000}
}
</style>
</head>
<body>
<a class="skip" href="#main">跳到正文</a>
<div class="progress" aria-hidden="true"><span id="progress-bar"></span></div>
<header class="hero" id="top">
  <div class="hero-inner">
    <div class="eyebrow">Zhejiang IDC &amp; AI Compute · Cooperation Diligence</div>
    <h1>平湖润泽：<br><em>浙江IDC与算力</em><br>合作落地报告</h1>
    <p class="hero-lead">值得合作，但要围绕实际订单与总部决策开展。用实体、资产、客户、合同和现金流穿透合作机会。</p>
    <div class="hero-meta">
      <span>研究截至 2026-09-21</span><span>公开资料研究版</span><span>约 22,800 字</span>
      <span>10章 + 2附录</span><span>27项公开来源</span><span>商务拓展 · 合作筛选 · 项目尽调</span>
    </div>
    <div class="hero-action"><a href="#decision">先看决策摘要 ↓</a><small>无 Word 下载 · 所有来源可追溯</small></div>
  </div>
</header>

<div class="layout" id="main">
  <aside class="sidebar" aria-label="页面目录">
    <div class="sidebar-label">Research map</div>
    <nav>__NAV__</nav>
    <div class="sidebar-note">阅读提示：来源编号可点击跳到附录。页面中的事实、管理层表述、报告判断和合作建议按文字标签与色彩共同区分。</div>
  </aside>

  <main class="content">
    <section class="decision" id="decision">
      <div class="kicker">Executive decision brief</div>
      <h2>合作价值已经出现，真正的门槛是把价值落到一个可收费、可验收、可回款的具体项目。</h2>
      <p>平湖已形成“本地基础设施与项目执行 + 集团客户、技术、资金和运营能力”的商业体系。园区能帮助识别工程、用电和运维需求；设备采购、算力产品、联合获客和资本安排通常仍需集团职能确认。</p>
      <div class="first-move"><b>建议的首个行动</b>用两周完成“目标楼栋或集群—需求负责人—实际签约主体—验收及付款路径”核实，再提交一份带预算、测试指标和退出条件的付费试点建议书。</div>
    </section>

    <section class="metric-grid" aria-label="关键数据全景">
      <div class="metric"><strong>100MW</strong><span>2025年上半年披露的新一代智算中心交付规模</span><small>交付不等于全部满载计费 · S13</small></div>
      <div class="metric"><strong>101.25MW</strong><span>审核回复列示的平湖B1规划功率</span><small>不同披露口径不强行合并 · S03</small></div>
      <div class="metric"><strong>25.11亿元</strong><span>审核回复列示的平湖B1项目投资</span><small>不是完整GPU集群总成本 · S03</small></div>
      <div class="metric"><strong>19.95亿元</strong><span>集团2026年上半年AIDC收入</span><small>已超过IDC收入 · S01</small></div>
      <div class="metric"><strong>17.51亿元</strong><span>集团2026年上半年IDC收入</span><small>合并口径，不是平湖收入 · S01</small></div>
      <div class="metric"><strong>81.74%</strong><span>AIDC折旧摊销占该业务成本的重算比例</span><small>设备利用率与寿命是关键</small></div>
      <div class="metric"><strong>58.07%</strong><span>IDC电力占该业务成本的重算比例</span><small>电价和上架爬坡直接影响经济性</small></div>
      <div class="metric"><strong>8.18亿元</strong><span>浙江泽悦2026年上半年营业收入</span><small>项目公司口径 · S01/S29</small></div>
      <div class="metric"><strong>−1.37亿元</strong><span>浙江泽悦同期经营现金流净额</span><small>需穿透回款与结算，不等于违约</small></div>
      <div class="metric"><strong>89.19%</strong><span>浙江泽悦2026年上半年末资产负债率</span><small>签约与付款主体需明确 · S29</small></div>
      <div class="metric"><strong>3条</strong><span>优先验证的合作路径</span><small>设备配套 · 集群优化 · 带客交付</small></div>
      <div class="metric"><strong>90天</strong><span>从需求核实到扩容订单的建议周期</span><small>每阶段均设置进入与停止条件</small></div>
    </section>

    <section class="visual-grid" aria-label="关键关系与路线图">
      <div class="visual">
        <h3>商务决策双线</h3><div class="caption">现场通过不等于获得总部采购或销售授权</div>
        <div class="entity-flow">
          <div class="entity"><strong>平湖园区 / 浙江泽悦</strong>识别需求 · 现场执行 · 运行反馈</div>
          <div class="arrow">⇄</div>
          <div class="entity"><strong>集团总部职能</strong>技术 · 市场 · 采购 · 资金 · 售后</div>
          <div class="arrow">⇄</div>
          <div class="entity"><strong>客户 / 运营商</strong>预算 · 合同 · 网络 · 验收 · 回款</div>
        </div>
      </div>
      <div class="visual">
        <h3>合作机会优先级</h3><div class="caption">优先解决明确瓶颈，避免先采购后找客户</div>
        <div class="opportunity">
          <div class="opp-row"><b>1</b><span>高密度机电、液冷、网络与存储</span><small>优先验证</small></div>
          <div class="opp-row"><b>2</b><span>集群稳定性、性能与能效优化</span><small>优先验证</small></div>
          <div class="opp-row"><b>3</b><span>带真实客户的联合算力交付</span><small>有条件优先</small></div>
          <div class="opp-row"><b>4</b><span>设备联投、融资租赁或项目股权</span><small>穿透后审慎</small></div>
        </div>
      </div>
      <div class="visual wide">
        <h3>平湖项目证据时间线</h3><div class="caption">建成、送电、联调、验收、上架、收入和回款是不同里程碑</div>
        <div class="timeline">
          <div class="time-item"><b>2020</b><span>项目引进；浙江泽悦成立</span></div>
          <div class="time-item"><b>2023.02</b><span>一期A1、A2通过竣工验收</span></div>
          <div class="time-item"><b>2023 Q3</b><span>平湖部署算力模组并开展国产芯片测试调优</span></div>
          <div class="time-item"><b>2025 H1</b><span>100MW新一代智算中心交付并启动上架</span></div>
          <div class="time-item"><b>2025.11</b><span>B区整体竣工，披露建筑面积约14.46万平方米</span></div>
          <div class="time-item"><b>2026.09</b><span>地方报道仍描述三期加快建设，须逐批核验</span></div>
        </div>
      </div>
      <div class="visual wide">
        <h3>四种模式必须分别核算</h3><div class="caption">收入稳定性、资本压力和主要风险并不相同</div>
        <div class="mode-grid">
          <div class="mode"><b>IDC托管 / 批发</b><p>主要看上架爬坡、电价、客户集中和续约；电力是重要成本。</p></div>
          <div class="mode"><b>AIDC设备 / 产品交付</b><p>主要看供应链、验收、存货和应收；收入可能集中在交付节点。</p></div>
          <div class="mode"><b>自持算力服务</b><p>主要看可计费利用率、租价、稳定性和设备经济寿命。</p></div>
          <div class="mode"><b>成熟资产循环</b><p>主要看资产适格性、运营数据、审批和市场条件；不能照搬到GPU。</p></div>
        </div>
      </div>
      <div class="visual wide">
        <h3>90天合作落地路线</h3><div class="caption">每一阶段都要求明确材料和进入条件；达不到就收缩或停止</div>
        <div class="route">
          <div class="phase"><b>01–15天</b><span>确认场景、负责人、合同与预算路径</span></div>
          <div class="phase"><b>16–30天</b><span>确定基线、范围、报价、验收和退出</span></div>
          <div class="phase"><b>31–60天</b><span>签约试点，保留日志，控制变更</span></div>
          <div class="phase"><b>61–75天</b><span>联合验收，确认生产价值和经济性</span></div>
          <div class="phase"><b>76–90天</b><span>对明确扩容范围报价并形成正式订单</span></div>
        </div>
      </div>
    </section>

    <div class="legend" aria-label="内容证据标签">
      <span class="tag fact-tag">已披露事实</span><span class="tag management-tag">管理层表述</span>
      <span class="tag judgment-tag">本报告判断</span><span class="tag action-tag">合作建议 / 情景假设</span>
    </div>
    <article class="research">__ARTICLE__</article>

    <section class="provenance">
      <h2>来源与生成说明</h2>
      <p>内容来自《平湖润泽：浙江IDC与算力产业及合作落地调研报告》公开资料研究版，研究截至 2026年9月21日。网页保留原报告十章、附录A、附录B和全部来源编号。</p>
      <p>页面用于商务拓展、合作筛选与项目尽调。它没有执行商业接洽、取得非公开合同或核查园区实时系统；合作建议、时间表和测算均需在具体项目中重新验证。</p>
      <p>公开地址：<code>ewangwo.github.io/lff-reports/reports/pinghu-runze-zhejiang-idc-compute-cooperation-2026.html</code></p>
      <a class="backtop" href="#top">返回顶部 ↑</a>
    </section>
  </main>
</div>
<footer>Independent research · Public-source diligence · 2026</footer>
<script>
const progressBar=document.getElementById('progress-bar');
const navLinks=[...document.querySelectorAll('.sidebar nav a')];
const sections=navLinks.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
function updatePage(){
  const max=document.documentElement.scrollHeight-window.innerHeight;
  progressBar.style.width=(max>0?window.scrollY/max*100:0)+'%';
  let active=sections[0];
  for(const section of sections){if(section.getBoundingClientRect().top<=130) active=section}
  navLinks.forEach(a=>a.classList.toggle('active',active&&a.getAttribute('href')==='#'+active.id));
}
addEventListener('scroll',updatePage,{passive:true});
addEventListener('resize',updatePage,{passive:true});
updatePage();
</script>
</body>
</html>
"""
    page = page.replace("__NAV__", nav).replace("__ARTICLE__", article)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(page):,} chars)")


if __name__ == "__main__":
    main()
