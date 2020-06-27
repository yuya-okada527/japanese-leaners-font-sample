import os
from pathlib import Path
from io import BytesIO
from dataclasses import dataclass
from typing import Tuple

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait, landscape
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
    practice_num: int
    sample_num: int
    pagesize: Tuple[float, float]

    @classmethod
    def make_layout(cls, font_size: FontSize, horizontal: bool):

        if horizontal:
            pagesize = landscape(A4)
        else:
            pagesize = portrait(A4)

        return cls(
            font_size=font_size.value["pixel"],
            practice_num=4,
            sample_num=2,
            pagesize=pagesize
        )


@dataclass()
class PdfWriter:
    layout: Layout
    font_name: str = "JapaneseLearnersFont"

    def write(self, text):

        # テーブルに表示するデータを作成
        data = self.make_data(text)

        with BytesIO() as output:

            # 白紙のドキュメントを作成
            doc = canvas.Canvas(output, pagesize=self.layout.pagesize, bottomup=False)

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

    def make_data(self, text: str):
        # 練習用の行を作成
        sample_row = [char for char in text]
        practice_rows = [["｜" for _ in text] for _ in range(self.layout.practice_num)]

        # データの作成
        data = []
        for _ in range(self.layout.sample_num):
            data.extend(practice_rows)
            data.append(sample_row)

        return data

    @classmethod
    def make_pdf_writer(cls, font_size: FontSize, horizontal: bool):
        layout = Layout.make_layout(font_size, horizontal)
        return cls(layout)
