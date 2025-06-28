from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


class TemplateEngine:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TemplateEngine, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.templates_dir = Path(__file__).parent.parent / "templates"
            self.templates_dir.mkdir(exist_ok=True)

            self.env = Environment(
                loader=FileSystemLoader(str(self.templates_dir)),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )

            self.env.filters['file_icon'] = self._get_file_icon
            self.env.filters['file_type_color'] = self._get_file_type_color
            self.env.filters['escape_html'] = self._escape_html

            self.initialized = True

    def render(self, template_name: str, **kwargs) -> str:
        try:
            template = self.env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            print(f"Error rendering template {template_name}: {e}")
            return f"<div class='template-error'>Template rendering error: {e}</div>"

    def _get_file_icon(self, file_type: str, subtype: str = '') -> str:
        if file_type == 'medical':
            if subtype == 'dicom':
                return '🏥'
            elif subtype == 'nifti':
                return '🧠'
            else:
                return '⚕️'

        icons = {
            'image': '🖼️',
            'text': '📄',
            'unknown': '📎'
        }
        return icons.get(file_type, '📎')

    def _get_file_type_color(self, file_type: str) -> str:
        colors = {
            'image': '#10b981',
            'text': '#3b82f6',
            'medical': '#e11d48',
            'unknown': '#6b7280'
        }
        return colors.get(file_type, '#6b7280')

    def _escape_html(self, text: str) -> str:
        return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))


template_engine = TemplateEngine()
