# -*- coding: utf-8 -*-

from flask import Flask, render_template

app = Flask(__name__,
    static_folder = "./dist/static",
    template_folder = "./dist")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template("index.html")

if __name__=='__main__':
    app.run(host='0.0.0.0',port=80,debug=True)

"""
import requests

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template('index.html')
"""