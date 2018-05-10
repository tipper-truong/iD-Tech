import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, send_file
from werkzeug import secure_filename
import subprocess
import signal
import sys
import time

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def check_video_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_VIDEO_EXTENSIONS

UPLOAD_FOLDER = os.path.join('static', 'images')
PREDICT_FOLDER = os.path.join('static', 'prediction')
ALLOWED_EXTENSIONS = set(['jpeg', 'png', 'jpg', 'JPG', 'PNG', 'JPEG', "MOV", "m4v", "mov", "avi", "AVI", "wmv", "WMV"])
ALLOWED_VIDEO_EXTENSIONS = set(["MOV", "m4v", "mov", "avi", "AVI", "wmv", "WMV"])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PREDICT_FOLDER'] = PREDICT_FOLDER 

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
            else:
                return render_template('upload.html', success=False, request="POST") # wrong image upload
        if(len(request.files.getlist("files")) > 0):
            return render_template('upload.html', success=True, request="POST") # successful image upload
        else:
            return render_template('upload.html', success=False, request="POST")

    else:
        return render_template('upload.html', success=False, request="GET") # don't display anything
    return render_template('upload.html')

@app.route("/gallery", methods=["GET"])
def display_images():
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("gallery.html", images=images)

@app.route("/gallery/image/<filename>", methods=["GET"])
def get_prediction(filename):
    if(filename):
        if(check_video_file(filename)): # it's a video file, run darkflow
            cmd = "flow --model cfg/yolo.cfg --load bin/yolo.weights --demo {} --saveVideo".format("../" + app.config['UPLOAD_FOLDER'] + "/" + filename) # video
            remove_video = "rm output.mp4"
            convert_avi_2_mp4 = "ffmpeg -i video.avi -c:a aac -b:a 128k -c:v libx264 -crf 23 output.mp4"
            copy_video = "cp output.mp4 ../static/prediction"
            p = subprocess.Popen(['(cd darkflow/;{};{};{};{})'.format(remove_video, cmd, convert_avi_2_mp4, copy_video)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout = []
            while True:
                line = p.stdout.readline()
                stdout.append(line)
                print(line),
                if line == '' and p.poll() != None:
                    return render_template("result.html", filename="output.mp4")

        else: # it's a image file, run darknet yolo
            cmd = "./darknet detect cfg/yolov3.cfg yolov3.weights {}".format("../" + app.config['UPLOAD_FOLDER'] + "/" + filename) # image
            copy_file = "cp predictions.png ../static/prediction"
            p = subprocess.Popen(['(cd darknet/;{};{})'.format(cmd, copy_file)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout = []
            while True:
                line = p.stdout.readline()
                stdout.append(line)
                print(line),
                if line == '' and p.poll() != None:
                    return render_template("result.html", filename="predictions.png")

@app.route('/predict/image/<filename>')
def get_file_prediction(filename):
    return send_from_directory(app.config['PREDICT_FOLDER'], filename)

@app.route('/image/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)