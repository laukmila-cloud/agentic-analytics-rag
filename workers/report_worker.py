from tools.pdf_generator import PDFGenerator


class ReportWorker:
    def __init__(self):
        self.pdf_generator = PDFGenerator()

    def generate(self, title: str, content: str) -> dict:
        return self.pdf_generator.generate(title=title, content=content)