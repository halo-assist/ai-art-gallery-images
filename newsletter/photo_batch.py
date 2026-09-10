#!/usr/bin/env python3
"""
photo-batch - prepare marketplace product photos in one command.

For every image in a folder it:
  1. fixes rotation (EXIF auto-orient)
  2. converts to sRGB-safe RGB (flattens transparency onto white)
  3. caps resolution (default: max 2400 px on the short edge; never upscales)
  4. compresses to a file-size target (default 900 KB) with a quality search
  5. strips metadata and renames to a consistent, SEO-friendly pattern

Usage:
  python3 photo_batch.py INPUT_DIR OUTPUT_DIR [--max-short 2400] [--max-kb 900]
                          [--prefix web-] [--quality-max 88]

Outputs:
  OUT_DIR/<prefix>NNN.jpg  +  OUT_DIR/_photo_batch_report.csv

Requires: Pillow (pip install Pillow)
"""
import argparse
import csv
import io
import sys
import time
from pathlib import Path

from PIL import Image, ImageOps

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def flatten(im):
    """Return an RGB image; flattened onto white if it has transparency."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        rgba = im.convert("RGBA")
        bg = Image.new("RGB", rgba.size, (255, 255, 255))
        bg.paste(rgba, mask=rgba.split()[-1])
        return bg
    return im.convert("RGB")


def prep_one(path: Path, out_dir: Path, idx: int, args):
    t0 = time.time()
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)                # 1) rotation from EXIF
    im = flatten(im)                                # 2) RGB / white flatten
    w, h = im.size
    short = min(w, h)
    if short > args.max_short:                      # 3) cap resolution
        scale = args.max_short / short
        im = im.resize((round(w * scale), round(h * scale)),
                       Image.Resampling.LANCZOS)
    elif short < 2000:
        print(f"  ! {path.name}: short edge {short}px < 2000 - kept as-is "
              f"(no upscaling)")
    out = out_dir / f"{args.prefix}{idx:03d}.jpg"
    q = args.quality_max                            # 4) size search
    data = b""
    while True:
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        data = buf.getvalue()
        if len(data) <= args.max_kb * 1024 or q <= 60:
            break
        q -= 6
    out.write_bytes(data)                           # 5) re-encode = no EXIF
    return {
        "file": path.name,
        "out": out.name,
        "in_px": f"{w}x{h}",
        "out_px": f"{im.size[0]}x{im.size[1]}",
        "in_kb": round(path.stat().st_size / 1024),
        "out_kb": round(len(data) / 1024),
        "quality": q,
        "sec": round(time.time() - t0, 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("input_dir")
    ap.add_argument("output_dir")
    ap.add_argument("--max-short", type=int, default=2400,
                    help="max px on the short edge (default 2400)")
    ap.add_argument("--max-kb", type=int, default=900,
                    help="file-size target in KB (default 900)")
    ap.add_argument("--prefix", default="web-",
                    help="output filename prefix (default 'web-')")
    ap.add_argument("--quality-max", type=int, default=88)
    args = ap.parse_args()

    inp, outp = Path(args.input_dir), Path(args.output_dir)
    outp.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in inp.iterdir() if p.suffix.lower() in EXTS)
    if not files:
        print(f"no images found in {inp}")
        return 1

    print(f"photo-batch: {len(files)} files -> {outp}")
    t0 = time.time()
    rows = []
    for i, f in enumerate(files, 1):
        try:
            rows.append(prep_one(f, outp, i, args))
        except Exception as e:  # noqa: BLE001 - keep batch going
            print(f"  x {f.name}: {e}")
    dt = time.time() - t0

    with (outp / "_photo_batch_report.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    kb_in = sum(r["in_kb"] for r in rows)
    kb_out = sum(r["out_kb"] for r in rows)
    ok = sum(1 for r in rows
             if r["out_kb"] <= args.max_kb * 1.02
             and min(int(x) for x in r["out_px"].split("x")) <= args.max_short)
    print(f"done: {len(rows)} files in {dt:.1f}s | "
          f"{kb_in/1024:.1f} MB -> {kb_out/1024:.1f} MB | within targets: {ok}/{len(rows)}")
    for r in rows[:3]:
        print("  ", r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
