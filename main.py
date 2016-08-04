# encoding: utf-8
from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
import os
from scipy.misc import imresize
from skimage import io
import selectivesearch
import tf_rcnn_classify


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def heroku_env():
    if 'DYNO' in os.environ:
        return True
    else:
        return False


def get_rois(img):
    img_lbl, regions = selectivesearch.selective_search(img, scale=500, sigma=0.9, min_size=10)
    candidates = set()
    for r in regions:
        if r['rect'] in candidates:
            continue
        if r['size'] < 2000:
            continue
        x, y, w, h = r['rect']
        if w / h > 1.2 or h / w > 1.2:
            continue
        candidates.add(r['rect'])
    return candidates


ALLOWED_EXTENSIONS = set(['jpg'])
SHRINK_SIZE = 256
N_ROI = 3

if heroku_env():
    UPLOAD_DIRECTORY = '/tmp'
else:
    UPLOAD_DIRECTORY = '.'

app = Flask(__name__)
app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY


# http://stackoverflow.com/questions/13768007/browser-caching-issues-in-flask
@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            filename = 'tmp.jpg'
            f.save(os.path.join(app.config['UPLOAD_DIRECTORY'], filename))
            return redirect(url_for('rcnn_result'))
        if f:
            return '''
            <h3>Not supported file</h3>
            '''
        else:
            return '''
            <h3>No file found</h3>
            '''


@app.route('/image')
def uploaded_file():
    return send_from_directory(app.config['UPLOAD_DIRECTORY'], 'tmp.jpg')


@app.route('/rcnn_result')
def rcnn_result():
    return render_template('result.html')


@app.route('/rcnn.json')
def rcnn_json():
    # grey scale image is not supported
    srcfile = os.path.join(app.config['UPLOAD_DIRECTORY'], 'tmp.jpg')
    img = io.imread(srcfile)
    height, width, _shape = img.shape

    # resize image so that we can process faster
    scale = min(float(SHRINK_SIZE) / width, float(SHRINK_SIZE) / height)
    resized_height = int(height * scale)
    resized_width = int(width * scale)
    resized_img = imresize(img, (resized_width, resized_height), interp='nearest')

    # find rois from resized image
    candidates = get_rois(resized_img)

    # predict in resized image
    candidates = list(candidates)[0:N_ROI]
    clf_results = tf_rcnn_classify.classify(srcfile, candidates)

    # recalculate roi
    for result in clf_results:
        result['roi'] = [int(x / scale) for x in result['roi']]
        # convert numpy.foat32 to float
        for res in result['result']:
            res['score'] = ('%.2f' % res['score'].item())

    return jsonify({'width': width, 'height': height, 'result': clf_results})


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
