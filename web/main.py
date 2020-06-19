from io import BytesIO

from flask import (
    Flask,
    request,
    render_template,
    make_response
)
from reportlab.pdfgen import canvas

from .domain.service import get_workbooks, get_workbook
from .domain.pdf import PdfWriter
from .logger import create_logger


app = Flask(__name__)

log = create_logger(__file__)


@app.route("/")
def index():
    return render_template("index.html", workbooks=get_workbooks())


@app.route("/create")
def create():

    log.info("info")
    log.debug("debug")

    # リクエストパラメータを取得
    message = request.args.get("text")

    # PDFを作成
    with BytesIO() as output:
        # キャンパスの作成
        p = canvas.Canvas(output)

        # 描画
        p.drawString(100, 100, message)
        p.showPage()

        # 書き出し
        p.save()
        pdf_out = output.getvalue()

    # レスポンスの作成
    response = make_response(pdf_out)
    response.headers['Content-Disposition'] = "attachment; filename=sakulaci.pdf"
    response.mimetype = 'application/pdf'

    return response


@app.route("/download")
def download():

    # クエリパラメータからキーを取得
    key = request.args.get("key")

    # S3から教材を取得
    workbook = get_workbook(key)

    # レスポンスを作成する
    response = make_response(workbook)
    response.headers['Content-Disposition'] = "attachment; filename=" + "workbook.pdf"  # TODO ファイル名 オリジナルのキー名を使うと文字コード系のエラーがでる
    response.mimetype = 'application/pdf'
    return response


@app.route("/pdf")
def pdf():

    # サンプルのPDFファイルを作成する
    pdf_writer = PdfWriter("abcdef")
    pdf_file = pdf_writer.write()

    # レスポンスを作成する
    response = make_response(pdf_file)
    response.headers['Content-Disposition'] = "attachment; filename=sample.pdf"
    response.mimetype = 'application/pdf'
    return response


if __name__ == "__main__":
    app.run(debug=True)
