import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = set(['jpeg', 'png', 'jpg', 'JPG', 'PNG', 'JPEG'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if(request.method == "POST"):
        for img in request.files.getlist("files"): # for every img in the list of "files" (from <input name="files"/> 
            filename = secure_filename(img.filename)
            if(allowed_file(filename)):
                print("{} is the filename".format(filename))
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return render_template('upload.html')

@app.route("/images")
def images():
    return render_template('images.html')

@app.route("/image/<filename>")
def get_image(filename):
    full_filename = "../" + os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template("image.html", filename=full_filename)

@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)