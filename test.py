from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/profile/<name>')
def profile(name):
    return render_template('profile.html', name=name)

@app.route('/tuna')
def tuna():
    return '<h1>I am no Tuna</h1>'

if __name__ == "__main__":
    app.run(debug=True)
