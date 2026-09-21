#!/usr/bin/env python3
"""Static completeness checks for the public Pinghu Runze report."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "reports" / "pinghu-runze-zhejiang-idc-compute-cooperation-2026.html"


class Inspector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.hrefs: list[str] = []
        self.text: list[str] = []
        self.tags: dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if values.get("href"):
            self.hrefs.append(values["href"] or "")

    def handle_data(self, data: str) -> None:
        self.text.append(data)


def main() -> None:
    raw = PAGE.read_text(encoding="utf-8")
    inspector = Inspector()
    inspector.feed(raw)
    visible = " ".join(inspector.text)

    required_ids = {
        "decision", "chapter-1", "chapter-2", "chapter-3", "chapter-4",
        "chapter-5", "chapter-6", "chapter-7", "chapter-8", "chapter-9",
        "chapter-10", "appendix-a", "appendix-b",
    }
    assert required_ids <= inspector.ids, required_ids - inspector.ids

    source_ids = {value for value in inspector.ids if value.startswith("source-s")}
    source_hrefs = {value[1:] for value in inspector.hrefs if value.startswith("#source-s")}
    assert len(source_ids) == 27, f"expected 27 source entries, found {len(source_ids)}"
    assert source_hrefs == source_ids, f"source references differ: {source_hrefs ^ source_ids}"

    missing_targets = {
        href[1:] for href in inspector.hrefs
        if href.startswith("#") and href[1:] not in inspector.ids
    }
    assert not missing_targets, f"missing fragment targets: {sorted(missing_targets)}"

    required_text = [
        "平湖润泽：浙江IDC与算力产业及合作落地调研报告",
        "值得合作，但要围绕实际订单与总部决策开展",
        "四条流向决定合作是否成立",
        "应优先取得的20项信息",
        "附录A：资料来源、获取状态与用途",
        "附录B：关键结论的证据强度",
        "所有合作方案、时间表与测算均为后续推进建议",
    ]
    for phrase in required_text:
        assert phrase in visible, f"missing required text: {phrase}"

    external = [href for href in inspector.hrefs if href.startswith("http")]
    assert len(external) >= 27, f"expected at least 27 external links, found {len(external)}"
    assert inspector.tags.get("table", 0) >= 10, "expected at least 10 data tables"
    assert 'name="viewport"' in raw
    assert "@media(max-width:720px)" in raw
    assert "@media print" in raw
    assert "prefers-reduced-motion" in raw
    assert "/Users/" not in raw
    assert ".docx" not in raw.lower()
    assert "TBD" not in raw and "TODO" not in raw
    print(
        f"PASS: {len(source_ids)} sources, {inspector.tags.get('table', 0)} tables, "
        f"{len(external)} external links, {len(raw):,} characters"
    )


if __name__ == "__main__":
    main()
