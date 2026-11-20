"""Compare separate chaining and linear probing on the same deterministic keys."""

import csv
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.probe_experiment import random_keys
from src.hash_table import HashTable
from src.linear_probing import LinearProbingHashTable


CAPACITY = 1000
LOAD_FACTORS = tuple(step / 10 for step in range(1, 10))


def measure() -> list[tuple[float, ...]]:
    keys = random_keys(round(CAPACITY * 0.9), 2026)
    misses = random_keys(round(CAPACITY * 0.9), 2027, excluded=keys)
    results = []
    for load_factor in LOAD_FACTORS:
        entry_count = round(CAPACITY * load_factor)
        active_keys = keys[:entry_count]
        chaining = HashTable(initial_capacity=CAPACITY, max_load_factor=None)
        linear = LinearProbingHashTable(initial_capacity=CAPACITY, max_load_factor=None)
        for index, key in enumerate(active_keys):
            chaining.put(key, index)
            linear.put(key, index)
        chaining.reset_comparisons()
        linear.reset_comparisons()

        chain_success = 0
        linear_success = 0
        for key in active_keys:
            chaining.get(key)
            chain_success += chaining.last_comparisons
            linear.get(key)
            linear_success += linear.last_probes

        chain_failure = 0
        linear_failure = 0
        for key in misses:
            chaining.get(key)
            chain_failure += chaining.last_comparisons
            linear.get(key)
            linear_failure += linear.last_probes

        results.append(
            (
                load_factor,
                entry_count,
                chain_success / entry_count,
                1 + load_factor / 2,
                chain_failure / len(misses),
                load_factor,
                linear_success / entry_count,
                0.5 * (1 + 1 / (1 - load_factor)),
                linear_failure / len(misses),
                0.5 * (1 + 1 / ((1 - load_factor) ** 2)),
            )
        )
    return results


def write_csv(results: list[tuple[float, ...]]) -> None:
    headers = (
        "load_factor",
        "entries",
        "chaining_success_measured",
        "chaining_success_theory",
        "chaining_failure_measured",
        "chaining_failure_theory",
        "linear_success_measured",
        "linear_success_theory",
        "linear_failure_measured",
        "linear_failure_theory",
    )
    with (ROOT / "experiments" / "linear_probing_results.csv").open(
        "w", newline="", encoding="utf-8"
    ) as output:
        writer = csv.writer(output)
        writer.writerow(headers)
        for row in results:
            writer.writerow(
                (f"{row[0]:.1f}", row[1], *(f"{value:.4f}" for value in row[2:]))
            )


def write_markdown(results: list[tuple[float, ...]]) -> None:
    lines = [
        "# Chaining vs. linear probing",
        "",
        f"Capacity: {CAPACITY}; same deterministic key set at each load factor; "
        "900 unsuccessful queries per row.",
        "",
        "| α | n | Chain hit (obs/theory) | Chain miss (obs/theory) "
        "| Linear hit (obs/theory) | Linear miss (obs/theory) |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in results:
        lines.append(
            f"| {row[0]:.1f} | {row[1]} | {row[2]:.3f}/{row[3]:.3f} "
            f"| {row[4]:.3f}/{row[5]:.3f} | {row[6]:.3f}/{row[7]:.3f} "
            f"| {row[8]:.3f}/{row[9]:.3f} |"
        )
    lines.extend(
        (
            "",
            "Chaining theory: successful `1 + α/2`, unsuccessful `α`. "
            "Linear-probing theory: successful `0.5(1 + 1/(1-α))`, "
            "unsuccessful `0.5(1 + 1/(1-α)^2)`.",
            "",
            "The linear-probing estimates rise sharply near full capacity because "
            "contiguous occupied runs cause primary clustering. Chaining grows more "
            "gradually; finite deterministic keys and discrete bucket occupancy explain "
            "small departures from the idealized uniform-hashing estimates.",
            "",
        )
    )
    (ROOT / "experiments" / "linear_probing_results.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def write_svg(results: list[tuple[float, ...]]) -> None:
    width, height = 1000, 610
    panel_top, panel_bottom = 125, 500
    panels = (
        ("Successful lookups", 2, 3, 6, 7, 6),
        ("Unsuccessful lookups", 4, 5, 8, 9, 55),
    )
    colors = ("#1769aa", "#1769aa", "#d84315", "#d84315")
    dashed = (False, True, False, True)
    labels = (
        "Chaining measured",
        "Chaining theory",
        "Linear measured",
        "Linear theory",
    )
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="500" y="35" text-anchor="middle" font-family="sans-serif" font-size="21">Hash table lookup cost vs. load factor</text>',
    ]
    for index, label in enumerate(labels):
        x1 = 90 + index * 235
        color = colors[index]
        dash = ' stroke-dasharray="7 5"' if dashed[index] else ""
        svg.append(f'<line x1="{x1}" y1="75" x2="{x1 + 28}" y2="75" stroke="{color}" stroke-width="2"{dash}/>')
        svg.append(f'<text x="{x1 + 34}" y="79" font-family="sans-serif" font-size="12">{label}</text>')

    for panel_index, (title, first, second, third, fourth, maximum) in enumerate(panels):
        left = 75 + panel_index * 475
        right = left + 410
        top, bottom = panel_top, panel_bottom
        x = lambda alpha: left + (alpha - 0.1) / 0.8 * (right - left)
        y = lambda value: bottom - value / maximum * (bottom - top)
        svg.append(f'<text x="{(left + right) / 2:.1f}" y="105" text-anchor="middle" font-family="sans-serif" font-size="15">{title}</text>')
        tick_step = maximum / 5
        for tick in range(6):
            value = tick * tick_step
            py = y(value)
            svg.append(f'<line x1="{left}" y1="{py:.1f}" x2="{right}" y2="{py:.1f}" stroke="#dddddd"/>')
            svg.append(f'<text x="{left - 8}" y="{py + 4:.1f}" text-anchor="end" font-family="sans-serif" font-size="10">{value:g}</text>')
        for tick in range(1, 10):
            alpha = tick / 10
            px = x(alpha)
            svg.append(f'<line x1="{px:.1f}" y1="{top}" x2="{px:.1f}" y2="{bottom}" stroke="#eeeeee"/>')
            if tick % 2 == 1:
                svg.append(f'<text x="{px:.1f}" y="{bottom + 18}" text-anchor="middle" font-family="sans-serif" font-size="10">{alpha:.1f}</text>')
        svg.extend(
            (
                f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#333"/>',
                f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#333"/>',
                f'<text x="{(left + right) / 2:.1f}" y="{bottom + 42}" text-anchor="middle" font-family="sans-serif" font-size="12">Load factor α</text>',
            )
        )
        for series_index, column in enumerate((first, second, third, fourth)):
            points = " ".join(
                f"{x(row[0]):.1f},{y(row[column]):.1f}" for row in results
            )
            dash = ' stroke-dasharray="7 5"' if dashed[series_index] else ""
            svg.append(
                f'<polyline points="{points}" fill="none" stroke="{colors[series_index]}" '
                f'stroke-width="2"{dash}/>'
            )
    svg.append("</svg>")
    (ROOT / "experiments" / "linear_probing_comparison.svg").write_text(
        "\n".join(svg), encoding="utf-8"
    )


def _pdf_text(x: float, y: float, size: float, text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return f"BT /F1 {size:g} Tf 1 0 0 1 {x:g} {y:g} Tm ({escaped}) Tj ET\n"


def _pdf_panel(
    results: list[tuple[float, ...]],
    title: str,
    columns: tuple[int, int, int, int],
    left: float,
    bottom: float,
    width: float,
    height: float,
    maximum: float,
) -> str:
    output = [_pdf_text(left + width / 2 - 45, bottom + height + 18, 9, title)]
    x = lambda alpha: left + (alpha - 0.1) / 0.8 * width
    y = lambda value: bottom + value / maximum * height
    output.append("0.75 G 0.4 w\n")
    for tick in range(6):
        value = maximum * tick / 5
        py = y(value)
        output.append(f"{left:g} {py:g} m {left + width:g} {py:g} l S\n")
        output.append(_pdf_text(left - 18, py - 2, 6, f"{value:g}"))
    output.append("0 G 0.8 w\n")
    output.append(f"{left:g} {bottom:g} m {left + width:g} {bottom:g} l S\n")
    output.append(f"{left:g} {bottom:g} m {left:g} {bottom + height:g} l S\n")
    colors = ((0.09, 0.41, 0.67), (0.09, 0.41, 0.67), (0.85, 0.26, 0.08), (0.85, 0.26, 0.08))
    for series_index, column in enumerate(columns):
        red, green, blue = colors[series_index]
        output.append(f"{red:g} {green:g} {blue:g} RG 1.2 w\n")
        output.append("[4 3] 0 d\n" if series_index in (1, 3) else "[] 0 d\n")
        points = [(x(row[0]), y(row[column])) for row in results]
        output.append(f"{points[0][0]:g} {points[0][1]:g} m\n")
        for px, py in points[1:]:
            output.append(f"{px:g} {py:g} l\n")
        output.append("S\n")
    output.append("[] 0 d\n0 G\n")
    return "".join(output)


def write_pdf_report(results: list[tuple[float, ...]]) -> None:
    content = []
    content.append(_pdf_text(45, 805, 18, "Chaining vs. Linear Probing"))
    content.append(_pdf_text(45, 787, 9, "Capacity 1,000; identical seeded keys; alpha from 0.1 to 0.9"))
    content.append(_pdf_text(45, 767, 8, "Chaining: hit 1+alpha/2; miss alpha."))
    content.append(_pdf_text(45, 753, 8, "Linear: hit 0.5(1+1/(1-alpha)); miss 0.5(1+1/(1-alpha)^2)."))
    content.append(_pdf_text(45, 737, 8, "Measured values count chain nodes or probed slots; each load uses the same keys for both tables."))

    legend = (
        ("Chaining measured", 45, 0.09, 0.41, 0.67, False),
        ("Chaining theory", 165, 0.09, 0.41, 0.67, True),
        ("Linear measured", 275, 0.85, 0.26, 0.08, False),
        ("Linear theory", 395, 0.85, 0.26, 0.08, True),
    )
    for label, x, red, green, blue, dashed_line in legend:
        content.append(f"{red:g} {green:g} {blue:g} RG 1.2 w\n")
        content.append("[4 3] 0 d\n" if dashed_line else "[] 0 d\n")
        content.append(f"{x:g} 718 m {x + 20:g} 718 l S\n")
        content.append("[] 0 d\n0 G\n")
        content.append(_pdf_text(x + 24, 715, 7, label))

    content.append(_pdf_panel(results, "Successful", (2, 3, 6, 7), 55, 520, 220, 125, 6))
    content.append(_pdf_panel(results, "Unsuccessful", (4, 5, 8, 9), 330, 520, 220, 125, 55))

    content.append(_pdf_text(45, 492, 9, "Observed averages (node comparisons / slot probes)"))
    content.append(_pdf_text(55, 476, 7, "alpha       Chain hit/miss       Linear hit/miss"))
    for row_index, load in enumerate((0.1, 0.5, 0.9)):
        row = next(item for item in results if abs(item[0] - load) < 1e-9)
        line = (
            f"{load:.1f}          {row[2]:.2f} / {row[4]:.2f}"
            f"                 {row[6]:.2f} / {row[8]:.2f}"
        )
        content.append(_pdf_text(55, 461 - row_index * 13, 7, line))

    high_load = next(item for item in results if abs(item[0] - 0.9) < 1e-9)
    notes = (
        "Finding: linear probing keeps data contiguous but develops primary clustering.",
        f"At alpha=0.9, unsuccessful probes average {high_load[8]:.2f} (theory {high_load[9]:.2f}),",
        f"versus {high_load[4]:.2f} chain-node comparisons (theory 0.90).",
        "Chaining cost grows gradually; linear probing is especially costly near capacity.",
        "Small theory gaps come from finite deterministic keys and nonuniform bucket occupancy.",
    )
    for index, line in enumerate(notes):
        content.append(_pdf_text(45, 412 - index * 14, 8, line))

    stream = "".join(content).encode("ascii")
    objects = (
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"endstream",
    )
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, item in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(item)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode(
            "ascii"
        )
    )
    (ROOT / "experiments" / "linear_probing_report.pdf").write_bytes(pdf)


def main() -> None:
    results = measure()
    write_csv(results)
    write_markdown(results)
    write_svg(results)
    write_pdf_report(results)
    print(
        "Wrote linear_probing_results.csv, linear_probing_results.md, "
        "linear_probing_comparison.svg, and linear_probing_report.pdf"
    )


if __name__ == "__main__":
    main()
