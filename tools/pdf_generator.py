import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.config import settings


class PDFGenerator:
    def generate(self, title: str, content: str) -> dict:
        os.makedirs(settings.reports_path, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_{timestamp}.pdf"
        filepath = os.path.join(settings.reports_path, filename)

        pdf = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter

        y = height - 72

        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(72, y, title)

        y -= 40
        pdf.setFont("Helvetica", 10)

        for line in content.split("\n"):
            if y < 72:
                pdf.showPage()
                y = height - 72
                pdf.setFont("Helvetica", 10)

            pdf.drawString(72, y, line[:100])
            y -= 16

        pdf.save()

        return {
            "success": True,
            "file_path": filepath,
        }