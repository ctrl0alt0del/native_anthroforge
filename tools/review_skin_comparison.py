"""Package matched renders and measured results into a local, read-only comparison page."""

import html
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

VIEWS = ("front", "back", "left", "right", "oblique")
STYLE = """<style>
body{background:#1c2229;color:#e1e5e9;font:16px/1.5 Segoe UI,sans-serif;margin:24px}
h1{font-size:28px}h2{text-transform:capitalize}a{color:#8cc6df}.note{color:#b4bec7}
.views{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}figure{margin:0}
img{width:100%}figcaption{font-weight:600;padding:8px 0}table{border-collapse:collapse}
td,th{padding:8px 24px 8px 0;text-align:left;border-bottom:1px solid #45505b}
section{margin-top:36px}nav{position:sticky;top:0;background:#1c2229;padding:12px 0}
nav a{margin-right:24px}</style>"""
INTRO = """<h1>Whole-body draft skin — Blender versus AnthroForge</h1>
<p>58 SCP surfaces + 96 authored tissues. {geometry:,} output triangles.
Every physical contributor in the saved assembly is included;
no extra opposite-side muscles were synthesized.</p>
<p><strong>Geometry and all six common binding arrays exactly equal: {same}.</strong>
Identical accepted world-space anatomy, settings, units and cameras in both engines.</p>
<p>The mesh has topology warnings: it is not watertight or orientable.
These are shared output defects, not evidence of a clean final skin.
Source coverage and protected-gap checks pass.</p>
<p class="note">Source: {source}<br>
Draft generation only: fields, envelope, validation and bindings.
Excludes project loading, topology generation, final-skin deformation, export and rendering.</p>"""
MEASUREMENTS = """<table><tr><th>Engine</th><th>Median</th><th>Range</th>
<th>Peak resident memory</th></tr>{rows}</table>
<p class="note">Three fresh processes per engine, serial counterbalanced order.
OS process peaks include host overhead; Blender runs in its actual 5.0.1 worker host.
Profiling and rendering are off during timing.</p>"""


def font(size):
    return ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", size)


def strip(folder, view):
    canvas = Image.new("RGB", (2000, 1300), "#171d25")
    draw = ImageDraw.Draw(canvas)
    for index, (name, title) in enumerate(
        (("blender", "Blender addon"), ("app", "Standalone app"))
    ):
        with Image.open(folder / f"{name}-{view}.png") as image:
            canvas.paste(image.convert("RGB"), (index * 1000, 100))
        draw.text((index * 1000 + 28, 20), title + " | " + view, font=font(36), fill="white")
    canvas.save(folder / f"comparison-{view}.png")


def performance_rows(report):
    return "".join(
        f"<tr><td>{title}</td><td>{report[name]['seconds']['median']:.2f} s</td>"
        f"<td>{report[name]['seconds']['minimum']:.2f}–"
        f"{report[name]['seconds']['maximum']:.2f} s</td>"
        f"<td>{report[name]['peak_rss']['median'] / 1024**3:.2f} GiB</td></tr>"
        for name, title in (
            ("blender", "Blender 5.0.1 addon worker"),
            ("app", "Standalone native core"),
        )
    )


def views_section():
    return "".join(
        f'<section id="{view}"><h2>{view.title()}</h2>'
        f'<div class="views">{panels(view)}</div></section>'
        for view in VIEWS
    )


def panels(view):
    return "".join(
        f'<figure><figcaption>{title}</figcaption><a href="{name}-{view}.png">'
        f'<img loading="lazy" src="{name}-{view}.png" alt="{title}, {view}"></a></figure>'
        for name, title in (
            ("inputs", "Accepted anatomy"),
            ("blender", "Blender addon"),
            ("app", "App"),
        )
    )


def introduction(report):
    same = all(row["exact"] for row in report["comparison"].values())
    geometry = report["comparison"]["faces"]["first_shape"][0]
    source = html.escape(report["capture"]["project"])
    return INTRO.format(geometry=geometry, same=same, source=source)


def page(report):
    head = '<!doctype html><html lang="en"><meta charset="utf-8">'
    title = "<title>Whole-body skin comparison</title>"
    body = introduction(report) + MEASUREMENTS.format(rows=performance_rows(report))
    return head + title + STYLE + body + navigation() + views_section() + "</html>"


def navigation():
    links = "".join(f'<a href="#{view}">{view.title()}</a>' for view in VIEWS)
    return f'<nav>{links}<a href="comparison.json">Raw measurements</a></nav>'


def main():
    folder = Path(sys.argv[1])
    report = json.loads((folder / "comparison.json").read_text())
    for view in ("front", "back", "left", "right", "oblique"):
        strip(folder, view)
    (folder / "review.html").write_text(page(report), encoding="utf-8")


if __name__ == "__main__":
    main()
