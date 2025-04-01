from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("app/templates"),
                  trim_blocks=True,  # Убирает лишние пустые строки
                  lstrip_blocks=True  # Убирает лишние пробелы перед блоками
                   )

def render_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(context)
