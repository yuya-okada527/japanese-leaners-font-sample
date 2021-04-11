import os
from pathlib import Path
from io import BytesIO
from dataclasses import dataclass
from typing import List, Tuple

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm

from ..config import settings
from ..infra.s3 import S3Client
from ..enums import FontSize, Env

FONT_NAME = "JapaneseLearnersFont"
FONT_NAME2B = "JapaneseLearnersFont2B"
FONT_KEY = "fonts/ttf/J-Learners1.ttf"
FONT_KEY2B = "fonts/ttf/J-Learners2B.ttf"
COLOR_GRAY = (0.7, 0.7, 0.7)
SPACES = " 　"


def init_font():
    print("init_font")
    if settings.env == Env.LOCAL:
        return os.path.join(
            Path(__file__).resolve().parents[2],
            "fonts",
            "ttf",
            "J-Learners1.ttf"
        )

    return BytesIO(S3Client.get_object(FONT_KEY).get()["Body"].read())


def init_font2b():
    print("init_font2b")
    if settings.env == Env.LOCAL:
        return os.path.join(
            Path(__file__).resolve().parents[2],
            "fonts",
            "ttf",
            "J-Learners2B.ttf"
        )

    return BytesIO(S3Client.get_object(FONT_KEY2B).get()["Body"].read())


# PDF生成の設定を変更
pdfmetrics.registerFont(TTFont(FONT_NAME, init_font()))
pdfmetrics.registerFont(TTFont(FONT_NAME2B, init_font2b()))


@dataclass()
class Layout:
    font_size: int
    practice_num: int
    sample_num: int
    pagesize: Tuple[float, float]
    draw_on: Tuple[int, int]

    @classmethod
    def make_layout(cls, font_size: FontSize, horizontal: bool):

        if horizontal:
            pagesize = landscape(A4)
            sample_num = 1
        else:
            pagesize = portrait(A4)
            sample_num = 2

        return cls(
            font_size=font_size.value["pixel"],
            practice_num=font_size.value["practice_num"] if not horizontal else font_size.value["horizontal_practice_num"],
            sample_num=sample_num,
            pagesize=pagesize,
            draw_on=font_size.value["draw_on"]
        )

    @classmethod
    def optimize_layout(cls, text: str):
        text_size = len(text)
        if text_size <= 6:
            return cls.make_layout(FontSize.LARGE, False)
        elif text_size <= 8:
            return cls.make_layout(FontSize.MIDDLE, False)
        elif text_size <= 10:
            return cls.make_layout(FontSize.SMALL, False)
        elif text_size <= 13:
            return cls.make_layout(FontSize.MIDDLE, True)
        elif text_size <= 15:
            return cls.make_layout(FontSize.SMALL, True)
        else:
            raise ValueError(f"text size={text_size} > 15")


@dataclass()
class PdfWriter:
    layout: Layout
    font_name: str = FONT_NAME

    def write(self, text_list: List[str]):

        with BytesIO() as output:

            # 白紙のドキュメントを作成
            doc = canvas.Canvas(output, pagesize=self.layout.pagesize, bottomup=False)

            # ドキュメント設定
            # フォントを指定
            doc.setFont(self.font_name, self.layout.font_size)

            for text in text_list:
                if text is None or len(text) == 0:
                    continue

                # テーブルに表示するデータを作成
                data = self.make_data(text)

                # テーブルを作成
                table = Table(data)

                # テーブルスタイルを作成
                table_style = [
                    ("FONT", (0, 0), (-1, -1), self.font_name, self.layout.font_size),
                    ("FONT",
                    (0, self.layout.practice_num),
                    (len(text) - 1, self.layout.practice_num),
                    FONT_NAME2B, self.layout.font_size),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]

                if self.layout.sample_num == 2:
                    table_style.append(
                        ("FONT",
                        (0, self.layout.practice_num * 2 + 2),
                        (len(text) - 1, self.layout.practice_num * 2 + 2),
                        FONT_NAME2B, self.layout.font_size),
                    )
                table.setStyle(TableStyle(table_style))

                # テーブルを描画
                table.wrapOn(doc, self.layout.draw_on[0] * mm, self.layout.draw_on[1] * mm)
                table.drawOn(doc, self.layout.draw_on[0] * mm, self.layout.draw_on[1] * mm)

                # ドキュメントを描画する
                doc.showPage()

            doc.save()
            return output.getvalue()

    def make_data(self, text: str):
        # 練習用の行を作成
        sample_row    = [[char for char in text] for _ in range(2)]
        practice_rows = [[PdfWriter.practice_char(char) for char in text]
                         for _ in range(self.layout.practice_num)]

        # データの作成
        data = []
        for _ in range(self.layout.sample_num):
            data.extend(practice_rows)
            data.extend(sample_row)

        return data

    @staticmethod
    def practice_char(char):
        if char in SPACES:
            return " "
        return "｜"

    @classmethod
    def make_pdf_writer(cls, font_size: FontSize, horizontal: bool):
        layout = Layout.make_layout(font_size, horizontal)
        return cls(layout)

    @classmethod
    def from_layout(cls, layout: Layout):
        return cls(layout)
