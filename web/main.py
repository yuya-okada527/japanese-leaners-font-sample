from io import BytesIO

from flask import (
    Flask,
    request,
    render_template,
    make_response
)
from reportlab.pdfgen import canvas


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create")
def create():

    # リクエストパラメータを取得
    message = request.args.get("string")

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
    response.headers['Content-Disposition'] = "attachment; filename='sakulaci.pdf"
    response.mimetype = 'application/pdf'

    return response


if __name__ == "__main__":
    app.run(debug=True)
