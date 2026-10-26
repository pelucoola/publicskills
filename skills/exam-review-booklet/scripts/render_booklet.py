#!/usr/bin/env python3
"""Render confirmed exam-review JSON into a printable PDF and self-contained HTML.

All text fields are plain text, not HTML. Image crop coordinates are normalized
to the EXIF-oriented image. The script lays out verified content; it does not
recognize handwriting, solve questions, or infer exam metadata.
"""
from __future__ import annotations

import argparse
import base64
from collections import deque
from copy import copy
from dataclasses import dataclass, field
from html import escape
from io import BytesIO
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from typing import Any

try:
    from PIL import Image, ImageOps
    from reportlab.lib.colors import HexColor
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
except ImportError as exc:
    raise SystemExit("缺少依赖：请在可用的 Python 运行时安装 reportlab 和 Pillow。" + str(exc))

PAGE_W, PAGE_H = landscape(A4)
MARGIN = 32.0
GAP = 24.0
COL_W = (PAGE_W - 2 * MARGIN - GAP) / 2
BODY_SIZE = 11.5
BODY_LEADING = 16.4
HEADING_SIZE = 12.0
HEADING_LEADING = 17.0
CAPTION_SIZE = 9.5
CAPTION_LEADING = 13.0
INK = "#202020"
NAVY = "#183047"
GRAY = "#606870"
FONT_REG = "BookletRegular"
FONT_BOLD = "BookletBold"


class ContentError(ValueError):
    pass


def require_text(value: Any, name: str, *, empty: bool = False, limit: int = 20000) -> str:
    if not isinstance(value, str):
        raise ContentError(f"{name} 必须是纯文本字符串。")
    value = value.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not value and not empty:
        raise ContentError(f"{name} 不能为空。")
    if len(value) > limit:
        raise ContentError(f"{name} 过长（最多 {limit} 个字符），请拆分内容。")
    if any(ord(c) < 32 and c not in "\n\t" for c in value):
        raise ContentError(f"{name} 包含不支持的控制字符。")
    return value


def validate(data: Any, base: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ContentError("输入 JSON 顶层必须是对象。")
    exam = data.get("exam")
    if not isinstance(exam, dict):
        raise ContentError("缺少 exam 对象。")
    confirmation = exam.get("confirmation")
    if not isinstance(confirmation, dict) or confirmation.get("title") is not True or confirmation.get("exam_date") is not True:
        raise ContentError("标题和试卷日期尚未确认。请先完成用户确认，再将 confirmation.title 与 confirmation.exam_date 都设为 true。")
    exam["title"] = require_text(exam.get("title"), "exam.title", limit=400)
    exam["exam_date"] = require_text(exam.get("exam_date"), "exam.exam_date", limit=80)
    exam["generated_at"] = require_text(exam.get("generated_at"), "exam.generated_at", limit=120)
    exam["date_label"] = require_text(exam.get("date_label", "试卷日期"), "exam.date_label", limit=16)
    pages = data.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ContentError("pages 必须是非空数组。")
    for page_i, page in enumerate(pages, 1):
        loc = f"pages[{page_i - 1}]"
        if not isinstance(page, dict):
            raise ContentError(f"{loc} 必须是对象。")
        page["topic"] = require_text(page.get("topic"), f"{loc}.topic", limit=400)
        if page.get("kind", "explanation") not in ("explanation", "answer"):
            raise ContentError(f"{loc}.kind 只能是 explanation 或 answer。")
        page.setdefault("kind", "explanation")
        page["intro"] = require_text(page.get("intro", ""), f"{loc}.intro", empty=True)
        page["key_tip"] = require_text(page.get("key_tip", ""), f"{loc}.key_tip", empty=True)
        nonempty = bool(page["intro"] or page["key_tip"])
        for side in ("left", "right"):
            blocks = page.get(side, [])
            if not isinstance(blocks, list):
                raise ContentError(f"{loc}.{side} 必须是数组。")
            page[side] = blocks
            for block_i, block in enumerate(blocks):
                b_loc = f"{loc}.{side}[{block_i}]"
                if not isinstance(block, dict):
                    raise ContentError(f"{b_loc} 必须是对象。")
                block.setdefault("type", "text")
                block["heading"] = require_text(block.get("heading", ""), f"{b_loc}.heading", empty=True, limit=200)
                if block["type"] == "text":
                    block["text"] = require_text(block.get("text", ""), f"{b_loc}.text", empty=True)
                    if not (block["text"] or block["heading"]):
                        raise ContentError(f"{b_loc} 的标题与正文不能同时为空。")
                elif block["type"] == "image":
                    raw_path = require_text(block.get("path"), f"{b_loc}.path")
                    path = Path(raw_path).expanduser()
                    path = path if path.is_absolute() else base / path
                    path = path.resolve()
                    if not path.is_file():
                        raise ContentError(f"{b_loc} 图片不存在：{path}")
                    block["_path"] = str(path)
                    block["caption"] = require_text(block.get("caption", ""), f"{b_loc}.caption", empty=True, limit=500)
                    crop = block.get("crop", [0, 0, 1, 1])
                    if not isinstance(crop, list) or len(crop) != 4 or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in crop):
                        raise ContentError(f"{b_loc}.crop 必须是四个有限数值 [左,上,右,下]。")
                    if not (0 <= crop[0] < crop[2] <= 1 and 0 <= crop[1] < crop[3] <= 1):
                        raise ContentError(f"{b_loc}.crop 必须满足 0≤左<右≤1 且 0≤上<下≤1。")
                    block["crop"] = crop
                    mh = block.get("max_height_pt")
                    if mh is not None and (isinstance(mh, bool) or not isinstance(mh, (int, float)) or not math.isfinite(mh) or mh < 24):
                        raise ContentError(f"{b_loc}.max_height_pt 必须为不小于24的有限数值。")
                else:
                    raise ContentError(f"{b_loc}.type 不支持：{block['type']}")
                nonempty = True
        if not nonempty:
            raise ContentError(f"{loc} 没有可打印内容。")
    return data


def gather_text(value: Any) -> str:
    if isinstance(value, dict):
        return "\n".join(gather_text(v) for k, v in value.items() if not k.startswith("_") and k not in ("path", "crop"))
    if isinstance(value, list):
        return "\n".join(gather_text(v) for v in value)
    return value if isinstance(value, str) else ""


STATIC_TEXT = "试卷日期作业日期日期生成时间第页题目要点原题与作答辅助图与前半段答案错因与逐步思路标准答案整理版关键指导续本题原作答辅助图讲解答案见首页。0123456789 /:()-[]A4横向打印讲评册打印只读取本地材料"


def is_cjk(c: str) -> bool:
    return "\u3400" <= c <= "\u9fff" or "\uf900" <= c <= "\ufaff"


def find_font(explicit: str | None, all_text: str, diagnostics: list[dict]) -> Path:
    choices = []
    if explicit:
        choices.append(Path(explicit).expanduser())
    elif os.environ.get("EXAM_BOOKLET_FONT"):
        choices.append(Path(os.environ["EXAM_BOOKLET_FONT"]).expanduser())
    else:
        choices.extend(Path(p) for p in (
            "/Library/Fonts/Arial Unicode.ttf",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ))
    failures = []
    cjk_chars = {c for c in all_text if is_cjk(c)}
    for path in choices:
        if not path.is_file():
            continue
        try:
            font = TTFont(FONT_REG, str(path), subfontIndex=0)
            missing_cjk = [c for c in cjk_chars if ord(c) not in font.face.charWidths]
            if missing_cjk:
                failures.append(f"{path.name} 缺少中文字符 {''.join(missing_cjk[:8])}")
                continue
            pdfmetrics.registerFont(font)
            missing = sorted({c for c in all_text if not c.isspace() and ord(c) not in font.face.charWidths})
            if missing:
                diagnostics.append({"code": "font_missing_symbols", "severity": "warning", "characters": "".join(missing), "message": "字体缺少这些符号；请检查渲染图或改用覆盖更全的 --font。"})
            return path.resolve()
        except Exception as exc:
            failures.append(f"{path.name}: {exc}")
    raise ContentError("未找到可嵌入的中文 TrueType 字体。请用 --font 指定支持中文的 .ttf/.ttc 字体。" + (" 检查结果：" + "；".join(failures) if failures else ""))


def register_bold(path: str | None, regular: Path, diagnostics: list[dict], all_text: str) -> Path:
    candidate = Path(path).expanduser() if path else regular
    if not candidate.is_file():
        raise ContentError(f"粗体字体不存在：{candidate}")
    try:
        font = TTFont(FONT_BOLD, str(candidate), subfontIndex=0)
        missing = sorted({c for c in all_text if is_cjk(c) and ord(c) not in font.face.charWidths})
        if missing:
            raise ContentError("粗体字体缺少中文字符：" + "".join(missing[:12]))
        pdfmetrics.registerFont(font)
    except Exception as exc:
        raise ContentError(f"无法加载粗体字体：{exc}") from exc
    return candidate.resolve()


def wrap_text(text: str, width: float, size: float = BODY_SIZE, font: str = FONT_REG) -> list[str]:
    """Explicit line boxes make HTML and PDF use the same measured pagination."""
    output = []
    for raw in text.expandtabs(4).split("\n"):
        if not raw:
            output.append("")
            continue
        remaining = raw
        while remaining:
            running = 0.0
            end = 0
            last_space = -1
            for i, char in enumerate(remaining):
                new_w = pdfmetrics.stringWidth(char, font, size)
                if running + new_w > width and i > 0:
                    break
                running += new_w
                end = i + 1
                if char.isspace():
                    last_space = i
            if end == len(remaining):
                output.append(remaining.rstrip())
                break
            if last_space >= max(1, end // 2):
                output.append(remaining[:last_space].rstrip())
                remaining = remaining[last_space + 1:].lstrip()
            else:
                # Avoid leaving common closing punctuation at the start of a line.
                if end < len(remaining) and remaining[end] in "，。；：、！？）》」』】％%" and end > 1:
                    end -= 1
                output.append(remaining[:end])
                remaining = remaining[end:]
    return output


@dataclass
class Unit:
    kind: str
    uid: str
    heading: str = ""
    lines: list[str] = field(default_factory=list)
    continued: bool = False
    image: Image.Image | None = None
    source: str = ""
    crop: list[float] | None = None
    max_height: float | None = None
    caption: list[str] = field(default_factory=list)


def text_units(block: dict, uid: str) -> list[Unit]:
    paragraphs = re.split(r"\n\s*\n", block.get("text", ""))
    paragraphs = paragraphs or [""]
    result = []
    for i, paragraph in enumerate(paragraphs):
        if not paragraph and i > 0:
            continue
        result.append(Unit("text", f"{uid}.p{i}", block.get("heading", "") if i == 0 else "", wrap_text(paragraph, COL_W)))
    return result


def prepare_blocks(blocks: list[dict], uid: str, diagnostics: list[dict]) -> list[Unit]:
    units = []
    for i, block in enumerate(blocks):
        b_uid = f"{uid}.{i}"
        if block["type"] == "text":
            units.extend(text_units(block, b_uid))
            continue
        try:
            with Image.open(block["_path"]) as original:
                image = ImageOps.exif_transpose(original).convert("RGB")
            w, h = image.size
            left, top, right, bottom = block["crop"]
            crop_box = (round(left * w), round(top * h), round(right * w), round(bottom * h))
            if crop_box[2] <= crop_box[0] or crop_box[3] <= crop_box[1]:
                raise ContentError("归一化裁剪区在实际像素中为空。")
            image = image.crop(crop_box)
        except Exception as exc:
            raise ContentError(f"无法读取图片 {block['_path']}：{exc}") from exc
        aspect = image.width / image.height
        if aspect > 6 or aspect < 1 / 6:
            diagnostics.append({"code": "image_extreme_aspect", "severity": "warning", "unit": b_uid, "source": block["_path"], "aspect_ratio": round(aspect, 3), "message": "裁图长宽比极端，原作答可能难以辨认；建议分段裁剪或增加独立原图页。"})
        units.append(Unit("image", b_uid, block.get("heading", ""), image=image,
                          source=block["_path"], crop=block["crop"],
                          max_height=block.get("max_height_pt"),
                          caption=wrap_text(block.get("caption", ""), COL_W, CAPTION_SIZE) if block.get("caption") else []))
    return units


def text_command(text: str, x: float, y: float, width: float, size: float, *, bold: bool = False, color: str = INK) -> dict:
    return dict(type="text", text=text, x=x, y=y, width=width, height=size * 1.1,
                font_size=size, bold=bold, color=color)


def header(exam: dict, page: dict, part: int, diagnostics: list[dict]) -> tuple[list[dict], float, float]:
    commands = [dict(type="rect", x=0, y=0, width=PAGE_W, height=7, fill=NAVY)]
    y = MARGIN - 3
    for line in wrap_text(exam["title"], PAGE_W - 2 * MARGIN, 16.5, FONT_BOLD):
        commands.append(text_command(line, MARGIN, y, PAGE_W - 2 * MARGIN, 16.5, bold=True, color=NAVY))
        y += 21.0
    y += 4
    date_text = exam["date_label"] + "：" + exam["exam_date"]
    for line in wrap_text(date_text, PAGE_W - 2 * MARGIN, 10.5):
        commands.append(text_command(line, MARGIN, y, PAGE_W - 2 * MARGIN, 10.5, color=GRAY))
        y += 14.0
    y += 6
    topic = page["topic"] + (f"（续{part}）" if part else "")
    for line in wrap_text(topic, PAGE_W - 2 * MARGIN, 13.0, FONT_BOLD):
        commands.append(text_command(line, MARGIN, y, PAGE_W - 2 * MARGIN, 13.0, bold=True, color=NAVY))
        y += 17.5
    y += 7
    commands.append(dict(type="rect", x=MARGIN, y=y, width=PAGE_W - 2 * MARGIN, height=0.5, fill="#bfc5cb"))
    y += 8
    if page["kind"] == "answer":
        titles = ("辅助图与前半段解答", "标准答案（整理版）")
    else:
        titles = ("原题与当时作答", "错因与逐步思路")
    for x, title in zip((MARGIN, MARGIN + COL_W + GAP), titles):
        commands.append(text_command(title, x, y, COL_W, 11.0, bold=True, color=NAVY))
    top = y + 22.0
    footer_lines = wrap_text("生成时间：" + exam["generated_at"], PAGE_W - 2 * MARGIN - 115, 8.5)
    footer_h = max(44.0, 18.0 + len(footer_lines) * 11.0 + 13.0)
    bottom = PAGE_H - footer_h
    if bottom - top < 100:
        raise ContentError("试卷标题、日期或题目标题过长，剩余正文高度不足。请保留完整信息并为页眉使用更简短的标题。")
    commands.append(dict(type="rect", x=MARGIN + COL_W + GAP / 2, y=top - 3,
                         width=0.5, height=bottom - top + 3, fill="#d4d9de"))
    return commands, top, bottom


def heading_lines(unit: Unit) -> list[str]:
    heading = unit.heading + ("（续）" if unit.continued and unit.heading else "")
    return wrap_text(heading, COL_W, HEADING_SIZE, FONT_BOLD) if heading else []


def image_geometry(unit: Unit, capacity: float) -> tuple[float, float, float]:
    assert unit.image is not None
    hh = len(heading_lines(unit)) * HEADING_LEADING + (4 if unit.heading else 0)
    ch = len(unit.caption) * CAPTION_LEADING + (4 if unit.caption else 0)
    available = capacity - hh - ch - 10
    if unit.max_height is not None:
        available = min(available, unit.max_height)
    if available < 24:
        raise ContentError(f"图片 {unit.uid} 的标题或说明太长，无法保留可读图像；请缩短说明或拆页。")
    scale = min(COL_W / unit.image.width, available / unit.image.height)
    width, height = unit.image.width * scale, unit.image.height * scale
    return width, height, hh + height + ch + 10


def add_heading(commands: list[dict], unit: Unit, x: float, y: float) -> float:
    for line in heading_lines(unit):
        commands.append(text_command(line, x, y, COL_W, HEADING_SIZE, bold=True, color=NAVY))
        y += HEADING_LEADING
    return y + (4 if unit.heading else 0)


def consume_column(queue: deque[Unit], x: float, top: float, bottom: float,
                   page_number: int, side: str, diagnostics: list[dict]) -> tuple[list[dict], list[dict]]:
    commands, boxes = [], []
    y, capacity = top, bottom - top
    while queue:
        unit = queue[0]
        remaining = bottom - y
        if unit.kind == "image":
            width, height, total = image_geometry(unit, capacity)
            if total > remaining + 0.01:
                break
            start = y
            y = add_heading(commands, unit, x, y)
            commands.append(dict(type="image", image=unit.image, x=x + (COL_W - width) / 2,
                                 y=y, width=width, height=height, unit=unit.uid))
            effective_dpi = unit.image.width / (width / 72)
            if effective_dpi < 120:
                diagnostics.append({"code": "image_low_resolution", "severity": "warning", "unit": unit.uid, "page": page_number, "effective_dpi": round(effective_dpi, 1), "message": "原图有效分辨率较低，必须目视确认手写内容可辨。"})
            y += height
            if unit.caption:
                y += 4
                for line in unit.caption:
                    commands.append(text_command(line, x, y, COL_W, CAPTION_SIZE, color=GRAY))
                    y += CAPTION_LEADING
            y += 10
            boxes.append(dict(unit=unit.uid, type="image", side=side, x=x, y=start,
                              width=COL_W, height=y - start, source=unit.source, crop=unit.crop,
                              image_pixels=list(unit.image.size), display_points=[round(width, 2), round(height, 2)],
                              effective_dpi=round(effective_dpi, 1)))
            queue.popleft()
            continue
        h_lines = heading_lines(unit)
        hh = len(h_lines) * HEADING_LEADING + (4 if unit.heading else 0)
        total = hh + len(unit.lines) * BODY_LEADING + 10
        take = len(unit.lines)
        split = False
        if total > remaining + 0.01:
            # A paragraph that fits a fresh column is kept together.
            if total <= capacity + 0.01:
                break
            take = int((remaining - hh - 10) // BODY_LEADING)
            if take < min(2, len(unit.lines)):
                break
            if len(unit.lines) - take == 1 and take > 2:
                take -= 1
            split = take < len(unit.lines)
        start = y
        y = add_heading(commands, unit, x, y)
        for line in unit.lines[:take]:
            commands.append(text_command(line, x, y, COL_W, BODY_SIZE))
            y += BODY_LEADING
        y += 10
        boxes.append(dict(unit=unit.uid, type="text", side=side, x=x, y=start,
                          width=COL_W, height=y - start, font_size=BODY_SIZE,
                          line_count=take, continued=unit.continued, split_paragraph=split))
        queue.popleft()
        if split:
            rest = copy(unit)
            rest.lines = unit.lines[take:]
            rest.continued = True
            queue.appendleft(rest)
            diagnostics.append({"code": "oversized_paragraph_split", "severity": "info", "unit": unit.uid, "page": page_number, "message": "该段长于一整栏，按已测量的文本行拆至续页；字号保持11.5磅。"})
            break
    return commands, boxes


def paginate(data: dict, diagnostics: list[dict]) -> list[dict]:
    physical = []
    for logical_i, logical in enumerate(data["pages"], 1):
        left = []
        if logical["intro"]:
            left.extend(text_units({"heading": "题目要点", "text": logical["intro"]}, f"page{logical_i}.intro"))
        left.extend(prepare_blocks(logical["left"], f"page{logical_i}.left", diagnostics))
        right = prepare_blocks(logical["right"], f"page{logical_i}.right", diagnostics)
        if logical["key_tip"]:
            right.extend(text_units({"heading": "关键指导", "text": logical["key_tip"]}, f"page{logical_i}.key_tip"))
        queues = (deque(left), deque(right))
        part, first_page = 0, len(physical) + 1
        while any(queues):
            page_number = len(physical) + 1
            commands, top, bottom = header(data["exam"], logical, part, diagnostics)
            boxes = []
            counts_before = sum(len(q) for q in queues)
            line_counts_before = sum(sum(len(u.lines) for u in q) for q in queues)
            for side, x, queue in zip(("left", "right"), (MARGIN, MARGIN + COL_W + GAP), queues):
                column_commands, column_boxes = consume_column(queue, x, top, bottom, page_number, side, diagnostics)
                if not column_boxes and not queue and part:
                    note = f"本题原作答/辅助图及前段内容见第{first_page}页。"
                    for j, line in enumerate(wrap_text(note, COL_W, 10.5)):
                        column_commands.append(text_command(line, x, top + 14 * j, COL_W, 10.5, color=GRAY))
                commands.extend(column_commands)
                boxes.extend(column_boxes)
            counts_after = sum(len(q) for q in queues)
            line_counts_after = sum(sum(len(u.lines) for u in q) for q in queues)
            if counts_before == counts_after and line_counts_before == line_counts_after:
                raise ContentError(f"题目“{logical['topic']}”的一段标题或正文无法排入新页；请拆成更短的语义段落。")
            for box in boxes:
                if box["y"] < top - 0.1 or box["y"] + box["height"] > bottom + 0.1:
                    raise ContentError(f"内部排版校验失败：第{page_number}页 {box['unit']} 超出正文边界。")
            physical.append(dict(number=page_number, logical_page=logical_i, continuation=part,
                                 topic=logical["topic"], kind=logical["kind"],
                                 content_top=top, content_bottom=bottom, commands=commands, boxes=boxes))
            part += 1
    return physical


def add_footers(pages: list[dict], exam: dict):
    for p in pages:
        y = p["content_bottom"] + 7
        p["commands"].append(dict(type="rect", x=MARGIN, y=y, width=PAGE_W - 2 * MARGIN, height=0.5, fill="#bdc4cb"))
        y += 7
        lines = wrap_text("生成时间：" + exam["generated_at"], PAGE_W - 2 * MARGIN - 115, 8.5)
        for line in lines:
            p["commands"].append(text_command(line, MARGIN, y, PAGE_W - 2 * MARGIN - 115, 8.5, color=GRAY))
            y += 11
        p["commands"].append(text_command(f"第{p['number']}/{len(pages)}页", PAGE_W - MARGIN - 105,
                                             p["content_bottom"] + 14, 105, 8.5, color=GRAY))


def encode_image(command: dict, image_dpi: int) -> tuple[bytes, str]:
    im = command["image"].copy()
    target = (max(1, math.ceil(command["width"] / 72 * image_dpi)), max(1, math.ceil(command["height"] / 72 * image_dpi)))
    im.thumbnail(target, Image.Resampling.LANCZOS)
    buf = BytesIO()
    im.save(buf, format="JPEG", quality=93, subsampling=0, optimize=True)
    return buf.getvalue(), "image/jpeg"


def write_pdf(path: Path, pages: list[dict], exam: dict, image_dpi: int):
    c = canvas.Canvas(str(path), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle(exam["title"] + " - 错题讲评册")
    c.setAuthor("错题讲评册")
    for page in pages:
        for cmd in page["commands"]:
            if cmd["type"] == "text":
                c.setFillColor(HexColor(cmd["color"]))
                c.setFont(FONT_BOLD if cmd["bold"] else FONT_REG, cmd["font_size"])
                c.drawString(cmd["x"], PAGE_H - cmd["y"] - cmd["font_size"], cmd["text"])
            elif cmd["type"] == "rect":
                c.setFillColor(HexColor(cmd["fill"]))
                c.rect(cmd["x"], PAGE_H - cmd["y"] - cmd["height"], cmd["width"], cmd["height"], fill=1, stroke=0)
            elif cmd["type"] == "image":
                raw, _ = encode_image(cmd, image_dpi)
                c.drawImage(ImageReader(BytesIO(raw)), cmd["x"], PAGE_H - cmd["y"] - cmd["height"],
                            width=cmd["width"], height=cmd["height"])
        c.showPage()
    c.save()


def browser_font(path: Path, text: str, diagnostics: list[dict]) -> tuple[bytes, str]:
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont as FTFont
        font = FTFont(str(path), fontNumber=0)
        options = subset.Options()
        options.name_IDs = [0, 1, 2, 3, 4, 5, 6]
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=text)
        subsetter.subset(font)
        font.flavor = "woff"
        out = BytesIO()
        font.save(out)
        return out.getvalue(), "font/woff"
    except Exception as exc:
        diagnostics.append({"code": "html_font_full_file", "severity": "info", "message": "网页已嵌入完整字体；可安装 fontTools 以减小体积。", "detail": type(exc).__name__})
        return path.read_bytes(), "font/collection" if path.suffix.lower() == ".ttc" else "font/ttf"


def write_html(path: Path, pages: list[dict], exam: dict, reg: Path, bold: Path, all_text: str, image_dpi: int, diagnostics: list[dict]):
    css_path = Path(__file__).resolve().parents[1] / "assets/layout.css"
    if not css_path.is_file():
        raise ContentError(f"缺少版式资源：{css_path}")
    css = css_path.read_text(encoding="utf-8")
    raw, mime = browser_font(reg, all_text + STATIC_TEXT, diagnostics)
    uri = "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")
    css += "\n@font-face{font-family:BookletRegular;src:url('" + uri + "');font-weight:400;}"
    if reg == bold:
        css += "\n.textline.bold{font-family:BookletRegular;font-weight:600;}"
    else:
        b_raw, b_mime = browser_font(bold, all_text + STATIC_TEXT, diagnostics)
        b_uri = "data:" + b_mime + ";base64," + base64.b64encode(b_raw).decode("ascii")
        css += "\n@font-face{font-family:BookletBold;src:url('" + b_uri + "');font-weight:600;}"
    articles = []
    for page in pages:
        parts = []
        for cmd in page["commands"]:
            pos = f"left:{cmd['x']:.3f}pt;top:{cmd['y']:.3f}pt;width:{cmd['width']:.3f}pt;height:{cmd['height']:.3f}pt;"
            if cmd["type"] == "text":
                cls = "textline bold" if cmd["bold"] else "textline"
                parts.append(f'<div class="{cls}" style="{pos}font-size:{cmd["font_size"]:.3f}pt;color:{cmd["color"]}">{escape(cmd["text"])}</div>')
            elif cmd["type"] == "rect":
                parts.append(f'<div class="rule" style="{pos}background:{cmd["fill"]}"></div>')
            else:
                raw, mime = encode_image(cmd, image_dpi)
                uri = "data:" + mime + ";base64," + base64.b64encode(raw).decode("ascii")
                parts.append(f'<img class="figure" alt="原作答或辅助图" style="{pos}" src="{uri}">')
        articles.append('<article class="sheet" data-page="' + str(page["number"]) + '">' + "".join(parts) + '</article>')
    html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + escape(exam["title"] + " - 错题讲评册") + '</title><style>' + css + '</style></head><body><div class="toolbar"><button type="button" onclick="window.print()">打印讲评册</button>A4横向，共' + str(len(pages)) + '页。试卷日期与生成时间分开显示；请先查看打印预览。</div>' + "".join(articles) + '</body></html>'
    path.write_text(html, encoding="utf-8")


def output_stem(exam: dict) -> str:
    def clip_utf8(value: str, limit: int) -> str:
        encoded = value.encode("utf-8")
        return encoded[:limit].decode("utf-8", errors="ignore")
    # Preserve the date even for a very long title and stay below common 255-byte
    # filename limits on filesystems that count UTF-8 bytes rather than characters.
    name = f"{clip_utf8(exam['title'], 100)}_{clip_utf8(exam['exam_date'], 50)}_错题讲评册"
    name = unicodedata.normalize("NFKC", name)
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", name).strip(". ")
    return name.rstrip(". ") or "错题讲评册"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="经用户确认元数据的讲评 JSON")
    parser.add_argument("--output-dir", type=Path, help="输出目录，默认输入文件旁的 output")
    parser.add_argument("--stem", help="文件名，不含扩展名")
    parser.add_argument("--font", help="中文 TrueType 字体 .ttf/.ttc")
    parser.add_argument("--bold-font", help="可选粗体字体，默认同一字体")
    parser.add_argument("--image-dpi", type=int, default=220, help="派生图片的最大输出 DPI，默认220")
    parser.add_argument("--overwrite", action="store_true", help="覆盖同名输出（不会修改输入图片）")
    parser.add_argument("--validate-only", action="store_true", help="仅校验结构与图片路径，不生成文件")
    args = parser.parse_args(argv)
    try:
        source = args.input.expanduser().resolve()
        data = json.loads(source.read_text(encoding="utf-8"))
        data = validate(data, source.parent)
        if args.validate_only:
            print(json.dumps({"valid": True, "logical_pages": len(data["pages"]), "title": data["exam"]["title"], "exam_date": data["exam"]["exam_date"]}, ensure_ascii=False))
            return 0
        if not 100 <= args.image_dpi <= 600:
            raise ContentError("--image-dpi 必须在100至600之间。")
        out_dir = (args.output_dir.expanduser() if args.output_dir else source.parent / "output").resolve()
        stem = args.stem or output_stem(data["exam"])
        if Path(stem).name != stem or stem in ("", ".", "..") or "/" in stem or "\\" in stem:
            raise ContentError("--stem 只能是文件名，不能包含路径。")
        if len(stem.encode("utf-8")) > 225:
            raise ContentError("--stem 太长，请缩短到225个UTF-8字节以内。")
        targets = {k: out_dir / (stem + ext) for k, ext in (("pdf", ".pdf"), ("html", ".html"), ("layout", ".layout.json"))}
        if not args.overwrite:
            existing = [str(p) for p in targets.values() if p.exists()]
            if existing:
                raise ContentError("输出已存在；若确需更新，请显式加 --overwrite：" + "；".join(existing))
        diagnostics = []
        all_text = gather_text(data) + STATIC_TEXT
        reg = find_font(args.font, all_text, diagnostics)
        bold = register_bold(args.bold_font, reg, diagnostics, all_text)
        pages = paginate(data, diagnostics)
        add_footers(pages, data["exam"])
        # Include dynamically generated continuation and page-count labels in the subset.
        rendered_text = "".join(cmd["text"] for p in pages for cmd in p["commands"] if cmd["type"] == "text")
        out_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".booklet-", dir=out_dir) as tmp:
            temp = Path(tmp)
            write_pdf(temp / "booklet.pdf", pages, data["exam"], args.image_dpi)
            write_html(temp / "booklet.html", pages, data["exam"], reg, bold, all_text + rendered_text, args.image_dpi, diagnostics)
            metadata = dict(exam=data["exam"], page_size_points=[PAGE_W, PAGE_H],
                            body_font_size=BODY_SIZE, font_size=BODY_SIZE, fonts={"regular": str(reg), "bold": str(bold)},
                            logical_pages=len(data["pages"]), physical_pages=len(pages), page_count=len(pages),
                            pages=[{k: v for k, v in p.items() if k != "commands"} for p in pages],
                            diagnostics=diagnostics)
            (temp / "booklet.layout.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
            for key, temp_name in (("pdf", "booklet.pdf"), ("html", "booklet.html"), ("layout", "booklet.layout.json")):
                (temp / temp_name).replace(targets[key])
        print(json.dumps({"pdf": str(targets["pdf"]), "html": str(targets["html"]), "layout": str(targets["layout"]),
                          "physical_pages": len(pages), "diagnostics": diagnostics}, ensure_ascii=False))
        return 0
    except (ContentError, OSError, json.JSONDecodeError) as exc:
        print("错误：" + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
