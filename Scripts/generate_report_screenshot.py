import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import textwrap

def render_text_to_image(text: str, out_path: Path, width: int = 1200, font_size: int = 14):
    # use default font
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    # estimate character width using a temporary draw
    tmp_img = Image.new('RGB', (10, 10), color='white')
    tmp_draw = ImageDraw.Draw(tmp_img)
    if font:
        try:
            cw, ch = tmp_draw.textsize('A', font=font)
        except Exception:
            cw, ch = (8, 16)
    else:
        cw, ch = (8, 16)

    max_chars = max(40, width // max(6, cw))
    lines = []
    for paragraph in text.splitlines():
        if paragraph.strip() == '':
            lines.append('')
            continue
        wrapped = textwrap.wrap(paragraph, width=max_chars)
        if not wrapped:
            lines.append('')
        else:
            lines.extend(wrapped)

    line_height = ch + 4
    padding = 20
    img_h = padding * 2 + line_height * len(lines)
    img = Image.new('RGB', (width, max(200, img_h)), color='white')
    draw = ImageDraw.Draw(img)
    y = padding
    for ln in lines:
        draw.text((padding, y), ln, fill='black', font=font)
        y += line_height

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)

def main():
    if len(sys.argv) < 3:
        print('Usage: generate_report_screenshot.py <input_md> <output_png>')
        sys.exit(2)
    inp = Path(sys.argv[1])
    out = Path(sys.argv[2])
    if not inp.exists():
        print('Input not found:', inp)
        sys.exit(1)
    text = inp.read_text(encoding='utf-8')
    render_text_to_image(text, out)
    print('Saved screenshot to', out)

if __name__ == '__main__':
    main()
