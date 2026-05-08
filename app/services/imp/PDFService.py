import io
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from app.models import Presupuesto


class PDFService:
    def __init__(self):
        self.env = Environment(loader=FileSystemLoader("app/templates"))

    def generar_presupuesto_pdf(self, presupuesto: Presupuesto) -> bytes:
        """
        Recibe un objeto Presupuesto (SQLAlchemy model) con sus relaciones cargadas.
        """
        template = self.env.get_template("presupuesto_pro.html")
        
        html_content = template.render(p=presupuesto)

        buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(buffer)
        
        return buffer.getvalue()