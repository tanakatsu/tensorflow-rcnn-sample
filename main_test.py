# encoding: utf-8
from flask import Flask, render_template
import os
from skimage import io

app = Flask(__name__)


@app.route('/')
def main():
    srcfile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/lena.jpg')
    img = io.imread(srcfile)
    height, width, _shape = img.shape
    return render_template('test.html', width=width, height=height)


if __name__ == '__main__':
    app.debug = True
    app.run()
