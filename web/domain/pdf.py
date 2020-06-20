from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm

from ..config import settings


class PdfWriter:

    def __init__(self,
                 text: str,
                 font_name: str = "JapaneseLearnersFont",
                 font_size: int = 30):
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.data = [
            [char for char in self.text],
            ["　" for _ in self.text],
            ["　" for _ in self.text],
            ["　" for _ in self.text],
            ["　" for _ in self.text]
        ]

    def write(self):
        with BytesIO() as output:

            # 白紙のドキュメントを作成
            doc = canvas.Canvas(output, pagesize=portrait(A4), bottomup=False)

            # ドキュメント設定
            # フォントを指定
            pdfmetrics.registerFont(TTFont(self.font_name, settings.fonts_path))
            doc.setFont(self.font_name, self.font_size)

            # テーブルを作成
            table = Table(self.data)
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, self.font_size),
            ]))
            table.wrapOn(doc, 50 * mm, 10 * mm)
            table.drawOn(doc, 50 * mm, 10 * mm)

            # ドキュメントを描画する
            doc.showPage()
            doc.save()
            return output.getvalue()

