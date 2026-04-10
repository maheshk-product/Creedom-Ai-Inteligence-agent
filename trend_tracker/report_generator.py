"""
Trend Report Generator.

Reads collected trend data and generates human-readable Markdown reports
(suitable for email, Slack, or a simple web dashboard).
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import config
from .data_storage import load_records

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------ #
#  Analytics helpers                                                   #
# ------------------------------------------------------------------ #

def _aggregate_by_topic(
    records: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Group records by topic and compute aggregate engagement metrics."""
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for rec in records:
        topic = rec.get("topic", "unknown")
        grouped[topic].append(rec)

    summary: Dict[str, Dict[str, Any]] = {}
    for topic, items in grouped.items():
        total_views = sum(int(i.get("view_count", 0) or 0) for i in items)
        total_likes = sum(int(i.get("like_count", 0) or 0) for i in items)
        total_comments = sum(int(i.get("comment_count", 0) or 0) for i in items)
        sources = list({i.get("source", "") for i in items})
        summary[topic] = {
            "count": len(items),
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "sources": sources,
            "top_items": _top_items(items, n=3),
        }
    return summary


def _top_items(
    items: List[Dict[str, Any]], n: int = 3
) -> List[Dict[str, Any]]:
    """Return the top-n items sorted by engagement (views + likes)."""
    def _score(item: Dict[str, Any]) -> int:
        return int(item.get("view_count", 0) or 0) + int(item.get("like_count", 0) or 0)

    return sorted(items, key=_score, reverse=True)[:n]


def _format_number(n: int) -> str:
    """Format large numbers with K/M suffixes for readability."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


# ------------------------------------------------------------------ #
#  Markdown report builder                                             #
# ------------------------------------------------------------------ #

def _build_markdown_report(
    date_str: str,
    summary: Dict[str, Dict[str, Any]],
    total_records: int,
) -> str:
    """Render a Markdown trend report from aggregated data."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: List[str] = [
        f"# 📊 Trend Intelligence Report – {date_str}",
        f"",
        f"*Generated: {now_utc}*  |  *Total records collected: {total_records}*",
        f"",
        f"---",
        f"",
    ]

    if not summary:
        lines.append("⚠️ No trend data available for this date.")
        return "\n".join(lines)

    for topic, data in summary.items():
        lines += [
            f"## 🔥 #{topic}",
            f"",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Items collected | {data['count']} |",
            f"| Total views | {_format_number(data['total_views'])} |",
            f"| Total likes | {_format_number(data['total_likes'])} |",
            f"| Total comments | {_format_number(data['total_comments'])} |",
            f"| Data sources | {', '.join(data['sources']) or 'N/A'} |",
            f"",
            f"### Top Content",
            f"",
        ]
        for rank, item in enumerate(data["top_items"], start=1):
            title = item.get("title") or item.get("reel_id") or "N/A"
            url = item.get("url", "")
            views = _format_number(int(item.get("view_count", 0) or 0))
            likes = _format_number(int(item.get("like_count", 0) or 0))
            lines.append(
                f"{rank}. **[{title}]({url})**  "
                f"👁 {views} views  ❤️ {likes} likes"
            )
        lines.append("")
        lines.append("---")
        lines.append("")

    lines += [
        "## 💡 Next Steps",
        "",
        "- Review the top-performing content above for inspiration.",
        "- Increase tracking topics in `.env` → `TRENDING_TOPICS`.",
        "- Share this report with your team or schedule it for daily email delivery.",
        "",
    ]
    return "\n".join(lines)


# ------------------------------------------------------------------ #
#  Public API                                                          #
# ------------------------------------------------------------------ #

def generate_report(
    date_str: Optional[str] = None,
    data_dir: Optional[Path] = None,
    report_dir: Optional[Path] = None,
) -> Path:
    """
    Generate a Markdown trend report for a given date.

    Loads data from ``data_dir``, aggregates it, and writes a ``.md``
    report file to ``report_dir``.

    Args:
        date_str:   YYYY-MM-DD date string. Defaults to today (UTC).
        data_dir:   Directory containing trend data. Defaults to ``config.DATA_DIR``.
        report_dir: Directory to write the report into. Defaults to ``config.REPORT_DIR``.

    Returns:
        Path to the generated report file.
    """
    if date_str is None:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if report_dir is None:
        report_dir = config.REPORT_DIR

    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)

    records = load_records(data_dir=data_dir, date_str=date_str)
    logger.info("Generating report for %s (%d records)", date_str, len(records))

    summary = _aggregate_by_topic(records)
    markdown = _build_markdown_report(date_str, summary, len(records))

    report_path = report_dir / f"report_{date_str}.md"
    report_path.write_text(markdown, encoding="utf-8")

    logger.info("Report written to %s", report_path)
    return report_path
