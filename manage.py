import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from werkzeug import secure_filename
import subprocess
import signal
import sys
import time

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = os.path.join('static', 'images')
PREDICT_FOLDER = os.path.join('darknet')
PREDICT_VIDEO_FOLDER = os.path.join('darkflow')
ALLOWED_EXTENSIONS = set(['jpeg', 'png', 'jpg', 'JPG', 'PNG', 'JPEG', "MOV", "m4v", "mov", "avi", "AVI", "wmv", "WMV"])
ALLOWED_VIDEO_EXTENSIONS = set(["MOV", "m4v", "mov", "avi", "AVI", "wmv", "WMV"])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PREDICT_FOLDER'] = PREDICT_FOLDER
app.config['PREDICT_VIDEO_FOLDER'] = PREDICT_VIDEO_FOLDER



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
        return render_template('upload.html', success=False, request="GET") # don't display anything
    return render_template('upload.html')

@app.route("/gallery")
def images():
    if(request.args.get("image")):
        #cmd = "./darknet detect cfg/yolov3.cfg yolov3.weights {}".format("../" + app.config['UPLOAD_FOLDER'] + "/" + request.args.get("image")) # image
        cmd = "flow --model cfg/yolo.cfg --load bin/yolo.weights --demo {} --saveVideo".format("../" + app.config['UPLOAD_FOLDER'] + "/" + request.args.get("image")) # video
        # ffmpeg -i video.avi -c:a aac -b:a 128k -c:v libx264 -crf 23 output.mp4 --> convert .avi to .mp4
        remove_video = "rm output.mp4"
        convert_avi_2_mp4 = "ffmpeg -i video.avi -c:a aac -b:a 128k -c:v libx264 -crf 23 output.mp4"
        p = subprocess.Popen(['(cd darkflow/;{};{};{})'.format(remove_video, cmd, convert_avi_2_mp4)], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout = []
        while True:
            line = p.stdout.readline()
            stdout.append(line)
            print(line),
            if line == '' and p.poll() != None:
               #return send_from_directory(app.config['PREDICT_FOLDER'], 'predictions.png')
               return send_from_directory(app.config['PREDICT_VIDEO_FOLDER'], 'output.mp4')

    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("gallery.html", images=images)

@app.route('/image/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)