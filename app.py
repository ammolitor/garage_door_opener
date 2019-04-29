"""
    Raspberry Pi GPIO Status and Control
"""
import time
import RPi.GPIO as GPIO
import flask

app = flask.Flask(__name__)


def push_button():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(7, GPIO.HIGH)
    GPIO.cleanup()


@app.route("/")
@app.route("/index")
def index():
    template_data = {
        'title': 'Garage Door'
    }
    return flask.render_template('index.html', **template_data)


@app.route("/button")
def push_button():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(7, GPIO.OUT)
    GPIO.output(7, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(7, GPIO.HIGH)
    GPIO.cleanup()
    return flask.redirect(flask.url_for('index'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)
