from flask import (
    Flask,
    render_template
)


app = Flask(__name__)


@app.route('/')
def index():
    name = "Hello World"
    return render_template("index.html", title="Sample Page", name=name)


if __name__ == "__main__":
    app.run(debug=True)
