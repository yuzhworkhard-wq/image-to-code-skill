#!/usr/bin/env python3
"""Audit PNG cut assets for edge clipping, dimensions, and transparency."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit transparent PNG cut assets.")
    parser.add_argument("paths", nargs="+", help="PNG files or directories to audit")
    parser.add_argument(
        "--manifest",
        help=(
            "Optional JSON manifest. Supported formats: "
            "[{\"path\":\"assets/icons/a.png\",\"width\":40,\"height\":40}], "
            "[{\"asset\":\"assets/icons/a.png\",\"asset_pixel_width\":80,"
            "\"asset_pixel_height\":80}], or "
            "{\"assets/icons/a.png\":{\"width\":40,\"height\":40}}."
        ),
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=0,
        help="Alpha value greater than this threshold counts as visible.",
    )
    parser.add_argument(
        "--require-transparent-bg",
        action="store_true",
        help="Fail when corner/background pixels are opaque instead of transparent.",
    )
    parser.add_argument(
        "--bg-alpha-threshold",
        type=int,
        default=12,
        help="Corner/background alpha greater than this fails transparent-bg checks.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON report.")
    return parser.parse_args()


def collect_pngs(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for item in paths:
        path = Path(item)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.png")))
        elif path.suffix.lower() == ".png":
            files.append(path)
    return files


def load_manifest(path: str | None) -> dict[str, tuple[int, int]]:
    if not path:
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    result: dict[str, tuple[int, int]] = {}
    if isinstance(data, list):
        for item in data:
            item_path = item.get("path") or item.get("asset")
            if not item_path:
                continue
            width = item.get("asset_pixel_width", item.get("width"))
            height = item.get("asset_pixel_height", item.get("height"))
            if width is None or height is None:
                continue
            result[str(item_path)] = (int(width), int(height))
    elif isinstance(data, dict):
        for key, value in data.items():
            width = value.get("asset_pixel_width", value.get("width"))
            height = value.get("asset_pixel_height", value.get("height"))
            if width is None or height is None:
                continue
            result[str(key)] = (int(width), int(height))
    return result


def manifest_size(manifest: dict[str, tuple[int, int]], path: Path) -> tuple[int, int] | None:
    candidates = [str(path), path.as_posix(), path.name]
    for candidate in candidates:
        if candidate in manifest:
            return manifest[candidate]
    return None


def corner_alpha_stats(alpha) -> dict[str, float]:
    h, w = alpha.shape
    patch = max(1, min(4, h, w))
    samples = [
        alpha[:patch, :patch],
        alpha[:patch, w - patch :],
        alpha[h - patch :, :patch],
        alpha[h - patch :, w - patch :],
    ]
    values = [float(sample.mean()) for sample in samples]
    return {
        "corner_alpha_max": round(max(values), 4),
        "corner_alpha_mean": round(sum(values) / len(values), 4),
    }


def main() -> int:
    args = parse_args()

    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        print("Missing dependencies: install Pillow and numpy.", file=sys.stderr)
        return 2

    manifest = load_manifest(args.manifest)
    pngs = collect_pngs(args.paths)
    if not pngs:
        print("No PNG files found.", file=sys.stderr)
        return 2

    report = []
    failed = False

    for path in pngs:
        original = Image.open(path)
        has_alpha_channel = original.mode in ("RGBA", "LA") or (
            original.mode == "P" and "transparency" in original.info
        )
        image = original.convert("RGBA")
        alpha = np.asarray(image)[:, :, 3]
        visible = alpha > args.alpha_threshold
        top = bool(visible[0, :].any())
        bottom = bool(visible[-1, :].any())
        left = bool(visible[:, 0].any())
        right = bool(visible[:, -1].any())
        edge_touch = {"top": top, "bottom": bottom, "left": left, "right": right}
        touches_edge = any(edge_touch.values())

        expected = manifest_size(manifest, path)
        size_ok = True
        if expected is not None:
            size_ok = image.size == expected

        alpha_stats = corner_alpha_stats(alpha)
        transparent_bg_ok = True
        if args.require_transparent_bg:
            transparent_bg_ok = (
                has_alpha_channel
                and alpha_stats["corner_alpha_max"] <= args.bg_alpha_threshold
            )

        item = {
            "path": str(path),
            "width": image.width,
            "height": image.height,
            "has_alpha_channel": has_alpha_channel,
            "transparent_bg_ok": transparent_bg_ok,
            **alpha_stats,
            "expected_width": expected[0] if expected else None,
            "expected_height": expected[1] if expected else None,
            "size_ok": size_ok,
            "touches_edge": touches_edge,
            "edge_touch": edge_touch,
        }
        report.append(item)

        if touches_edge or not size_ok or not transparent_bg_ok:
            failed = True

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for item in report:
            status = (
                "FAIL"
                if item["touches_edge"] or not item["size_ok"] or not item["transparent_bg_ok"]
                else "OK"
            )
            expected = ""
            if item["expected_width"] is not None:
                expected = f" expected={item['expected_width']}x{item['expected_height']}"
            edges = ",".join(k for k, v in item["edge_touch"].items() if v) or "none"
            print(
                f"{status} {item['path']} size={item['width']}x{item['height']}"
                f"{expected} edge_touch={edges}"
                f" alpha={item['has_alpha_channel']}"
                f" corner_alpha_max={item['corner_alpha_max']}"
                f" transparent_bg_ok={item['transparent_bg_ok']}"
            )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
