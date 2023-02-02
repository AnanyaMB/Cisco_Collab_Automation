from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/diff')
def diff():
    return render_template('diff.html')

@app.route("/current")
def current():
    return render_template('post.html')

if __name__ == "__main__":
    app.run(host="127.0.0.1",port=8080,debug="True")