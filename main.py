# encoding: utf-8
from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
import os
import numpy as np
import json
from scipy.misc import imresize
from skimage import io
import selectivesearch
import tf_rcnn_classify
import roi


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
        if r['size'] < (SHRINK_SIZE * SHRINK_SIZE / 12):
            continue
        x, y, w, h = r['rect']
        if w / h > 1.2 or h / w > 1.2:
            continue
        candidates.add(r['rect'])
    return candidates


ALLOWED_EXTENSIONS = set(['jpg'])
SHRINK_SIZE = 128
MAX_ROI = 5

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
            uploaded_file = os.path.join(app.config['UPLOAD_DIRECTORY'], 'tmp.jpg')
            f.save(uploaded_file)

            # resize image so that we can process faster
            img = io.imread(uploaded_file)
            height, width, _colors = img.shape
            scale = min(float(SHRINK_SIZE) / width, float(SHRINK_SIZE) / height)
            resized_height = int(height * scale)
            resized_width = int(width * scale)
            resized_img = imresize(img, (resized_height, resized_width), interp='nearest')
            io.imsave(os.path.join(app.config['UPLOAD_DIRECTORY'], 'tmp.s.jpg'), resized_img)

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


@app.route('/rcnn_roi.json')
def rcnn_roi_json():
    # find rois from resized image
    resized_filename = os.path.join(app.config['UPLOAD_DIRECTORY'], 'tmp.s.jpg')
    img = io.imread(resized_filename)
    roi_resized = get_rois(img)
    print 'roi(resized)=', roi_resized

    # select N rois
    roi_resized = roi.select_candidates(list(roi_resized))
    print 'roi(selected)=', roi_resized
    roi_resized = roi_resized[0:MAX_ROI]

    uploaded_file = os.path.join(app.config['UPLOAD_DIRECTORY'], 'tmp.jpg')
    img = io.imread(uploaded_file)
    height, width, _colors = img.shape
    scale = min(float(SHRINK_SIZE) / width, float(SHRINK_SIZE) / height)
    return jsonify({'width': width, 'height': height, 'roi': roi_resized, 'scale': scale})


@app.route('/rcnn_classify.json', methods=['POST'])
def rcnn_classify_json():
    if request.headers['Content-Type'] != 'application/json':
        print(request.headers['Content-Type'])
        return jsonify(error='Invalid Content-Type'), 400

    srcfile = os.path.join(app.config['UPLOAD_DIRECTORY'], 'tmp.s.jpg')
    roi = json.loads(request.data)["roi"]

    # predict in resized image (grey scale image is not supported)
    clf_results = tf_rcnn_classify.classify(srcfile, roi, savedir=UPLOAD_DIRECTORY)
    print 'results=', clf_results

    for result in clf_results:
        # convert numpy.float32 to float
        result['score'] = ('%.2f' % result['score'].item())

    return jsonify({'roi': roi, 'result': clf_results})


@app.route('/')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    if not heroku_env():
        app.debug = True
    app.run()
