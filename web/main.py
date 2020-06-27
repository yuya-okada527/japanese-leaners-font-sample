from urllib.parse import quote

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
    horizontal = request.args.get("horizontal", default=False, type=bool)

    # パラメータのバリデーション
    if len(text) == 0:
        return render_template(
            "index.html",
            workbooks=get_workbooks(),
            error="入力欄が未記入です。"
        ), 421

    # サンプルのPDFファイルを作成する
    pdf_writer = PdfWriter.make_pdf_writer(font_size, horizontal)
    pdf_file = pdf_writer.write(text)

    # レスポンスの作成
    response = make_response(pdf_file)

    # ファイル名を作成
    file_name = quote(text + ".pdf")
    response.headers['Content-Disposition'] = f"attachment; filename={file_name}; filename*=UTF-8''{file_name}"
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

    # ファイル名を作成
    file_name = quote(key.split("/")[-1])
    response.headers['Content-Disposition'] = f"attachment; filename={file_name}; filename*=UTF-8''{file_name}"
    response.mimetype = 'application/pdf'
    return response


@app.errorhandler(Exception)
def internal_server_error(error):
    log.error(error)
    return render_template("error_500.html")


if __name__ == "__main__":
    # app.run(host="0.0.0.0")
    app.run(debug=True)
