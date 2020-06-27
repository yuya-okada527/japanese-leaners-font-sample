import os
from pathlib import Path
from io import BytesIO
from dataclasses import dataclass

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm

# from ..infra.s3 import S3Client
from ..enums import FontSize

# FONT_KEY = "fonts/ttf/JapaneseLearners1.ttf"
# FONT_FILE = S3Client.get_object(FONT_KEY).get()["Body"].read()
FONT_PATH = os.path.join(
    Path(__file__).resolve().parents[3],
    "fonts",
    "ttf",
    "JapaneseLearners1.ttf"
)


@dataclass()
class Layout:
    font_size: int

    @classmethod
    def make_layout(cls, font_size: FontSize):
        return cls(font_size.value["pixel"])


@dataclass()
class PdfWriter:
    layout: Layout
    font_name: str = "JapaneseLearnersFont"

    def write(self, text):

        # テーブルに表示するデータを作成
        data = PdfWriter.make_data(text)

        with BytesIO() as output:

            # 白紙のドキュメントを作成
            doc = canvas.Canvas(output, pagesize=portrait(A4), bottomup=False)

            # ドキュメント設定
            # フォントを指定
            pdfmetrics.registerFont(TTFont(self.font_name, FONT_PATH))
            doc.setFont(self.font_name, self.layout.font_size)

            # テーブルを作成
            table = Table(data)
            table.setStyle(TableStyle([
                ("FONT",         (0, 0), (-1, -1), self.font_name, self.layout.font_size),
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]))
            table.wrapOn(doc, 10 * mm, 20 * mm)
            table.drawOn(doc, 10 * mm, 20 * mm)

            # ドキュメントを描画する
            doc.showPage()
            doc.save()
            return output.getvalue()

    @classmethod
    def make_data(cls, text: str):
        return [
            ["｜" for _ in text],
            ["｜" for _ in text],
            ["｜" for _ in text],
            ["｜" for _ in text],
            [char for char in text],
            ["｜" for _ in text],
            ["｜" for _ in text],
            ["｜" for _ in text],
            ["｜" for _ in text],
            [char for char in text]
        ]

    @classmethod
    def make_pdf_writer(cls, font_size: FontSize):
        layout = Layout.make_layout(font_size)
        return cls(layout)
