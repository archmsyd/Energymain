from __future__ import annotations

from pathlib import Path
from typing import List


def render_pdf_to_images(pdf_path: Path, pages_dir: Path, dpi: int = 400) -> List[Path]:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError("PyMuPDF is required for PDF rendering.") from exc

    doc = fitz.open(pdf_path)
    output_paths: List[Path] = []
    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)
    for index in range(doc.page_count):
        page = doc.load_page(index)
        pix = page.get_pixmap(matrix=matrix)
        output_path = pages_dir / f"page_{index:03d}.png"
        pix.save(output_path)
        output_paths.append(output_path)
    return output_paths
