from flask import (
    Flask,
    render_template
)


app = Flask(__name__)


@app.route("/")
def index():
    name = "Hello World"
    return render_template("index.html", title="index", name=name)


@app.route("/create")
def create():
    return render_template("index.html", title="create", name="Create")


if __name__ == "__main__":
    app.run(debug=True)
