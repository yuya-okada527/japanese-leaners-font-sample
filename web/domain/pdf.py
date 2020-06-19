from io import BytesIO
from reportlab.pdfgen import canvas


class PdfWriter:

    def __init__(self, text: str):
        self.text = text

    def write(self):
        with BytesIO() as output:
            pass


