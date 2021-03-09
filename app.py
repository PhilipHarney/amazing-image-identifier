from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

import tensorflow as tf
import numpy as np
import os
import wikipedia as wiki

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

model = tf.keras.applications.VGG16()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/cakes')
def cakes():
    return 'Yummy cakes!'

IMAGE_SIZE = 224

def identify_image(image_path):
    image = tf.keras.preprocessing.image.load_img(image_path, target_size=(IMAGE_SIZE, IMAGE_SIZE))
    image = tf.keras.preprocessing.image.img_to_array(image)
    image = np.expand_dims(image, axis=0)
    prediction_result = model.predict(image, batch_size=1)
    best_prediction = tf.keras.applications.imagenet_utils.decode_predictions(prediction_result, top=1)
    return best_prediction[0][0][1]

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image_url = url_for('static', filename='uploads/' + filename)
    identification = identify_image(image_path)
    article = wiki.page(identification)
    return f"""
    <!doctype html>
    <title>{article.title}</title>
    <h1>{article.title}</h1>
    <img src='{image_url}' />
    <p>{article.summary}</p>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')