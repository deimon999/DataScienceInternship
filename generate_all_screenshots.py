from pathlib import Path
import sys

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_for_filename
    from pygments.formatters import ImageFormatter
except Exception:
    print('Missing dependencies: please run pip install pygments pillow')
    sys.exit(2)


ROOT = Path(__file__).resolve().parent
OUT = ROOT

targets = {
    'task1': ROOT / 'Task-1-ETL-Pipeline' / 'etl_pipeline.py',
    'task2': ROOT / 'Task-2-Deep-Learning' / 'task2_deep_learning.py',
    'task3': ROOT / 'Task-3-E-Commerce-Product-Page' / 'product_page.html',
}

outputs = {
    'task1': OUT / 'task1_etl_screenshot.png',
    'task2': OUT / 'task2_deep_learning_screenshot.png',
    'task3': OUT / 'task3_product_page_screenshot.png',
}


def make_image(src: Path, dst: Path):
    if not src.exists():
        print('missing', src)
        return False
    code = src.read_text(encoding='utf-8', errors='replace')
    try:
        lexer = get_lexer_for_filename(str(src.name), code)
    except Exception:
        from pygments.lexers import TextLexer

        lexer = TextLexer()

    formatter = ImageFormatter(font_name='DejaVu Sans Mono', line_numbers=True, font_size=14, image_format='PNG')
    img_data = highlight(code, lexer, formatter)
    dst.write_bytes(img_data)
    print('wrote', dst)
    return True


def main():
    for k, src in targets.items():
        dst = outputs[k]
        success = make_image(src, dst)
        if not success:
            print('Failed for', src)


if __name__ == '__main__':
    main()
