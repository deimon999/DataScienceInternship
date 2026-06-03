from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'screenshots'
OUT.mkdir(exist_ok=True)


def generate_code_images():
    try:
        from pygments import highlight
        from pygments.lexers import get_lexer_for_filename
        from pygments.formatters import ImageFormatter
    except Exception as e:
        print('Missing Pygments or Pillow. Install with: pip install pygments pillow')
        return

    files = list(ROOT.rglob('*.py')) + list(ROOT.rglob('*.md'))
    # exclude virtualenv and output folders
    files = [f for f in files if '.venv' not in str(f) and 'screenshots' not in str(f)]

    for f in files:
        rel = f.relative_to(ROOT)
        out_name = OUT / (str(rel).replace('/', '_').replace('\\', '_') + '.png')
        try:
            code = f.read_text(encoding='utf-8', errors='replace')
        except Exception:
            print('Skipping (read error):', f)
            continue
        try:
            lexer = get_lexer_for_filename(str(f.name), code)
        except Exception:
            from pygments.lexers import TextLexer

            lexer = TextLexer()

        # Try common Windows monospace fonts first
        fonts = ['Consolas', 'Courier New', 'DejaVu Sans Mono']
        success = False
        for font in fonts:
            try:
                formatter = ImageFormatter(font_name=font, line_numbers=True, font_size=14, image_format='PNG')
                img = highlight(code, lexer, formatter)
                out_name.write_bytes(img)
                print('wrote', out_name)
                success = True
                break
            except Exception as e:
                # try next font
                continue
        if not success:
            try:
                formatter = ImageFormatter(line_numbers=True, font_size=14, image_format='PNG')
                img = highlight(code, lexer, formatter)
                out_name.write_bytes(img)
                print('wrote', out_name)
            except Exception as e:
                print('Failed to render image for', f, 'error:', e)


def render_html_screenshots():
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print('Playwright not installed. Install with: pip install playwright')
        return

    html_files = [p for p in ROOT.rglob('*.html') if '.venv' not in str(p)]
    if not html_files:
        print('No HTML files found')
        return

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        for h in html_files:
            path = h.resolve()
            url = f'file:///{path.as_posix()}'
            try:
                page.goto(url, wait_until='networkidle')
                out_name = OUT / (h.relative_to(ROOT).as_posix().replace('/', '_').replace('\\', '_') + '.png')
                page.screenshot(path=str(out_name), full_page=True)
                print('rendered', out_name)
            except Exception as e:
                print('Failed to render', h, 'error:', e)
        browser.close()


def main():
    print('Generating code images...')
    generate_code_images()
    print('Rendering HTML pages...')
    render_html_screenshots()


if __name__ == '__main__':
    main()
