from urllib.parse import quote

from flask import (
    Flask,
    request,
    render_template,
    make_response
)

from .enums import FontSize
from .domain.service import get_workbooks, get_workbook
from .domain.pdf import PdfWriter, Layout
from .logger import create_logger
from .config import settings

MAX_TEXT_SIZE = 15


app = Flask(__name__)

log = create_logger(__file__)


@app.route("/")
def index():
    return render_template(
        "index.html",
        workbooks=get_workbooks(),
        env=settings.env.value
    )


@app.route("/create")
def create():

    # リクエストパラメータを取得
    text = request.args.get("text")
    # パラメータのバリデーション
    if text is None or len(text) == 0:
        # log.info("Validation Error: text field is empty.")
        return render_template(
            "index.html",
            workbooks=get_workbooks(),
            error="入力欄が未記入です。",
            env=settings.env.value
        ), 421

    try:
        font_size = FontSize.name_of(request.args.get("font-size"))
    except ValueError:
        return render_template(
            "index.html",
            workbooks=get_workbooks(),
            error=f"フォントサイズの指定がありません。",
            env=settings.env.value

        ), 421
    horizontal = request.args.get("horizontal", default=False, type=bool)

    # 大きなサイズのリクエストが来ると負担になるので、制限する
    if len(text) > MAX_TEXT_SIZE:
        # log.info(f"Validation Error: text size > {MAX_TEXT_SIZE} size=" + str(len(text)))
        return render_template(
            "index.html",
            workbooks=get_workbooks(),
            error=f"文字数は{MAX_TEXT_SIZE}文字までとなっています。",
            env=settings.env.value
        ), 421

    # サンプルのPDFファイルを作成する
    if request.args.get("layout_specified") != "on":
        layout = Layout.optimize_layout(text)
        pdf_writer = PdfWriter.from_layout(layout)
    else:
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
    try:
        workbook = get_workbook(key)
    except Exception:
        return render_template(
            "index.html",
            workbooks=get_workbooks(),
            env = settings.env.value
        ), 421

    # レスポンスを作成する
    response = make_response(workbook)

    # ファイル名を作成
    file_name = quote(key.split("/")[-1])
    response.headers['Content-Disposition'] = f"attachment; filename={file_name}; filename*=UTF-8''{file_name}"
    response.mimetype = 'application/pdf'
    return response


@app.route("/health")
def ping():
    return {"health": "OK"}, 200


@app.errorhandler(Exception)
def internal_server_error(error):
    log.error(error)
    return render_template("error_500.html"), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0")
