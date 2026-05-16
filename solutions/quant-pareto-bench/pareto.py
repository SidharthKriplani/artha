"""
Pareto frontier computation and ASCII visualization for quant-pareto-bench.

Each model variant is a point: (tokens_per_second, accuracy_score).
Pareto-optimal = no other point is better on BOTH axes.
"""

from dataclasses import dataclass


@dataclass
class ModelPoint:
    quant_label: str
    model_path: str
    avg_tokens_per_second: float
    avg_accuracy: float | None      # None if no references provided
    avg_latency_ms: float
    file_size_mb: float | None      # None if not measured


def _is_pareto_optimal(point: ModelPoint, all_points: list[ModelPoint]) -> bool:
    """A point is Pareto-optimal if no other point dominates it on both axes."""
    if point.avg_accuracy is None:
        # Without accuracy, rank by speed only — all are "optimal"
        return True
    for other in all_points:
        if other is point:
            continue
        if other.avg_accuracy is None:
            continue
        # 'other' dominates 'point' if it's better or equal on both axes, strictly better on one
        if (other.avg_tokens_per_second >= point.avg_tokens_per_second and
                other.avg_accuracy >= point.avg_accuracy and
                (other.avg_tokens_per_second > point.avg_tokens_per_second or
                 other.avg_accuracy > point.avg_accuracy)):
            return False
    return True


def compute_pareto(points: list[ModelPoint]) -> list[tuple[ModelPoint, bool]]:
    """Return list of (point, is_pareto_optimal) sorted by tokens/sec descending."""
    sorted_points = sorted(points, key=lambda p: p.avg_tokens_per_second, reverse=True)
    return [(p, _is_pareto_optimal(p, points)) for p in sorted_points]


def print_report(
    points: list[ModelPoint],
    use_color: bool = True,
) -> None:
    BOLD   = "\033[1m"   if use_color else ""
    RESET  = "\033[0m"   if use_color else ""
    GREEN  = "\033[92m"  if use_color else ""
    GREY   = "\033[90m"  if use_color else ""
    YELLOW = "\033[93m"  if use_color else ""

    pareto = compute_pareto(points)
    has_accuracy = any(p.avg_accuracy is not None for p, _ in pareto)

    print()
    print(f"{BOLD}{'='*70}{RESET}")
    print(f"{BOLD}  QUANTIZATION PARETO REPORT{RESET}")
    print(f"  Models benchmarked : {len(points)}")
    print(f"  Accuracy scoring   : {'yes' if has_accuracy else 'no (no reference answers provided)'}")
    print(f"{BOLD}{'='*70}{RESET}")
    print()

    # table header
    if has_accuracy:
        print(f"  {'Quant':<12} {'tok/s':>8} {'Latency':>10} {'Accuracy':>10} {'Size MB':>9}  {'Status'}")
        print(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*10} {'-'*9}  {'-'*14}")
    else:
        print(f"  {'Quant':<12} {'tok/s':>8} {'Latency':>10} {'Size MB':>9}  {'Status'}")
        print(f"  {'-'*12} {'-'*8} {'-'*10} {'-'*9}  {'-'*14}")

    for point, is_optimal in pareto:
        color  = GREEN if is_optimal else GREY
        status = f"{GREEN}★ Pareto-optimal{RESET}" if is_optimal else f"{GREY}dominated{RESET}"
        size   = f"{point.file_size_mb:.0f}" if point.file_size_mb else "n/a"
        acc    = f"{point.avg_accuracy:.2f}" if point.avg_accuracy is not None else "n/a"
        tps    = f"{point.avg_tokens_per_second:.1f}"
        lat    = f"{point.avg_latency_ms:.0f} ms"

        if has_accuracy:
            print(f"  {color}{point.quant_label:<12}{RESET} {tps:>8} {lat:>10} {acc:>10} {size:>9}  {status}")
        else:
            print(f"  {color}{point.quant_label:<12}{RESET} {tps:>8} {lat:>10} {size:>9}  {status}")

    # ASCII scatter (speed vs accuracy)
    if has_accuracy and len(points) >= 2:
        _print_ascii_scatter(pareto, use_color)

    # recommendation
    optimal_points = [p for p, opt in pareto if opt]
    print(f"\n{BOLD}  RECOMMENDATION{RESET}")
    if len(optimal_points) == 1:
        p = optimal_points[0]
        print(f"  {GREEN}{p.quant_label}{RESET} is the only Pareto-optimal point — best balance of speed and accuracy.")
    elif len(optimal_points) > 1:
        fastest = max(optimal_points, key=lambda p: p.avg_tokens_per_second)
        most_accurate = max(optimal_points, key=lambda p: p.avg_accuracy or 0)
        print(f"  For max speed    → {GREEN}{fastest.quant_label}{RESET} ({fastest.avg_tokens_per_second:.1f} tok/s)")
        if most_accurate is not fastest:
            print(f"  For max accuracy → {GREEN}{most_accurate.quant_label}{RESET} (accuracy {most_accurate.avg_accuracy:.2f})")
    print()


def _print_ascii_scatter(
    pareto: list[tuple[ModelPoint, bool]],
    use_color: bool,
) -> None:
    """Simple ASCII scatter: rows = accuracy bands, cols = speed bands."""
    BOLD  = "\033[1m"  if use_color else ""
    RESET = "\033[0m"  if use_color else ""
    GREEN = "\033[92m" if use_color else ""
    GREY  = "\033[90m" if use_color else ""

    points_with_acc = [(p, opt) for p, opt in pareto if p.avg_accuracy is not None]
    if len(points_with_acc) < 2:
        return

    W, H = 40, 10
    min_tps = min(p.avg_tokens_per_second for p, _ in points_with_acc)
    max_tps = max(p.avg_tokens_per_second for p, _ in points_with_acc)
    min_acc = min(p.avg_accuracy for p, _ in points_with_acc)
    max_acc = max(p.avg_accuracy for p, _ in points_with_acc)

    grid = [["·"] * W for _ in range(H)]

    def to_col(tps):
        if max_tps == min_tps: return W // 2
        return int((tps - min_tps) / (max_tps - min_tps) * (W - 1))

    def to_row(acc):
        if max_acc == min_acc: return H // 2
        return H - 1 - int((acc - min_acc) / (max_acc - min_acc) * (H - 1))

    labels = {}
    for p, opt in points_with_acc:
        c, r = to_col(p.avg_tokens_per_second), to_row(p.avg_accuracy)
        grid[r][c] = "★" if opt else "○"
        labels[(r, c)] = p.quant_label

    print(f"\n  {BOLD}Speed (tok/s) →{RESET}")
    print(f"  Accuracy")
    for r, row in enumerate(grid):
        line = "  │ "
        for c, ch in enumerate(row):
            if (r, c) in labels and ch in ("★", "○"):
                color = GREEN if ch == "★" else GREY
                line += f"{color}{ch}{RESET}"
            else:
                line += ch
        # add label at right margin if any marker in this row
        row_labels = [v for (rr, _), v in labels.items() if rr == r and grid[r][_] in ("★", "○")]
        if row_labels:
            line += "  " + " ".join(row_labels)
        print(line)
    print(f"  └{'─'*W}")
    print(f"    {min_tps:.0f} tok/s{' ' * (W - 16)}{max_tps:.0f} tok/s")
