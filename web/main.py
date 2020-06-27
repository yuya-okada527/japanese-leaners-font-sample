from flask import (
    Flask,
    request,
    render_template,
    make_response
)

from .enums import FontSize
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

    # リクエストパラメータを取得
    text = request.args.get("text")
    font_size = FontSize.name_of(request.args.get("font-size"))

    # サンプルのPDFファイルを作成する
    pdf_writer = PdfWriter.make_pdf_writer(font_size)
    pdf_file = pdf_writer.write(text)

    # レスポンスの作成
    response = make_response(pdf_file)
    response.headers['Content-Disposition'] = "attachment; filename=sample.pdf"
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


if __name__ == "__main__":
    # app.run(host="0.0.0.0")
    app.run(debug=True)
