"""Write a self-contained review artifact; no online hosting or desktop control."""

import base64
import json
from pathlib import Path

from fixture import OUT


def table():
    data = json.loads((OUT / "packed-summary.json").read_text())
    labels = dict(
        current="Current", improved="Experimental", routed_endpoints="ROUTED — endpoints only"
    )
    rows = []
    for key, label in labels.items():
        rows.append(table_row(label, data[key]))
    return "".join(rows)


def table_row(label, data):
    path, total = data["path_ms"]["median"], data["total_ms"]["median"]
    low, high = data["total_ms"]["minimum"], data["total_ms"]["maximum"]
    return (
        f"<tr><td>{label}</td><td>{path:,.2f} ms</td><td>{total:,.2f} ms</td>"
        f"<td>{low:,.2f}–{high:,.2f} ms</td></tr>"
    )


def pictures():
    return {
        p.stem: "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
        for p in OUT.glob("*.png")
    }


def run():
    source = Path(__file__).with_name("report_template.html").read_text(encoding="utf-8-sig")
    html = source.replace("TABLE_ROWS", table()).replace("PICTURES", json.dumps(pictures()))
    (OUT / "review.html").write_text(html, encoding="utf-8")
    print(OUT / "review.html")


if __name__ == "__main__":
    run()
