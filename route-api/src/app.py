from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/route')
def index():
    return 'hello'

if __name__ == '__main__':
    app.run(debug=True)