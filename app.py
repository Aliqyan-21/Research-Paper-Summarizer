from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
@app.route('/upload')
def upload():
    return render_template("upload.html")

@app.route('/result')
def result():
    return render_template("result.html")
