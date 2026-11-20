"""Measure separate-chaining lookup comparisons across load factors."""

import csv
from pathlib import Path
import random
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.hash_table import HashTable


CAPACITY = 4093
LOAD_FACTORS = tuple(step / 4 for step in range(1, 17))
KEY_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
QUERY_COUNT = CAPACITY * 4


def random_keys(
    count: int,
    seed: int,
    excluded: tuple[str, ...] | list[str] = (),
) -> list[str]:
    generator = random.Random(seed)
    keys = []
    while len(keys) < count:
        key = "".join(generator.choice(KEY_ALPHABET) for _ in range(16))
        if key not in keys and key not in excluded:
            keys.append(key)
    return keys


def random_urls(count: int, seed: int, category: str) -> list[str]:
    generator = random.Random(seed)
    urls = []
    for index in range(count):
        path = "".join(generator.choice(KEY_ALPHABET) for _ in range(16))
        urls.append(f"https://example.com/{category}/{path}/{index}")
    return urls


def measure() -> list[tuple[float, float, int, float, float, float, float]]:
    results = []
    all_urls = random_urls(CAPACITY * 4, 2026, "entry")
    unsuccessful_queries = random_urls(QUERY_COUNT, 2027, "missing")
    for target_load_factor in LOAD_FACTORS:
        entry_count = round(target_load_factor * CAPACITY)
        load_factor = entry_count / CAPACITY
        table = HashTable(initial_capacity=CAPACITY, max_load_factor=None)
        urls = all_urls[:entry_count]
        for index, url in enumerate(urls):
            table.put(url, index)

        successful_comparisons = 0
        for url in urls:
            table.get(url)
            successful_comparisons += table.last_comparisons

        unsuccessful_comparisons = 0
        for url in unsuccessful_queries:
            table.get(url)
            unsuccessful_comparisons += table.last_comparisons

        observed_success = successful_comparisons / len(urls)
        observed_failure = unsuccessful_comparisons / len(unsuccessful_queries)
        results.append(
            (
                target_load_factor,
                load_factor,
                entry_count,
                observed_success,
                1 + load_factor / 2,
                observed_failure,
                load_factor,
            )
        )
    return results


def write_csv(
    results: list[tuple[float, float, int, float, float, float, float]],
) -> None:
    path = ROOT / "experiments" / "results.csv"
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(
            (
                "target_load_factor",
                "actual_load_factor",
                "entries",
                "observed_success",
                "theory_success",
                "observed_failure",
                "theory_failure",
            )
        )
        for row in results:
            writer.writerow(
                (f"{row[0]:.2f}", f"{row[1]:.4f}", row[2], *(f"{value:.4f}" for value in row[3:]))
            )


def write_markdown(
    results: list[tuple[float, float, int, float, float, float, float]],
) -> None:
    lines = [
        "# Separate-chaining lookup comparisons",
        "",
        f"Capacity: {CAPACITY}; deterministic random URLs; "
        f"{QUERY_COUNT} unsuccessful queries per load factor.",
        "",
        "Target load factors run from 0.25 to 4.00 in 0.25 steps. Entry counts "
        "are rounded to integers, and theory uses the resulting actual load factor.",
        "",
        "| Target α | Actual α | Entries | Successful: measured | Successful: theory | Failed: measured | Failed: theory |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for target, load, entries, success, success_theory, failure, failure_theory in results:
        lines.append(
            f"| {target:.2f} | {load:.4f} | {entries} | {success:.3f} "
            f"| {success_theory:.3f} | {failure:.3f} | {failure_theory:.3f} |"
        )
    lines.extend(
        (
            "",
            "The theoretical estimates are `1 + α/2` for successful search and `α` "
            "for unsuccessful search.",
            "",
        )
    )
    (ROOT / "experiments" / "results.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def write_svg(
    results: list[tuple[float, float, int, float, float, float, float]],
) -> None:
    width, height = 900, 600
    left, right, top, bottom = 80, 850, 90, 500
    x = lambda load: left + load / 4 * (right - left)
    y = lambda comparisons: bottom - comparisons / 5 * (bottom - top)
    series = (
        ("Successful measured", 3, "#1769aa", "circle"),
        ("Successful theory (1 + α/2)", 4, "#1769aa", "dash"),
        ("Unsuccessful measured", 5, "#d84315", "circle"),
        ("Unsuccessful theory (α)", 6, "#d84315", "dash"),
    )
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="450" y="35" text-anchor="middle" font-family="sans-serif" font-size="20">Chaining lookup comparisons vs load factor</text>',
    ]
    for tick in range(6):
        py = y(tick)
        svg.append(f'<line x1="{left}" y1="{py:.1f}" x2="{right}" y2="{py:.1f}" stroke="#dddddd"/>')
        svg.append(f'<text x="{left - 15}" y="{py + 5:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{tick}</text>')
    for tick in range(0, 5):
        px = x(tick)
        svg.append(f'<line x1="{px:.1f}" y1="{top}" x2="{px:.1f}" y2="{bottom}" stroke="#eeeeee"/>')
        svg.append(f'<text x="{px:.1f}" y="{bottom + 22}" text-anchor="middle" font-family="sans-serif" font-size="12">{tick}</text>')
    svg.extend(
        (
            f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#333"/>',
            f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#333"/>',
            f'<text x="465" y="555" text-anchor="middle" font-family="sans-serif" font-size="14">Load factor α</text>',
            f'<text x="22" y="300" transform="rotate(-90 22 300)" text-anchor="middle" font-family="sans-serif" font-size="14">Key comparisons</text>',
        )
    )
    for label, column, color, style in series:
        points = " ".join(f"{x(row[1]):.1f},{y(row[column]):.1f}" for row in results)
        dash = ' stroke-dasharray="7 5"' if style == "dash" else ""
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"{dash}/>')
        if style == "circle":
            for row in results:
                svg.append(f'<circle cx="{x(row[1]):.1f}" cy="{y(row[column]):.1f}" r="2.5" fill="{color}"/>')
    for index, (label, _, color, style) in enumerate(series):
        legend_y = 75 + index * 22
        dash = ' stroke-dasharray="7 5"' if style == "dash" else ""
        svg.append(f'<line x1="595" y1="{legend_y}" x2="625" y2="{legend_y}" stroke="{color}" stroke-width="2"{dash}/>')
        svg.append(f'<text x="632" y="{legend_y + 4}" font-family="sans-serif" font-size="12">{label}</text>')
    svg.append("</svg>")
    (ROOT / "experiments" / "results.svg").write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    results = measure()
    write_csv(results)
    write_markdown(results)
    write_svg(results)
    print("Wrote experiments/results.csv, results.md, and results.svg")


if __name__ == "__main__":
    main()
