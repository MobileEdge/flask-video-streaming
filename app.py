#!/usr/bin/env python
from flask import Flask, render_template, Response

# emulated camera
#from camera import Camera



# Raspberry Pi camera module (requires picamera package)
from camera_pi import Camera

from camera_pi_opencv import Camera_cv

app = Flask(__name__)


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def yeld_decoded(camera_pi):
    while True:
	yield ("[start]" + camera_pi.get_frame() + "[finish]")


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/decoded')
def decode():
    from flask import stream_with_context
    return Response(stream_with_context(yeld_decoded(Camera_cv())))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
