"""Render PDF page screenshots and crop figures/tables from a JSON spec.

Examples:
  python scripts/pdf_screenshot.py captions paper/AI4S/Protein/OntoProtein/paper.pdf
  python scripts/pdf_screenshot.py preview paper/AI4S/Protein/OntoProtein/paper.pdf --pages 2,3,5-8 --grid
  python scripts/pdf_screenshot.py crop paper/AI4S/Protein/OntoProtein/figure-crops.json
  python scripts/pdf_screenshot.py crop paper/AI4S/Protein/OntoProtein/figure-crops.json --out tmp-crops --dpi 150

The crop spec is intentionally plain JSON so every figure crop can be reviewed
and adjusted without editing this script.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit("Missing dependency: install PyMuPDF, for example `pip install pymupdf`.") from exc

try:
    from PIL import Image, ImageDraw
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit("Missing dependency: install Pillow, for example `pip install pillow`.") from exc


CAPTION_RE = re.compile(r"^(Figure|Fig\.|Table|TABLE)\s+(\d+)[:.]")


def parse_page_list(value: str, page_count: int) -> list[int]:
    pages: set[int] = set()
    for part in value.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", 1)
            start, end = int(left), int(right)
            if start > end:
                raise ValueError(f"Invalid page range: {token}")
            pages.update(range(start, end + 1))
        else:
            pages.add(int(token))

    bad = [page for page in pages if page < 1 or page > page_count]
    if bad:
        raise ValueError(f"Pages out of range for {page_count}-page PDF: {bad}")
    return sorted(pages)


def resolve_from(base: Path, value: str | None, default: str) -> Path:
    raw = value or default
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path


def pixmap_to_image(pix: fitz.Pixmap) -> Image.Image:
    mode = "RGBA" if pix.alpha else "RGB"
    return Image.frombytes(mode, (pix.width, pix.height), pix.samples)


def trim_white_border(image: Image.Image, threshold: int = 248, padding: int = 8) -> Image.Image:
    rgb = image.convert("RGB")
    gray = rgb.convert("L")
    mask = gray.point(lambda p: 255 if p < threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return image

    left, top, right, bottom = bbox
    left = max(left - padding, 0)
    top = max(top - padding, 0)
    right = min(right + padding, image.width)
    bottom = min(bottom + padding, image.height)
    return image.crop((left, top, right, bottom))


def draw_normalized_grid(image: Image.Image) -> Image.Image:
    draw = ImageDraw.Draw(image)
    width, height = image.size

    for i in range(21):
        ratio = i / 20
        x = round(width * ratio)
        y = round(height * ratio)
        major = i % 2 == 0
        color = (70, 120, 200) if major else (170, 195, 230)
        draw.line((x, 0, x, height), fill=color, width=2 if major else 1)
        draw.line((0, y, width, y), fill=color, width=2 if major else 1)

    for i in range(11):
        ratio = i / 10
        x = round(width * ratio)
        y = round(height * ratio)
        label = f"{ratio:.1f}"
        draw.text((x + 4, 4), label, fill=(0, 70, 150))
        draw.text((4, y + 4), label, fill=(0, 70, 150))

    return image


def rect_from_item(item: dict, page: fitz.Page, default_units: str) -> fitz.Rect:
    if "rect" not in item:
        raise ValueError(f"Crop item {item.get('name', '<unnamed>')} is missing `rect`.")

    rect_values = item["rect"]
    if not isinstance(rect_values, list) or len(rect_values) != 4:
        raise ValueError(f"Crop item {item.get('name', '<unnamed>')} has an invalid `rect`.")

    units = item.get("units", default_units)
    x0, y0, x1, y1 = [float(value) for value in rect_values]

    if units == "normalized":
        page_rect = page.rect
        rect = fitz.Rect(
            page_rect.x0 + x0 * page_rect.width,
            page_rect.y0 + y0 * page_rect.height,
            page_rect.x0 + x1 * page_rect.width,
            page_rect.y0 + y1 * page_rect.height,
        )
    elif units == "points":
        rect = fitz.Rect(x0, y0, x1, y1)
    else:
        raise ValueError(f"Unsupported rect units: {units}")

    padding_pt = float(item.get("padding_pt", 0))
    if padding_pt:
        rect = fitz.Rect(
            rect.x0 - padding_pt,
            rect.y0 - padding_pt,
            rect.x1 + padding_pt,
            rect.y1 + padding_pt,
        )

    return rect & page.rect


def iter_caption_lines(text: str) -> Iterable[str]:
    for line in text.splitlines():
        stripped = line.strip()
        if CAPTION_RE.match(stripped):
            yield stripped


def iter_caption_bboxes(page: fitz.Page) -> Iterable[tuple[str, fitz.Rect]]:
    text_dict = page.get_text("dict")
    for block in text_dict.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            text = "".join(span.get("text", "") for span in line.get("spans", [])).strip()
            if CAPTION_RE.match(text):
                yield text, fitz.Rect(line["bbox"])


def guess_crop_rect(page: fitz.Page, caption_rect: fitz.Rect, kind: str) -> fitz.Rect:
    page_rect = page.rect
    width = page_rect.width
    height = page_rect.height

    if caption_rect.x1 < page_rect.x0 + width * 0.55:
        x0 = page_rect.x0 + width * 0.07
        x1 = page_rect.x0 + width * 0.49
    elif caption_rect.x0 > page_rect.x0 + width * 0.45:
        x0 = page_rect.x0 + width * 0.51
        x1 = page_rect.x0 + width * 0.93
    else:
        x0 = page_rect.x0 + width * 0.07
        x1 = page_rect.x0 + width * 0.93

    crop_height = height * (0.40 if kind == "fig" else 0.20)
    y1 = max(page_rect.y0 + height * 0.08, caption_rect.y0 - 4)
    y0 = max(page_rect.y0 + height * 0.04, y1 - crop_height)

    return fitz.Rect(x0, y0, x1, y1) & page_rect


def format_rect(rect: fitz.Rect, page: fitz.Page, units: str) -> list[float]:
    if units == "normalized":
        page_rect = page.rect
        values = [
            (rect.x0 - page_rect.x0) / page_rect.width,
            (rect.y0 - page_rect.y0) / page_rect.height,
            (rect.x1 - page_rect.x0) / page_rect.width,
            (rect.y1 - page_rect.y0) / page_rect.height,
        ]
        return [round(value, 4) for value in values]
    if units == "points":
        return [round(value, 2) for value in (rect.x0, rect.y0, rect.x1, rect.y1)]
    raise ValueError(f"Unsupported rect units: {units}")


def unique_name(name: str, seen: set[str], page_no: int) -> str:
    if name not in seen:
        seen.add(name)
        return name

    stem, suffix = name.rsplit(".", 1)
    candidate = f"{stem}_p{page_no}.{suffix}"
    index = 2
    while candidate in seen:
        candidate = f"{stem}_p{page_no}_{index}.{suffix}"
        index += 1
    seen.add(candidate)
    return candidate


def command_captions(args: argparse.Namespace) -> int:
    doc = fitz.open(args.pdf)
    for index, page in enumerate(doc, start=1):
        lines = list(iter_caption_lines(page.get_text("text")))
        if not lines:
            continue
        print(f"page {index}")
        for line in lines:
            print(f"  {line}")
    return 0


def command_init(args: argparse.Namespace) -> int:
    pdf_path = Path(args.pdf).resolve()
    doc = fitz.open(pdf_path)
    pages = parse_page_list(args.pages, doc.page_count) if args.pages else list(range(1, doc.page_count + 1))

    if args.units not in {"normalized", "points"}:
        raise ValueError("`--units` must be either `normalized` or `points`.")

    seen: set[str] = set()
    items: list[dict] = []
    for page_no in pages:
        page = doc[page_no - 1]
        for caption, caption_rect in iter_caption_bboxes(page):
            match = CAPTION_RE.match(caption)
            if not match:
                continue

            label, number = match.groups()
            kind = "fig" if label.lower().startswith(("fig", "figure")) else "table"
            name = unique_name(f"{kind}{number}.png", seen, page_no)
            rect = guess_crop_rect(page, caption_rect, kind)
            items.append(
                {
                    "name": name,
                    "page": page_no,
                    "rect": format_rect(rect, page, args.units),
                    "caption": caption,
                }
            )

    out_path = Path(args.out).resolve() if args.out else pdf_path.parent / "figure-crops.json"
    if out_path.exists() and not args.force:
        raise ValueError(f"{out_path} already exists. Use --force to overwrite it.")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        pdf_value = Path(os.path.relpath(pdf_path, out_path.parent)).as_posix()
    except ValueError:
        pdf_value = pdf_path.as_posix()
    spec = {
        "pdf": pdf_value,
        "output_dir": "figures",
        "dpi": args.dpi,
        "units": args.units,
        "trim": True,
        "trim_threshold": 248,
        "trim_padding_px": 8,
        "items": items,
    }
    out_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{out_path} ({len(items)} items)")
    return 0


def command_preview(args: argparse.Namespace) -> int:
    pdf_path = Path(args.pdf)
    doc = fitz.open(pdf_path)
    pages = parse_page_list(args.pages, doc.page_count)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    zoom = args.dpi / 72
    for page_no in pages:
        page = doc[page_no - 1]
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        image = pixmap_to_image(pix)
        if args.grid:
            image = draw_normalized_grid(image)
        out = out_dir / f"{pdf_path.stem}_p{page_no}.png"
        image.save(out)
        print(f"{out} {image.width}x{image.height}")
    return 0


def command_crop(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec).resolve()
    spec_base = spec_path.parent
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    pdf_path = resolve_from(spec_base, spec.get("pdf"), "paper.pdf")
    output_dir = resolve_from(spec_base, args.out or spec.get("output_dir"), "figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    dpi = int(args.dpi or spec.get("dpi", 300))
    zoom = dpi / 72
    default_units = spec.get("units", "normalized")
    trim = args.trim or bool(spec.get("trim", False))
    trim_threshold = int(spec.get("trim_threshold", 248))
    trim_padding = int(spec.get("trim_padding_px", 8))

    doc = fitz.open(pdf_path)
    for item in spec.get("items", []):
        page_no = int(item["page"])
        if page_no < 1 or page_no > doc.page_count:
            raise ValueError(f"Page {page_no} is out of range for {pdf_path}.")

        page = doc[page_no - 1]
        rect = rect_from_item(item, page, default_units)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect, alpha=False)
        image = pixmap_to_image(pix)
        if trim:
            image = trim_white_border(image, threshold=trim_threshold, padding=trim_padding)

        out = output_dir / item["name"]
        image.save(out)
        print(f"{out} {image.width}x{image.height}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render PDF page screenshots and crop figures/tables from a JSON spec.",
        epilog=(
            "Examples:\n"
            "  python scripts/pdf_screenshot.py captions paper/AI4S/Protein/OntoProtein/paper.pdf\n"
            "  python scripts/pdf_screenshot.py init paper/AI4S/Protein/OntoProtein/paper.pdf --pages 2,3,5-8\n"
            "  python scripts/pdf_screenshot.py preview paper/AI4S/Protein/OntoProtein/paper.pdf --pages 2,3,5-8 --grid\n"
            "  python scripts/pdf_screenshot.py crop paper/AI4S/Protein/OntoProtein/figure-crops.json\n"
            "  python scripts/pdf_screenshot.py crop paper/AI4S/Protein/OntoProtein/figure-crops.json --out tmp-crops --dpi 150\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    captions = subparsers.add_parser("captions", help="List figure/table captions with page numbers.")
    captions.add_argument("pdf", help="PDF path.")
    captions.set_defaults(func=command_captions)

    init = subparsers.add_parser("init", help="Create a starter crop JSON from PDF captions.")
    init.add_argument("pdf", help="PDF path.")
    init.add_argument("--pages", help="Pages or ranges, for example 2,3,5-8. Defaults to all pages.")
    init.add_argument("--out", help="Output JSON path. Defaults to figure-crops.json next to the PDF.")
    init.add_argument("--dpi", type=int, default=300, help="Render DPI to store in the generated spec.")
    init.add_argument("--units", choices=["normalized", "points"], default="normalized", help="Coordinate units for generated rects.")
    init.add_argument("--force", action="store_true", help="Overwrite an existing JSON file.")
    init.set_defaults(func=command_init)

    preview = subparsers.add_parser("preview", help="Render full-page preview images.")
    preview.add_argument("pdf", help="PDF path.")
    preview.add_argument("--pages", required=True, help="Pages or ranges, for example 2,3,5-8.")
    preview.add_argument("--out", default="pdf-previews", help="Output directory.")
    preview.add_argument("--dpi", type=int, default=144, help="Preview render DPI.")
    preview.add_argument("--grid", action="store_true", help="Overlay a normalized coordinate grid.")
    preview.set_defaults(func=command_preview)

    crop = subparsers.add_parser("crop", help="Crop figures/tables from a JSON spec.")
    crop.add_argument("spec", help="Crop spec JSON path.")
    crop.add_argument("--out", help="Override output directory from spec.")
    crop.add_argument("--dpi", type=int, help="Override render DPI from spec.")
    crop.add_argument("--trim", action="store_true", help="Trim white borders after cropping.")
    crop.set_defaults(func=command_crop)

    return parser


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
