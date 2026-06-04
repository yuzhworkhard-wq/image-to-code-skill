#!/usr/bin/env python3
"""Compare two rendered images for high-fidelity image-to-code checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare two PNG/JPG images.")
    parser.add_argument("expected", help="Reference image path")
    parser.add_argument("actual", help="Rendered implementation screenshot path")
    parser.add_argument("--threshold", type=int, default=8, help="Per-channel diff threshold")
    parser.add_argument("--json", action="store_true", help="Print JSON only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        from PIL import Image, ImageChops
        import numpy as np
    except ImportError:
        print("Missing dependencies: install Pillow and numpy.", file=sys.stderr)
        return 2

    expected_path = Path(args.expected)
    actual_path = Path(args.actual)
    if not expected_path.exists():
        print(f"Expected image not found: {expected_path}", file=sys.stderr)
        return 2
    if not actual_path.exists():
        print(f"Actual image not found: {actual_path}", file=sys.stderr)
        return 2

    expected = Image.open(expected_path).convert("RGBA")
    actual = Image.open(actual_path).convert("RGBA")

    same_size = expected.size == actual.size
    width = min(expected.width, actual.width)
    height = min(expected.height, actual.height)
    expected_crop = expected.crop((0, 0, width, height))
    actual_crop = actual.crop((0, 0, width, height))

    diff = ImageChops.difference(expected_crop, actual_crop)
    diff_arr = np.asarray(diff, dtype=np.float32)
    rgb_diff = diff_arr[:, :, :3]
    alpha_diff = diff_arr[:, :, 3]

    per_pixel_max = rgb_diff.max(axis=2)
    changed = per_pixel_max > args.threshold
    changed_ratio = float(changed.mean()) if changed.size else 0.0
    mae = float(rgb_diff.mean()) if rgb_diff.size else 0.0
    rmse = float(np.sqrt(np.mean(rgb_diff * rgb_diff))) if rgb_diff.size else 0.0
    max_diff = int(rgb_diff.max()) if rgb_diff.size else 0
    alpha_mae = float(alpha_diff.mean()) if alpha_diff.size else 0.0

    result = {
        "expected_size": list(expected.size),
        "actual_size": list(actual.size),
        "same_size": same_size,
        "compared_size": [width, height],
        "threshold": args.threshold,
        "changed_pixel_ratio": round(changed_ratio, 6),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "max_rgb_diff": max_diff,
        "alpha_mae": round(alpha_mae, 4),
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"expected_size: {expected.size}")
        print(f"actual_size:   {actual.size}")
        print(f"same_size:     {same_size}")
        print(f"compared_size: {width}x{height}")
        print(f"threshold:     {args.threshold}")
        print(f"changed_ratio: {changed_ratio:.6f}")
        print(f"mae:           {mae:.4f}")
        print(f"rmse:          {rmse:.4f}")
        print(f"max_rgb_diff:  {max_diff}")
        print(f"alpha_mae:     {alpha_mae:.4f}")

    return 0 if same_size else 1


if __name__ == "__main__":
    raise SystemExit(main())
