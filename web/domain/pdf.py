from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import Table
from reportlab.lib.units import mm


class PdfWriter:

    def __init__(self, text: str):
        self.text = text
        self.data = [
            [char for char in self.text],
            ["　" for _ in self.text],
            ["　" for _ in self.text],
            ["　" for _ in self.text],
            ["　" for _ in self.text]
        ]

    def write(self):
        with BytesIO() as output:
            doc = canvas.Canvas(output, pagesize=portrait(A4), bottomup=False)
            table = Table(self.data)
            # tableを描き出す位置を指定
            table.wrapOn(doc, 50 * mm, 10 * mm)
            table.drawOn(doc, 50 * mm, 10 * mm)
            doc.showPage()
            doc.save()
            return output.getvalue()



