from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm

from ..infra.s3 import S3Client


FONT_KEY = "fonts/ttf/JapaneseLearners1.ttf"
FONT_FILE = S3Client.get_object(FONT_KEY).get()["Body"].read()


class PdfWriter:

    def __init__(
            self,
            text: str,
            font_name: str = "JapaneseLearnersFont",
            font_size: int = 50):
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.data = [
            ["｜" for _ in self.text],
            ["｜" for _ in self.text],
            ["｜" for _ in self.text],
            ["｜" for _ in self.text],
            [char for char in self.text],
            ["｜" for _ in self.text],
            ["｜" for _ in self.text],
            ["｜" for _ in self.text],
            ["｜" for _ in self.text],
            [char for char in self.text]
        ]

    def write(self):
        with BytesIO() as output:

            # 白紙のドキュメントを作成
            doc = canvas.Canvas(output, pagesize=portrait(A4), bottomup=False)

            # ドキュメント設定
            # フォントを指定
            pdfmetrics.registerFont(TTFont(self.font_name, BytesIO(FONT_FILE)))
            doc.setFont(self.font_name, self.font_size)

            # テーブルを作成
            table = Table(self.data)
            table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), self.font_name, self.font_size),
            ]))
            table.wrapOn(doc, 30 * mm, 30 * mm)
            table.drawOn(doc, 30 * mm, 30 * mm)

            # ドキュメントを描画する
            doc.showPage()
            doc.save()
            return output.getvalue()

