from pathlib import Path
from typing import Optional


class StaticAssets:
    def __init__(self, static_dir: Optional[Path] = None):
        if static_dir is None:
            self.static_dir = Path(__file__).parent.parent.parent / "static"
        else:
            self.static_dir = static_dir

        self.css_dir = self.static_dir / "css"
        self.js_dir = self.static_dir / "js"

    def load_css(self, filename: str) -> str:
        css_file = self.css_dir / filename
        if not css_file.exists():
            print(f"Warning: CSS file {css_file} not found")
            return ""

        try:
            content = css_file.read_text(encoding='utf-8')
            return f"<style>\n{content}\n</style>"
        except Exception as e:
            print(f"Error loading CSS file {css_file}: {e}")
            return ""

    def load_js(self, filename: str) -> str:
        js_file = self.js_dir / filename
        if not js_file.exists():
            print(f"Warning: JavaScript file {js_file} not found")
            return ""

        try:
            return js_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error loading JavaScript file {js_file}: {e}")
            return ""

    def load_multiple_css(self, *filenames: str) -> str:
        combined_css = []
        for filename in filenames:
            css_content = self.load_css(filename)
            if css_content:
                combined_css.append(css_content)
        return "\n".join(combined_css)

    def load_multiple_js(self, *filenames: str) -> str:
        combined_js = []
        for filename in filenames:
            js_content = self.load_js(filename)
            if js_content:
                combined_js.append(js_content)
        return "\n".join(combined_js)


assets = StaticAssets()
