from flask import (
    Flask,
    request,
    render_template,
    make_response
)


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create")
def create():

    # レスポンスの作成
    response = make_response()

    # ファイルコンテンツ
    response.data = request.args.get("string")

    # TODO 動作確認
    print(request.args.get("string"))

    # ファイル名をセット
    file_name = "sample.txt"
    response.headers["Content-Disposition"] = f"attachment; filename={file_name}"

    return response


if __name__ == "__main__":
    app.run(debug=True)
