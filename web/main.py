from flask import (
    Flask,
    render_template,
    make_response
)


app = Flask(__name__)


@app.route("/")
def index():
    name = "Hello World"
    return render_template("index.html", title="index", name=name)


@app.route("/create")
def create():

    # レスポンスの作成
    response = make_response()

    # ファイルコンテンツ
    response.data = "sample contents"

    # ファイル名をセット
    file_name = "sample.txt"
    response.headers["Content-Disposition"] = f"attachment; filename={file_name}"

    return response


if __name__ == "__main__":
    app.run(debug=True)
